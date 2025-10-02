from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.middlewares.auth import get_current_user
from app.repositories import table_repo, document_repo
from app.utils.authz import ensure_user_can_access_document
from fastapi.responses import StreamingResponse
import io
import csv
import json

router = APIRouter(prefix="/tables", tags=["tables"])

@router.get("/search", summary="Buscar en tablas extraídas", description="Busca texto dentro del JSON de tablas extraídas (JOIN con documents). Operadores: limitado a su departamento.")

def search_tables(
    q: str = Query(..., description="Texto a buscar"),
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

@router.get("/{document_id}/export", summary="Exportar tablas a CSV", description="Exporta todas las tablas del documento a un CSV plano (una fila por celda).")

def export_tables_csv(document_id: int, current_user=Depends(get_current_user), format: str = Query("csv")):
    if format != "csv":
        raise HTTPException(status_code=400, detail="Formato no soportado")
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    rows = table_repo.list_by_document(document_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["table_index", "row_index", "col_index", "value"])  # header
    for item in rows:
        content = item.get("content")
        try:
            data = content if isinstance(content, dict) else json.loads(content)
        except Exception:
            data = {}
        tables = data.get("tables", []) if isinstance(data, dict) else []
        for t_idx, tbl in enumerate(tables):
            for r_idx, row in enumerate(tbl.get("rows", [])):
                for c_idx, val in enumerate(row):
                    writer.writerow([t_idx, r_idx, c_idx, val])
    output.seek(0)
    filename = f"document_{document_id}_tables.csv"
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
