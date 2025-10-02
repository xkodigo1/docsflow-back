from app.utils.db import get_db_connection


def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()


def get_user_by_id(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()


def update_failed_attempts(user_id: int, failed_attempts: int, is_blocked: bool = False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET failed_attempts = %s,
                is_blocked = %s,
                blocked_at = CASE WHEN %s THEN NOW() ELSE blocked_at END,
                unblocked_at = CASE WHEN %s THEN NULL ELSE unblocked_at END
            WHERE id = %s
            """,
            (failed_attempts, is_blocked, is_blocked, is_blocked, user_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def reset_failed_attempts(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET failed_attempts = 0,
                is_blocked = FALSE,
                blocked_at = NULL,
                unblocked_at = NOW()
            WHERE id = %s
            """,
            (user_id,),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def list_users(limit: int | None = None, offset: int | None = None, role: str | None = None, department_id: int | None = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        filters = []
        params = []
        if role:
            filters.append("role = %s")
            params.append(role)
        if department_id is not None:
            filters.append("department_id = %s")
            params.append(department_id)
        query = "SELECT id, email, role, department_id, is_blocked, failed_attempts, created_at, updated_at FROM users"
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY created_at DESC"
        if limit is not None and offset is not None:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()
