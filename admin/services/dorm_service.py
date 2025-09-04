# admin/services/dorm_service.py
# ตัวอย่าง service แยกลอจิก (เรียกใช้จาก routes ได้ในอนาคต)
from core.db import get_db_connection

def list_pending_dorms():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM dorms WHERE is_approved=2').fetchall()
    conn.close()
    return rows
