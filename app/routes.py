from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import os

main_bp = Blueprint('main', __name__)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'dorm_management.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']

            # --- Logic การ Redirect ตามที่ต้องการ ---
            if user['user_type'] == 'admin':
                # ถ้าเป็น admin ให้ไปหน้า owner
                return redirect(url_for('owner.home')) 
            elif user['user_type'] == 'owner':
                # ถ้าเป็น owner ให้ไปหน้า admin
                return redirect(url_for('admin.admin_dashboard'))
        else:
            return "Invalid username or password"
            
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # ในระบบจริงควรมีการตรวจสอบ username ซ้ำ และเข้ารหัสรหัสผ่าน
        
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)",
                     (username, password, 'owner')) # สมัครเป็น owner เท่านั้น
        conn.commit()
        conn.close()
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))