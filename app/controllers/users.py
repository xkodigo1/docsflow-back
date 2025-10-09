from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from utils.authz import require_admin
from repositories.user_repo import list_users
from middlewares.auth import get_current_user
from utils.db import get_db_connection

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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Obtener información completa del usuario incluyendo email y departamento
        cursor.execute("""
            SELECT u.id, u.email, u.role, u.department_id, u.is_blocked, u.failed_attempts, 
                   u.created_at, u.updated_at, u.blocked_at, u.unblocked_at,
                   d.name as department_name
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.id = %s
        """, (current_user["id"],))
        
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id": user_data["id"],
            "email": user_data["email"],
            "role": user_data["role"],
            "department_id": user_data["department_id"],
            "department_name": user_data["department_name"],
            "is_blocked": user_data["is_blocked"],
            "failed_attempts": user_data["failed_attempts"],
            "created_at": user_data["created_at"],
            "updated_at": user_data["updated_at"],
            "blocked_at": user_data["blocked_at"],
            "unblocked_at": user_data["unblocked_at"]
        }
    finally:
        cursor.close()
        conn.close()
