from fastapi import HTTPException
from app.repositories import user_repo
from app.utils.security import verify_password, create_access_token
from datetime import timedelta
import hashlib

MAX_ATTEMPTS = 5


def login_user(email: str, password: str):
    user = user_repo.get_user_by_email(email)

    if not user:
        # No revelar existencia
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Bloqueo previo si corresponde
    if user["role"] == "operador" and user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="Usuario bloqueado, contacte al admin")

    # Validar password
    if not verify_password(password, user["password_hash"]):
        attempts = (user.get("failed_attempts") or 0) + 1
        will_block = user["role"] == "operador" and attempts >= MAX_ATTEMPTS
        user_repo.update_failed_attempts(user["id"], attempts, will_block)
        msg = "Usuario bloqueado" if will_block else "Credenciales inválidas"
        raise HTTPException(status_code=401, detail=msg)

    # Login exitoso: resetea intentos para operadores
    if user["role"] == "operador":
        user_repo.reset_failed_attempts(user["id"])

    # Emitir token con claims útiles
    payload = {
        "sub": str(user["id"]),
        "role": user["role"],
        "department_id": user["department_id"],
    }
    token = create_access_token(data=payload, expires_delta=timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}
