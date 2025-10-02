from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.schemas.user import UserLogin
from app.config.settings import settings
from datetime import datetime, timedelta
from app.schemas.user import UserCreate, UserOut
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import login_user
from app.utils.security import get_password_hash
from app.utils.db import get_db_connection
from app.utils.authz import require_admin
from app.repositories.password_reset_repo import create_token, get_valid_token, mark_used
from app.utils.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

security = HTTPBearer()

@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión", description="Autenticación con email y contraseña. Devuelve un JWT (30 min). Bloquea operador a 5 intentos fallidos.")

def login(user: UserLogin, request: Request):
    result = login_user(user.email, user.password)
    return TokenResponse(access_token=result["access_token"], expires_in=settings.jwt_expirations_minutes * 60)

@router.post("/refresh", response_model=TokenResponse)

def refresh_token(data: RefreshTokenRequest):
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

def register(user: UserCreate, admin=Depends(require_admin)):
    password_hash = get_password_hash(user.password)
    # Normalizar role por defecto
    role = (user.role or "operador").lower()
    if role not in ("admin", "operador"):
        role = "operador"
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, role, department_id, is_blocked, failed_attempts)
            VALUES (%s, %s, %s, %s, FALSE, 0)
            """,
            (user.email, password_hash, role, user.department_id)
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

@router.post("/forgot-password", summary="Solicitar recuperación de contraseña", description="Genera un token temporal (15 min) y envía un enlace al correo si el email existe.")

def forgot_password(data: ForgotPasswordRequest):
    from app.repositories.user_repo import get_user_by_email
    user = get_user_by_email(data.email)
    # Responder siempre 200
    if not user:
        return {"message": "Si el email existe, se envió un token"}
    token = create_token(user_id=user["id"], exp_minutes=15)
    base = settings.frontend_base_url or "https://your-frontend"
    reset_link = f"{base}/reset-password?token={token}"
    subject = "Recuperación de contraseña - DocsFlow"
    html = f"""
    <p>Hola,</p>
    <p>Recibimos una solicitud para restablecer tu contraseña. Usa el siguiente enlace (válido por 15 minutos):</p>
    <p><a href='{reset_link}'>Restablecer contraseña</a></p>
    <p>Si no solicitaste este cambio, ignora este mensaje.</p>
    """
    # Envío con manejo de errores explícito
    send_email(to_email=user["email"], subject=subject, html_body=html)
    return {"message": "Si el email existe, se envió un token"}

@router.post("/reset-password", summary="Restablecer contraseña", description="Valida el token y actualiza la contraseña del usuario.")

def reset_password(data: ResetPasswordRequest):
    valid = get_valid_token(data.token)
    if not valid:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    from app.repositories.user_repo import get_user_by_email
    from app.utils.db import get_db_connection
    from app.utils.security import get_password_hash
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = get_password_hash(data.new_password)
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, valid["user_id"]))
        mark_used(valid["id"]) 
        conn.commit()
        return {"message": "Contraseña actualizada"}
    finally:
        cursor.close()
        conn.close()