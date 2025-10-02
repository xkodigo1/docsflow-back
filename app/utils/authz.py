from fastapi import HTTPException, Depends
from app.middlewares.auth import get_current_user


def ensure_operator_can_access_document(operator_department_id: int, document_department_id: int) -> None:
    if operator_department_id != document_department_id:
        raise HTTPException(status_code=403, detail="No autorizado")


def ensure_user_can_access_document(user: dict, document: dict) -> None:
    if user.get("role") == "operador":
        ensure_operator_can_access_document(user.get("department_id"), document.get("department_id"))


def require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")
    return current_user


def require_operator(current_user=Depends(get_current_user)):
    if current_user.get("role") != "operador":
        raise HTTPException(status_code=403, detail="Solo operadores")
    return current_user
