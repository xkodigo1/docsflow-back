from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from schemas.user import UserLogin
from utils.db import get_db_connection
from config.settings import settings
import bcrypt
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, request: Request):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    db_user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if db_user["is_blocked"]:
        raise HTTPException(status_code=403, detail="Usuario bloqueado")
    if not bcrypt.checkpw(user.password.encode(), db_user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    # Generar JWT
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expirations_minutes)
    payload = {
        "sub": str(db_user["id"]),
        "role": db_user["role"],
        "exp": expire,
        "department_id": db_user["department_id"]
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return TokenResponse(access_token=token, expires_in=settings.jwt_expirations_minutes * 30)

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
    # Obtener usuario
    cursor.execute("SELECT * FROM users WHERE id = %s", (db_token["user_id"],))
    db_user = cursor.fetchone()
    if not db_user or db_user["is_blocked"]:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Usuario bloqueado o no encontrado")
    # Marcar refresh token como usado (opcional, para un solo uso)
    cursor.execute("UPDATE password_reset_tokens SET used = TRUE WHERE id = %s", (db_token["id"],))
    conn.commit()
    cursor.close()
    conn.close()
    # Generar nuevo access token
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expirations_minutes)
    payload = {
        "sub": str(db_user["id"]),
        "role": db_user["role"],
        "exp": expire,
        "department_id": db_user["department_id"]
    }
    access_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return TokenResponse(access_token=access_token, expires_in=settings.jwt_expirations_minutes * 60)
