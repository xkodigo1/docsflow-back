from typing import Optional, Tuple
from app.utils.db import get_db_connection
from app.utils.query import build_where


def insert_document(filename: str, uploaded_by: int, department_id: int, filepath: str, document_type: Optional[str] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO documents (filename, uploaded_by, department_id, filepath, document_type, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            """,
            (filename, uploaded_by, department_id, filepath, document_type)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_document(document_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def list_documents(limit: int, offset: int, department_id: Optional[int] = None, document_type: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        filters = []
        params = []
        if department_id is not None:
            filters.append("department_id = %s")
            params.append(department_id)
        if document_type:
            filters.append("document_type = %s")
            params.append(document_type)
        query = "SELECT * FROM documents" + build_where(filters) + " ORDER BY uploaded_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def search_documents(q: Optional[str], department_id: Optional[int], limit: int, offset: int, document_type: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        filters = []
        params = []
        if department_id is not None:
            filters.append("department_id = %s")
            params.append(department_id)
        if document_type:
            filters.append("document_type = %s")
            params.append(document_type)
        if q:
            filters.append("filename LIKE %s")
            params.append(f"%{q}%")
        query = "SELECT * FROM documents" + build_where(filters) + " ORDER BY uploaded_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def delete_document(document_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def mark_processed(document_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE documents SET status = 'processed', processed_at = NOW() WHERE id = %s", (document_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

