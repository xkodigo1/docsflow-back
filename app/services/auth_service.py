from fastapi import HTTPException
from repositories import user_repo
from utils.security import verify_password, create_access_token

def login_user(email: str, password: str):
    user = user_repo.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user["is_blocked"] and user["role"] == "operador":
        raise HTTPException(status_code=403, detail="Usuario bloqueado, contacte al admin")

    if not verify_password(password, user["password_hash"]):
        attempts = user["failed_attempts"] + 1
        blocked = attempts >= 5 and user["role"] == "operador"
        user_repo.update_failed_attempts(user["id"], attempts, blocked)
        msg = "Usuario bloqueado" if blocked else "Credenciales inválidas"
        raise HTTPException(status_code=401, detail=msg)

    user_repo.reset_attempts(user["id"])
    token = create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer"}
