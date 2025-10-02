from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.utils.authz import require_admin
from app.repositories.user_repo import list_users
from app.middlewares.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")

def get_users(
    admin=Depends(require_admin),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
    role: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None)
):
    effective_role = role if role is not None else "operador"
    rows = list_users(limit=limit, offset=offset, role=effective_role, department_id=department_id)
    return {"items": rows, "limit": limit, "offset": offset, "role": effective_role}

@router.get("/me")

def get_me(current_user=Depends(get_current_user)):
    return current_user
