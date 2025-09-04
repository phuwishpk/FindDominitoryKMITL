# admin/routes.py
from flask import render_template, request, redirect, url_for, session
from . import admin_bp
from core.db import get_db_connection, init_db

# กันเผื่อ DB ถูกลบ
init_db()

def require_admin():
    return session.get('user_type') == 'admin'

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=? AND user_type='admin'",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session.clear()
            session['username']  = user['username']
            session['user_id']   = user['id']
            session['user_type'] = user['user_type']
            return redirect(url_for('admin.dashboard'))
        return render_template('admin/login.html', error='Invalid admin username or password')
    return render_template('admin/login.html')

@admin_bp.route('/admin')
def dashboard():
    if not require_admin():
        return redirect(url_for('admin.login'))

    conn = get_db_connection()
    pending = conn.execute('''
        SELECT d.*, u.username AS owner_name
        FROM dorms d
        JOIN users u ON u.id = d.owner_id
        WHERE d.is_approved = 2
    ''').fetchall()
    conn.close()
    return render_template('admin/dashboard.html', pending_dorms=pending)

@admin_bp.route('/admin/dorm/<int:dorm_id>')
def dorm_details(dorm_id):
    if not require_admin():
        return redirect(url_for('admin.login'))

    conn = get_db_connection()
    dorm  = conn.execute('SELECT * FROM dorms WHERE id = ?', (dorm_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id = ?', (dorm_id,)).fetchall()
    conn.close()

    if dorm is None:
        return "Dorm not found", 404
    return render_template('admin/dorm_details.html', dorm=dorm, rooms=rooms)

@admin_bp.route('/admin/approve/<int:dorm_id>', methods=['POST'])
def approve_dorm(dorm_id):
    if not require_admin():
        return redirect(url_for('admin.login'))
    conn = get_db_connection()
    conn.execute('UPDATE dorms SET is_approved=1, rejection_reason=NULL WHERE id=?', (dorm_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/reject/<int:dorm_id>', methods=['POST'])
def reject_dorm(dorm_id):
    if not require_admin():
        return redirect(url_for('admin.login'))
    reason = request.form.get('rejection_reason', 'ไม่มีเหตุผล')
    conn = get_db_connection()
    conn.execute('UPDATE dorms SET is_approved=0, rejection_reason=? WHERE id=?', (reason, dorm_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))
