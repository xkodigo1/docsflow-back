from app.utils.db import get_db_connection


def exists(department_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM departments WHERE id = %s", (department_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
