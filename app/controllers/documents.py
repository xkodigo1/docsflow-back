from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from typing import Optional
import os
from datetime import datetime
from middlewares.auth import get_current_user
from utils.db import get_db_connection
from services.pdf_processing import extract_pdf_content
import json

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_MIME = {"application/pdf"}
MAX_SIZE_MB = 15

@router.post("/upload")
def upload_document(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"El archivo excede el tamaño máximo de {MAX_SIZE_MB}MB")
    department_id = current_user.get("department_id") if current_user.get("role") == "operador" else current_user.get("department_id")
    if current_user.get("role") == "operador" and not department_id:
        raise HTTPException(status_code=400, detail="Operador sin departamento asignado")
    base_dir = os.path.join("uploads", f"dept_{department_id}" if department_id else "all")
    os.makedirs(base_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = file.filename.replace(" ", "_")
    filepath = os.path.join(base_dir, f"{timestamp}_{safe_name}")
    with open(filepath, "wb") as f:
        f.write(contents)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO documents (filename, uploaded_by, department_id, filepath, status)
            VALUES (%s, %s, %s, %s, 'pending')
            """,
            (file.filename, current_user["id"], department_id if department_id else 0, filepath)
        )
        conn.commit()
        return {"message": "Archivo subido", "document_id": cursor.lastrowid}
    except Exception as e:
        conn.rollback()
        try:
            os.remove(filepath)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Error al guardar documento: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/")
def list_documents(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    department_id: Optional[int] = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if current_user["role"] == "operador":
            department_id = current_user["department_id"]
        params = []
        query = "SELECT * FROM documents"
        filters = []
        if department_id is not None:
            filters.append("department_id = %s")
            params.append(department_id)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY uploaded_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return {"items": rows, "limit": limit, "offset": offset}
    finally:
        cursor.close()
        conn.close()

@router.get("/{document_id}")
def get_document(document_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        if current_user["role"] == "operador":
            if doc["department_id"] != current_user["department_id"]:
                raise HTTPException(status_code=403, detail="No autorizado para ver este documento")
        return doc
    finally:
        cursor.close()
        conn.close()

@router.delete("/{document_id}")
def delete_document(document_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        if current_user["role"] == "operador" and doc["department_id"] != current_user["department_id"]:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este documento")
        filepath = doc["filepath"]
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        conn.commit()
        return {"message": "Documento eliminado"}
    finally:
        cursor.close()
        conn.close()

@router.post("/{document_id}/process")
def process_document(document_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        if current_user["role"] == "operador" and doc["department_id"] != current_user["department_id"]:
            raise HTTPException(status_code=403, detail="No autorizado para procesar este documento")
        # Procesamiento real
        content = extract_pdf_content(doc["filepath"])
        cursor2 = conn.cursor()
        cursor2.execute(
            "INSERT INTO extracted_tables (document_id, table_index, content) VALUES (%s, %s, %s)",
            (document_id, 0, json.dumps(content))
        )
        cursor.execute(
            "UPDATE documents SET status = 'processed', processed_at = NOW() WHERE id = %s",
            (document_id,)
        )
        conn.commit()
        return {"message": "Documento procesado"}
    finally:
        cursor.close()
        conn.close()
