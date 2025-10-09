from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from middlewares.auth import get_current_user
from repositories import table_repo, document_repo
from utils.authz import ensure_user_can_access_document
from utils.db import get_db_connection
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
                "uploaded_by": r.get("document_uploaded_by"),
            },
            "table": {
                "id": r["table_id"],
                "index": r["table_index"],
                "created_at": r["created_at"],
                "content": r["content"],
            }
        })
    return {"items": items, "limit": limit, "offset": offset}

@router.get("/my-tables", summary="Mis tablas extraídas", description="Obtiene todas las tablas extraídas de los documentos del usuario actual.")
def get_my_tables(
    q: str = Query("", description="Texto a buscar (opcional)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "operador":
        raise HTTPException(status_code=403, detail="Solo los operadores pueden acceder a sus tablas")
    
    rows = table_repo.get_all_by_user(
        user_id=current_user["id"], 
        q=q, 
        limit=limit, 
        offset=offset
    )
    items = []
    for r in rows:
        items.append({
            "document": {
                "id": r["document_id"],
                "filename": r["document_filename"],
                "department_id": r["document_department_id"],
                "uploaded_at": r["document_uploaded_at"],
                "status": r["document_status"],
                "uploaded_by": r["document_uploaded_by"],
            },
            "table": {
                "id": r["table_id"],
                "index": r["table_index"],
                "created_at": r["created_at"],
                "content": r["content"],
            }
        })
    return {"items": items, "limit": limit, "offset": offset}

@router.get("/my-tables/download", summary="Descargar mis tablas en JSON", description="Descarga todas las tablas del usuario en formato JSON.")
def download_my_tables(
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "operador":
        raise HTTPException(status_code=403, detail="Solo los operadores pueden descargar sus tablas")
    
    rows = table_repo.get_all_by_user(user_id=current_user["id"], limit=1000)
    
    # Organizar por documento
    documents_data = {}
    for r in rows:
        doc_id = r["document_id"]
        if doc_id not in documents_data:
            documents_data[doc_id] = {
                "document": {
                    "id": r["document_id"],
                    "filename": r["document_filename"],
                    "department_id": r["document_department_id"],
                    "uploaded_at": r["document_uploaded_at"],
                    "status": r["document_status"],
                    "uploaded_by": r["document_uploaded_by"],
                },
                "tables": []
            }
        
        documents_data[doc_id]["tables"].append({
            "id": r["table_id"],
            "index": r["table_index"],
            "created_at": r["created_at"],
            "content": r["content"]
        })
    
    # Convertir a lista
    result = list(documents_data.values())
    
    # Crear respuesta JSON
    json_content = json.dumps(result, indent=2, ensure_ascii=False)
    
    return StreamingResponse(
        io.BytesIO(json_content.encode('utf-8')),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=mis_tablas_{current_user['id']}.json"}
    )

@router.get("/table/{table_id}", summary="Obtener tabla específica", description="Obtiene los datos de una tabla específica por su ID.")
def get_table_by_id(table_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT et.id, et.document_id, et.table_index, et.content, et.created_at,
                   d.filename, d.status, d.uploaded_by
            FROM extracted_tables et 
            JOIN documents d ON d.id = et.document_id 
            WHERE et.id = %s
        """, (table_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Tabla no encontrada")
        
        # Verificar que el usuario puede acceder a esta tabla
        if current_user["role"] == "operador" and result["uploaded_by"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para acceder a esta tabla")
        
        return {
            "id": result["id"],
            "document_id": result["document_id"],
            "table_index": result["table_index"],
            "content": result["content"],
            "created_at": result["created_at"],
            "document": {
                "filename": result["filename"],
                "status": result["status"],
                "uploaded_by": result["uploaded_by"]
            }
        }
    finally:
        cursor.close()
        conn.close()

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
