from typing import Optional, List, Dict, Any
from app.utils.db import get_db_connection


def insert_extracted_table(document_id: int, table_index: int, content_json: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO extracted_tables (document_id, table_index, content) VALUES (%s, %s, %s)",
            (document_id, table_index, content_json)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def list_by_document(document_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, table_index, content, created_at FROM extracted_tables WHERE document_id = %s ORDER BY id",
            (document_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def search(q: str, department_id: Optional[int] = None, limit: int = 20, offset: int = 0):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        params = []
        query = (
            "SELECT et.id AS table_id, et.document_id, et.table_index, et.content, et.created_at, "
            "d.filename AS document_filename, d.department_id AS document_department_id, d.uploaded_at AS document_uploaded_at, d.status AS document_status "
            "FROM extracted_tables et JOIN documents d ON d.id = et.document_id"
        )
        filters = []
        if department_id is not None:
            filters.append("d.department_id = %s")
            params.append(department_id)
        # Búsqueda parcial (case-insensitive según collation de la columna)
        filters.append("JSON_SEARCH(JSON_EXTRACT(et.content, '$'), 'one', %s) IS NOT NULL")
        params.append(f"%{q}%")
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY et.id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def delete_by_document(document_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM extracted_tables WHERE document_id = %s", (document_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

