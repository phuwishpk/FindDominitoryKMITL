from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import json
import os

# Create a custom filter function
def from_json_filter(value):
    """
    Custom filter to parse a JSON string into a Python object.
    """
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {} # Return an empty dictionary on error to prevent crashing

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

# Register the custom filter
app.add_template_filter(from_json_filter, 'from_json')

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db_connection():
    conn = sqlite3.connect('dorm_management.db')
    conn.row_factory = sqlite3.Row
    return conn

# สร้างตารางในฐานข้อมูลและเพิ่มผู้ใช้ตัวอย่าง
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
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
    
    conn.execute("DELETE FROM users WHERE username='admin'")
    conn.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", ('admin', 'admin', 'owner'))
    conn.commit()
    conn.close()

if not os.path.exists('dorm_management.db'):
    init_db()

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
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
            
    return render_template('login.html')

@app.route('/add_dorm', methods=['GET', 'POST'])
def add_dorm():
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['dorm_name']
        try:
            water_fee = float(request.form['water_fee'])
            electricity_fee = float(request.form['electricity_fee'])
            deposit = float(request.form['deposit'])
            location_lat = float(request.form['location_lat'])
            location_long = float(request.form['location_long'])
        except (ValueError, KeyError):
            flash("ข้อมูลตัวเลขไม่ถูกต้อง", 'error')
            return redirect(url_for('add_dorm'))

        contact_line = request.form['contact_line']
        contact_phone = request.form['contact_phone']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO dorms (owner_id, name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (session.get('user_id'), name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long))
            conn.commit()
            flash('เพิ่มหอพักสำเร็จแล้ว!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'เกิดข้อผิดพลาดในการเพิ่มหอพัก: {e}', 'error')
        finally:
            conn.close()
            
        return redirect(url_for('home'))
    
    return render_template('add_dorm.html')
    
@app.route('/dorm/<int:dorm_id>')
def dorm_details(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ? AND owner_id = ?', (dorm_id, session.get('user_id'))).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id = ?', (dorm_id,)).fetchall()
    conn.close()
    
    if dorm is None:
        flash("ไม่พบหอพัก หรือคุณไม่มีสิทธิ์เข้าถึงหน้านี้", 'error')
        return redirect(url_for('home'))
        
    return render_template('dorm_details.html', dorm=dorm, rooms=rooms)

@app.route('/add_room/<int:dorm_id>', methods=['POST'])
def add_room(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ? AND owner_id = ?', (dorm_id, session.get('user_id'))).fetchone()
    
    if dorm is None:
        flash("ไม่พบหอพัก หรือคุณไม่มีสิทธิ์เพิ่มห้องพัก", 'error')
        conn.close()
        return redirect(url_for('home'))

    room_type = request.form['room_type']
    try:
        price = float(request.form['price'])
        room_count = int(request.form['room_count'])
    except (ValueError, KeyError):
        flash("ข้อมูลตัวเลขสำหรับห้องพักไม่ถูกต้อง", 'error')
        conn.close()
        return redirect(url_for('dorm_details', dorm_id=dorm_id))

    images = request.form.getlist('images')
    
    try:
        conn.execute('INSERT INTO rooms (dorm_id, room_type, price, room_count, images) VALUES (?, ?, ?, ?, ?)',
                     (dorm_id, room_type, price, room_count, json.dumps(images)))
        conn.commit()
        flash('เพิ่มห้องพักสำเร็จแล้ว!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'เกิดข้อผิดพลาดในการเพิ่มห้องพัก: {e}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dorm_details', dorm_id=dorm_id))

@app.route('/edit_dorm/<int:dorm_id>', methods=['GET', 'POST'])
def edit_dorm(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ? AND owner_id = ?', (dorm_id, user_id)).fetchone()

    if dorm is None:
        flash('ไม่พบหอพัก หรือคุณไม่มีสิทธิ์แก้ไขหอพักนี้', 'error')
        conn.close()
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            name = request.form['dorm_name']
            water_fee = float(request.form['water_fee'])
            electricity_fee = float(request.form['electricity_fee'])
            deposit = float(request.form['deposit'])
            contact_line = request.form['contact_line']
            contact_phone = request.form['contact_phone']
            location_lat = float(request.form['location_lat'])
            location_long = float(request.form['location_long'])
        except (ValueError, KeyError) as e:
            flash(f'ข้อมูลไม่ถูกต้อง: {e}', 'error')
            conn.close()
            return redirect(url_for('edit_dorm', dorm_id=dorm_id))

        try:
            conn.execute('''
                UPDATE dorms
                SET name = ?, water_fee = ?, electricity_fee = ?, deposit = ?,
                contact_line = ?, contact_phone = ?, location_lat = ?, location_long = ?
                WHERE id = ? AND owner_id = ?
            ''', (name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long, dorm_id, user_id))
            conn.commit()
            flash('แก้ไขข้อมูลหอพักเรียบร้อยแล้ว!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {e}', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('home'))
        
    conn.close()
    return render_template('edit_dorm.html', dorm=dorm)

@app.route('/delete_dorm/<int:dorm_id>', methods=['POST'])
def delete_dorm(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ? AND owner_id = ?', (dorm_id, user_id)).fetchone()
    
    if dorm is None:
        flash('ไม่พบหอพัก หรือคุณไม่มีสิทธิ์ลบหอพักนี้', 'error')
        conn.close()
        return redirect(url_for('home'))

    try:
        conn.execute('DELETE FROM rooms WHERE dorm_id = ?', (dorm_id,))
        conn.execute('DELETE FROM dorms WHERE id = ?', (dorm_id,))
        conn.commit()
        flash('ลบหอพักเรียบร้อยแล้ว!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'เกิดข้อผิดพลาดในการลบหอพัก: {e}', 'error')
    finally:
        conn.close()

    return redirect(url_for('home'))

@app.route('/approve_dorm/<int:dorm_id>', methods=['POST'])
def approve_dorm(dorm_id):
    if 'username' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    dorm = conn.execute('SELECT * FROM dorms WHERE id = ?', (dorm_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id = ?', (dorm_id,)).fetchall()
    
    if dorm is None:
        conn.close()
        return jsonify({"status": "error", "message": "Dorm not found"}), 404

    payload = {
        "dorm_info": dict(dorm),
        "room_info": [dict(room) for room in rooms]
    }
    
    print("Sending data to Admin API for approval:", payload)
    
    try:
        conn.execute('UPDATE dorms SET is_approved = 2 WHERE id = ?', (dorm_id,))
        conn.commit()
        flash('ส่งข้อมูลหอพักเพื่อขออนุมัติเรียบร้อยแล้ว!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'เกิดข้อผิดพลาดในการส่งข้อมูลเพื่ออนุมัติ: {e}', 'error')
    finally:
        conn.close()

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash('คุณออกจากระบบเรียบร้อยแล้ว', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)