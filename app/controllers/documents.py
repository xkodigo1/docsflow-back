from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Form
from typing import Optional
import os
from datetime import datetime
from middlewares.auth import get_current_user
from repositories import document_repo, table_repo, department_repo
import json
from utils.db import get_db_connection
from utils.files import build_upload_path, write_bytes
from utils.authz import ensure_user_can_access_document
from fastapi.responses import FileResponse

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_MIME = {"application/pdf"}
MAX_SIZE_MB = 15

@router.post("/upload", summary="Subir PDF", description="Valida PDF, guarda en disco por departamento, inserta metadata y deja el documento en estado 'pending'.")

def upload_document(
    file: UploadFile = File(..., description="Archivo PDF a subir"),
    current_user=Depends(get_current_user),
    department_id: Optional[int] = Form(None, description="Obligatorio para admin; operadores usan su propio departamento"),
    document_type: Optional[str] = Form(None, description="Tipo de documento para filtros (ej. 'factura', 'reporte')")
):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"El archivo excede el tamaño máximo de {MAX_SIZE_MB}MB")

    if current_user.get("role") == "operador":
        effective_department_id = current_user.get("department_id")
        if not effective_department_id:
            raise HTTPException(status_code=400, detail="Operador sin departamento asignado")
    else:
        if not department_id:
            raise HTTPException(status_code=400, detail="Debe indicar department_id para subir documentos")
        effective_department_id = department_id

    if not department_repo.exists(int(effective_department_id)):
        raise HTTPException(status_code=400, detail="El department_id indicado no existe")

    filepath = build_upload_path(int(effective_department_id), file.filename)
    write_bytes(filepath, contents)

    doc_id = document_repo.insert_document(file.filename, current_user["id"], int(effective_department_id), filepath, document_type=document_type)
    return {"message": "Archivo subido", "document_id": doc_id}

@router.get("/")
def list_documents(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    department_id: Optional[int] = None,
    document_type: Optional[str] = None
):
    if current_user["role"] == "operador":
        department_id = current_user["department_id"]
    rows = document_repo.list_documents(limit=limit, offset=offset, department_id=department_id, document_type=document_type)
    return {"items": rows, "limit": limit, "offset": offset}

@router.get("/{document_id}")

def get_document(document_id: int, current_user=Depends(get_current_user)):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    return doc

@router.delete("/{document_id}")

def delete_document(document_id: int, current_user=Depends(get_current_user)):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    filepath = doc["filepath"]
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass
    document_repo.delete_document(document_id)
    return {"message": "Documento eliminado"}

@router.post("/{document_id}/process")

def process_document(document_id: int, current_user=Depends(get_current_user)):
    from services.pdf_processing import extract_pdf_content
    from utils.db import get_db_connection
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    # Marcar processing y timestamp intento
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE documents SET status='processing', last_attempt_at = NOW(), error_message = NULL WHERE id = %s", (document_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()
    # Ejecutar extracción
    try:
        content = extract_pdf_content(doc["filepath"])
        
        # Guardar cada tabla individualmente
        if content.get("tables") and len(content["tables"]) > 0:
            for table_index, table_data in enumerate(content["tables"]):
                table_repo.insert_extracted_table(document_id, table_index, json.dumps(table_data))
        else:
            # Si no hay tablas, guardar el contenido completo como antes
            table_repo.insert_extracted_table(document_id, 0, json.dumps(content))
        
        document_repo.mark_processed(document_id)
        return {"message": f"Documento procesado. {len(content.get('tables', []))} tablas extraídas"}
    except Exception as e:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE documents SET status='error', error_message=%s WHERE id=%s", (str(e)[:500], document_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()
        raise HTTPException(status_code=500, detail="Error procesando el documento")

@router.post("/{document_id}/reprocess")

def reprocess_document(document_id: int, current_user=Depends(get_current_user)):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    # Limpiar tablas extraídas y marcar pending
    table_repo.delete_by_document(document_id)
    from utils.db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE documents SET status = 'pending', processed_at = NULL WHERE id = %s", (document_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()
    return {"message": "Documento marcado para reprocesar"}

@router.get("/search")

def search_documents(
    q: Optional[str] = Query(None, description="Texto a buscar en el nombre del archivo"),
    department_id: Optional[int] = Query(None, description="Filtrar por departamento"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
):
    if current_user["role"] == "operador":
        department_id = current_user["department_id"]
    rows = document_repo.search_documents(q=q, department_id=department_id, limit=limit, offset=offset, document_type=document_type)
    return {"items": rows, "limit": limit, "offset": offset, "total": len(rows)}

@router.get("/{document_id}/download")

def download_document(document_id: int, current_user=Depends(get_current_user)):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    if not doc.get("filepath") or not os.path.exists(doc["filepath"]):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    filename = doc.get("filename") or os.path.basename(doc["filepath"])
    return FileResponse(path=doc["filepath"], media_type="application/pdf", filename=filename)

@router.get("/{document_id}/status", summary="Estado de procesamiento", description="Devuelve estado actual, último intento y error si lo hay.")

def get_document_status(document_id: int, current_user=Depends(get_current_user)):
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    return {
        "id": doc["id"],
        "status": doc.get("status"),
        "processed_at": doc.get("processed_at"),
        "last_attempt_at": doc.get("last_attempt_at"),
        "error_message": doc.get("error_message"),
    }