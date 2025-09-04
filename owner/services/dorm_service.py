# owner/services/dorm_service.py
from core.db import get_db_connection

def list_my_dorms(owner_id: int):
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM dorms WHERE owner_id=?', (owner_id,)).fetchall()
    conn.close()
    return rows
