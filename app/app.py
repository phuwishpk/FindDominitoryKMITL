from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db_connection():
    # ../ เพื่อให้ path วิ่งไปยัง parent directory
    db_path = os.path.join(os.path.dirname(__file__), '..', 'dorm_management.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ? AND user_type = ?', 
                            (username, password, 'admin')).fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin username or password"
            
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    pending_dorms = conn.execute('SELECT * FROM dorms WHERE is_approved = 2').fetchall()
    conn.close()

    return render_template('admin_dashboard.html', pending_dorms=pending_dorms)

@app.route('/admin/dorm/<int:dorm_id>')
def admin_dorm_details(dorm_id):
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ?', (dorm_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id = ?', (dorm_id,)).fetchall()
    conn.close()

    if dorm is None:
        return "Dorm not found", 404
        
    return render_template('admin_dorm_details.html', dorm=dorm, rooms=rooms)

@app.route('/admin/approve/<int:dorm_id>', methods=['POST'])
def admin_approve_dorm(dorm_id):
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('UPDATE dorms SET is_approved = 1, rejection_reason = NULL WHERE id = ?', (dorm_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:dorm_id>', methods=['POST'])
def admin_reject_dorm(dorm_id):
    if 'username' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))

    rejection_reason = request.form.get('rejection_reason', 'ไม่มีเหตุผล')
    
    conn = get_db_connection()
    conn.execute('UPDATE dorms SET is_approved = 0, rejection_reason = ? WHERE id = ?', (rejection_reason, dorm_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001) # ใช้คนละ port กับ Owner