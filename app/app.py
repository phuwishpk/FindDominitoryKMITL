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
    from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_owner'

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db_connection():
    # ../ เพื่อให้ path วิ่งไปยัง parent directory
    db_path = os.path.join(os.path.dirname(__file__), '..', 'dorm_management.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# (ใส่ฟังก์ชัน init_db() ไว้ที่นี่ หากต้องการให้ Owner app สร้าง DB ได้เองในครั้งแรก)
def init_db():
    conn = get_db_connection()
    # Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    ''')
    # Dorms Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS dorms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            water_fee REAL,
            electricity_fee REAL,
            deposit REAL,
            contact_line TEXT,
            contact_phone TEXT,
            location_lat REAL,
            location_long REAL,
            is_approved INTEGER DEFAULT 0,
            rejection_reason TEXT,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    # Rooms Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dorm_id INTEGER NOT NULL,
            room_type TEXT NOT NULL,
            price REAL,
            room_count INTEGER,
            images TEXT,
            FOREIGN KEY (dorm_id) REFERENCES dorms (id)
        )
    ''')
    
    # Add sample users if not exists
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username IN ('owner', 'admin')")
    users = cursor.fetchall()
    if len(users) < 2:
        conn.execute("INSERT OR IGNORE INTO users (username, password, user_type) VALUES (?, ?, ?)", ('owner', 'owner', 'owner'))
        conn.execute("INSERT OR IGNORE INTO users (username, password, user_type) VALUES (?, ?, ?)", ('admin', 'admin', 'admin'))
    
    conn.commit()
    conn.close()
    
db_path = os.path.join(os.path.dirname(__file__), '..', 'dorm_management.db')
if not os.path.exists(db_path):
    init_db()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ? AND user_type = ?', 
                            (username, password, 'owner')).fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            return redirect(url_for('home'))
        else:
            return "Invalid owner username or password"
            
    return render_template('login.html')

@app.route('/')
def home():
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    username = session.get('username')
    conn = get_db_connection()
    dorms = conn.execute('SELECT * FROM dorms WHERE owner_id = ?', (user_id,)).fetchall()
    conn.close()
    
    return render_template('owner_dashboard.html', username=username, dorms=dorms)

@app.route('/add_dorm', methods=['GET', 'POST'])
def add_dorm():
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        # ... (โค้ดส่วน add_dorm เหมือนเดิม) ...
        name = request.form['dorm_name']
        try:
            water_fee = float(request.form['water_fee'])
            electricity_fee = float(request.form['electricity_fee'])
            deposit = float(request.form['deposit'])
            location_lat = float(request.form['location_lat'])
            location_long = float(request.form['location_long'])
        except (ValueError, KeyError):
            return "Invalid data format for numeric fields.", 400

        contact_line = request.form['contact_line']
        contact_phone = request.form['contact_phone']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO dorms (owner_id, name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (session.get('user_id'), name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
        
    return render_template('add_dorm.html')
    
@app.route('/dorm/<int:dorm_id>')
def dorm_details(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))
    
    # ... (โค้ดส่วน dorm_details เหมือนเดิม) ...
    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ?', (dorm_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id = ?', (dorm_id,)).fetchall()
    conn.close()
    
    if dorm is None:
        return "Dorm not found", 404
        
    return render_template('dorm_details.html', dorm=dorm, rooms=rooms)


@app.route('/add_room/<int:dorm_id>', methods=['POST'])
def add_room(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))
    
    # ... (โค้ดส่วน add_room เหมือนเดิม) ...
    room_type = request.form['room_type']
    try:
        price = float(request.form['price'])
        room_count = int(request.form['room_count'])
    except (ValueError, KeyError):
        return "Invalid data format for numeric fields.", 400

    images = request.form.getlist('images')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO rooms (dorm_id, room_type, price, room_count, images) VALUES (?, ?, ?, ?, ?)',
                 (dorm_id, room_type, price, room_count, json.dumps(images)))
    conn.commit()
    conn.close()
    
    return redirect(url_for('dorm_details', dorm_id=dorm_id))

@app.route('/edit_dorm/<int:dorm_id>', methods=['GET', 'POST'])
def edit_dorm(dorm_id):
    # Placeholder
    return f"This is the page to edit dorm with ID: {dorm_id}"

@app.route('/delete_dorm/<int:dorm_id>', methods=['POST'])
def delete_dorm(dorm_id):
    # Placeholder
    return f"This is the endpoint to delete dorm with ID: {dorm_id}"

@app.route('/approve_dorm/<int:dorm_id>', methods=['POST'])
def approve_dorm(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('UPDATE dorms SET is_approved = 2 WHERE id = ?', (dorm_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('dorm_details', dorm_id=dorm_id))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)