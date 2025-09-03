from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # ตั้งค่า secret key สำหรับ session

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db_connection():
    conn = sqlite3.connect('dorm_management.db')
    conn.row_factory = sqlite3.Row
    return conn

# สร้างตารางในฐานข้อมูล (รันครั้งแรกเท่านั้น)
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    ''')
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
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
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
    conn.close()

# เรียกใช้ฟังก์ชันสร้างตาราง
init_db()

# --- หน้าหลักของเจ้าของหอ ---
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

# --- หน้าล็อกอิน (ตัวอย่าง) ---
@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('home'))
        else:
            return "Invalid username or password"
            
    return render_template('login.html')

# --- หน้าเพิ่มหอพัก ---
@app.route('/add_dorm', methods=['GET', 'POST'])
def add_dorm():
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['dorm_name']
        water_fee = request.form['water_fee']
        electricity_fee = request.form['electricity_fee']
        deposit = request.form['deposit']
        contact_line = request.form['contact_line']
        contact_phone = request.form['contact_phone']
        location_lat = request.form['location_lat']
        location_long = request.form['location_long']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO dorms (owner_id, name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (session.get('user_id'), name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
        
    return render_template('add_dorm.html')
    
# --- หน้ารายละเอียดหอ, แก้ไข, ลบ ---
@app.route('/dorm/<int:dorm_id>')
def dorm_details(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ?', (dorm_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id = ?', (dorm_id,)).fetchall()
    conn.close()
    
    if dorm is None:
        return "Dorm not found", 404
        
    return render_template('dorm_details.html', dorm=dorm, rooms=rooms)

@app.route('/edit_dorm/<int:dorm_id>', methods=['GET', 'POST'])
def edit_dorm(dorm_id):
    # โค้ดสำหรับแก้ไขข้อมูลหอพัก
    return "Edit Dorm Page"

@app.route('/delete_dorm/<int:dorm_id>', methods=['POST'])
def delete_dorm(dorm_id):
    # โค้ดสำหรับลบหอพัก
    return "Delete Dorm Endpoint"

# --- เพิ่มห้องพัก ---
@app.route('/add_room/<int:dorm_id>', methods=['POST'])
def add_room(dorm_id):
    room_type = request.form['room_type']
    price = request.form['price']
    room_count = request.form['room_count']
    images = request.form.getlist('images')  # สมมติว่ารับรูปภาพเป็น URL หรือ base64
    
    conn = get_db_connection()
    conn.execute('INSERT INTO rooms (dorm_id, room_type, price, room_count, images) VALUES (?, ?, ?, ?, ?)',
                 (dorm_id, room_type, price, room_count, json.dumps(images)))
    conn.commit()
    conn.close()
    
    return redirect(url_for('dorm_details', dorm_id=dorm_id))

# --- ส่งข้อมูลไปให้ Admin (จำลอง API) ---
@app.route('/approve_dorm/<int:dorm_id>', methods=['POST'])
def approve_dorm(dorm_id):
    # จำลองการส่งข้อมูล API ไปยังฝั่ง Admin
    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ?', (dorm_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id = ?', (dorm_id,)).fetchall()
    conn.close()
    
    if dorm is None:
        return jsonify({"status": "error", "message": "Dorm not found"}), 404

    # สร้าง payload สำหรับส่งไป API ของ Admin
    payload = {
        "dorm_info": dict(dorm),
        "room_info": [dict(room) for room in rooms]
    }
    
    # ณ จุดนี้ จะต้องมีการส่งข้อมูล payload ไปยัง API ของ Admin จริงๆ
    # เช่น requests.post('http://admin_api_endpoint/approve', json=payload)
    print("Sending data to Admin API for approval:", payload)
    
    # อัปเดตสถานะในฐานข้อมูลเป็น "รอการอนุมัติ" (สมมติว่า is_approved = 2)
    conn = get_db_connection()
    conn.execute('UPDATE dorms SET is_approved = 2 WHERE id = ?', (dorm_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Dorm submitted for approval"})


if __name__ == '__main__':
    # เพิ่ม user ตัวอย่างสำหรับทดสอบ
    conn = get_db_connection()
    conn.execute("INSERT OR IGNORE INTO users (id, username, password, user_type) VALUES (?, ?, ?, ?)", (1, 'owner1', 'password123', 'owner'))
    conn.commit()
    conn.close()
    app.run(debug=True)