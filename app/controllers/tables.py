from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from middlewares.auth import get_current_user
from utils.db import get_db_connection

router = APIRouter(prefix="/tables", tags=["tables"])

@router.get("/search")
def search_tables(
    q: str = Query(..., description="Texto a buscar en el JSON de tablas"),
    department_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if current_user["role"] == "operador":
            department_id = current_user["department_id"]
        filters = []
        params = []
        query = """
            SELECT et.id, et.document_id, et.table_index, et.content, et.created_at
            FROM extracted_tables et
            JOIN documents d ON d.id = et.document_id
        """
        if department_id is not None:
            filters.append("d.department_id = %s")
            params.append(department_id)
        filters.append("JSON_SEARCH(JSON_EXTRACT(et.content, '$'), 'one', %s) IS NOT NULL")
        params.append(q)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY et.id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return {"items": rows, "limit": limit, "offset": offset}
    finally:
        cursor.close()
        conn.close()

@router.get("/{document_id}")
def list_tables_by_document(document_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT department_id FROM documents WHERE id = %s", (document_id,))
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        if current_user["role"] == "operador" and doc["department_id"] != current_user["department_id"]:
            raise HTTPException(status_code=403, detail="No autorizado")
        cursor.execute("SELECT id, table_index, content, created_at FROM extracted_tables WHERE document_id = %s ORDER BY id", (document_id,))
        rows = cursor.fetchall()
        return {"items": rows}
    finally:
        cursor.close()
        conn.close()
