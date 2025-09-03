from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from .routes import get_db_connection # Import ฟังก์ชันเชื่อมต่อ DB
import json

owner_bp = Blueprint('owner', __name__, url_prefix='/owner')

@owner_bp.route('/')
def home():
    if 'username' not in session or session.get('user_type') != 'owner':
        # ถ้าไม่ใช่ owner ให้ redirect ไปหน้า login หลัก
        return redirect(url_for('main.login'))

    user_id = session.get('user_id')
    username = session.get('username')
    conn = get_db_connection()
    dorms = conn.execute('SELECT * FROM dorms WHERE owner_id = ?', (user_id,)).fetchall()
    conn.close()
    
    # อย่าลืมใส่ prefix 'owner/' สำหรับ template
    return render_template('owner/owner_dashboard.html', username=username, dorms=dorms)

# --- ย้าย Route อื่นๆ ของ Owner มาไว้ที่นี่ ---
# ตัวอย่าง: /add_dorm
@owner_bp.route('/add_dorm', methods=['GET', 'POST'])
def add_dorm():
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        # ... (โค้ดเหมือนเดิม) ...
        return redirect(url_for('owner.home'))
        
    return render_template('owner/add_dorm.html')

# ... (ย้าย Route อื่นๆ ของ Owner เช่น dorm_details, add_room, approve_dorm มาที่นี่)
# ... และเปลี่ยน url_for ทั้งหมดให้มี prefix 'owner.' เช่น url_for('owner.dorm_details', ...)