from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from middlewares.auth import get_current_user
from repositories import table_repo, document_repo
from utils.authz import ensure_user_can_access_document

router = APIRouter(prefix="/tables", tags=["tables"])

@router.get("/search")

def search_tables(
    q: str = Query(..., description="Texto a buscar en el JSON de tablas"),
    department_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    if current_user["role"] == "operador":
        department_id = current_user["department_id"]
    rows = table_repo.search(q=q, department_id=department_id, limit=limit, offset=offset)
    items = []
    for r in rows:
        items.append({
            "document": {
                "id": r["document_id"],
                "filename": r["document_filename"],
                "department_id": r["document_department_id"],
                "uploaded_at": r["document_uploaded_at"],
                "status": r["document_status"],
            },
            "table": {
                "id": r["table_id"],
                "index": r["table_index"],
                "created_at": r["created_at"],
                "content": r["content"],
            }
        })
    return {"items": items, "limit": limit, "offset": offset}

@router.get("/{document_id}")

def list_tables_by_document(document_id: int, current_user=Depends(get_current_user)):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    rows = table_repo.list_by_document(document_id)
    return {"items": rows}
