from fastapi import APIRouter, HTTPException, status, Request
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
