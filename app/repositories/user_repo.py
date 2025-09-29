from utils.db import get_db_connection


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
