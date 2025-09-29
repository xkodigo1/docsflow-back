from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from schemas.user import UserLogin
from config.settings import settings
from datetime import datetime, timedelta
from schemas.user import UserCreate, UserOut
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import login_user

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Solo el admin puede registrar usuarios")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, request: Request):
    result = login_user(user.email, user.password)
    # La expiración está manejada por create_access_token; exponemos segundos estándar
    return TokenResponse(access_token=result["access_token"], expires_in=settings.jwt_expirations_minutes * 60)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest):
    from utils.db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM password_reset_tokens WHERE token = %s AND used = FALSE AND expires_at > NOW()", (data.refresh_token,))
    db_token = cursor.fetchone()
    if not db_token:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
    cursor.execute("SELECT * FROM users WHERE id = %s", (db_token["user_id"],))
    db_user = cursor.fetchone()
    if not db_user or db_user["is_blocked"]:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Usuario bloqueado o no encontrado")
    cursor.execute("UPDATE password_reset_tokens SET used = TRUE WHERE id = %s", (db_token["id"],))
    conn.commit()
    cursor.close()
    conn.close()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expirations_minutes)
    payload = {
        "sub": str(db_user["id"]),
        "role": db_user["role"],
        "exp": expire,
        "department_id": db_user["department_id"]
    }
    access_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return TokenResponse(access_token=access_token, expires_in=settings.jwt_expirations_minutes * 60)

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, admin=Depends(get_current_admin)):
    import bcrypt
    from utils.db import get_db_connection
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, role, department_id, is_blocked, failed_attempts)
            VALUES (%s, %s, %s, %s, FALSE, 0)
            """,
            (user.email, password_hash, user.role, user.department_id)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        db_user = cursor.fetchone()
        return UserOut(
            id=db_user["id"],
            email=db_user["email"],
            role=db_user["role"],
            department_id=db_user["department_id"],
            is_blocked=db_user["is_blocked"],
            failed_attempts=db_user["failed_attempts"],
            created_at=db_user["created_at"],
            updated_at=db_user["updated_at"],
            blocked_at=db_user["blocked_at"],
            unblocked_at=db_user["unblocked_at"]
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al registrar usuario: {str(e)}")
    finally:
        cursor.close()
        conn.close()
