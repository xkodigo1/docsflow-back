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

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_MIME = {"application/pdf"}
MAX_SIZE_MB = 15

@router.post("/upload")

def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    department_id: Optional[int] = Form(None)
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

    doc_id = document_repo.insert_document(file.filename, current_user["id"], int(effective_department_id), filepath)
    return {"message": "Archivo subido", "document_id": doc_id}

@router.get("/")
def list_documents(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    department_id: Optional[int] = None
):
    if current_user["role"] == "operador":
        department_id = current_user["department_id"]
    rows = document_repo.list_documents(limit=limit, offset=offset, department_id=department_id)
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
    doc = document_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    ensure_user_can_access_document(current_user, doc)
    content = extract_pdf_content(doc["filepath"])
    table_repo.insert_extracted_table(document_id, 0, json.dumps(content))
    document_repo.mark_processed(document_id)
    return {"message": "Documento procesado"}

@router.get("/search")

def search_documents(
    q: Optional[str] = Query(None, description="Texto a buscar en el nombre del archivo"),
    department_id: Optional[int] = Query(None, description="Filtrar por departamento"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
):
    if current_user["role"] == "operador":
        department_id = current_user["department_id"]
    rows = document_repo.search_documents(q=q, department_id=department_id, limit=limit, offset=offset)
    return {"items": rows, "limit": limit, "offset": offset, "total": len(rows)}