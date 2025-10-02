from datetime import datetime, timedelta
import secrets
from app.utils.db import get_db_connection

DEFAULT_EXP_MINUTES = 15


def create_token(user_id: int, exp_minutes: int = DEFAULT_EXP_MINUTES) -> str:
    token = secrets.token_urlsafe(32)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO password_reset_tokens (user_id, token, expires_at, used) VALUES (%s, %s, %s, FALSE)",
            (user_id, token, datetime.utcnow() + timedelta(minutes=exp_minutes))
        )
        conn.commit()
        return token
    finally:
        cursor.close()
        conn.close()


def get_valid_token(token: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM password_reset_tokens WHERE token = %s AND used = FALSE AND expires_at > NOW()",
            (token,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def mark_used(token_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE password_reset_tokens SET used = TRUE WHERE id = %s", (token_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
