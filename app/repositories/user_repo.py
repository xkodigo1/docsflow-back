from utils.db import get_db_connection

def get_user_by_email(email: str):
    conn =get_db_connection
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user=cursor.fetchone()
    conn.close()
    return user


def update_failed_attempts(user_id: int, failed_attempts: int, is_blocked: bool = False, unblocked_at=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET failed_attempts=%s, is_blocked=%s, unblocked_at=%s
        WHERE id=%s
    """, (failed_attempts, is_blocked, unblocked_at, user_id))
    conn.commit()
    conn.close()

def reset_failed_attempts(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET failed_attempts=0, is_blocked=FALSE, blocked_at=NULL, unblocked_at=NULL
        WHERE id=%s
    """, (user_id,))
    conn.commit()
    conn.close()