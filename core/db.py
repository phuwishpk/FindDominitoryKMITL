# core/db.py
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # โฟลเดอร์โปรเจ็กต์
DB_PATH = os.path.join(BASE_DIR, 'dorm_management.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Users
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('admin','owner'))
        )
    ''')
    # Dorms
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
            is_approved INTEGER DEFAULT 2, -- 0=reject,1=approve,2=pending
            rejection_reason TEXT,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    # Rooms
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

    # seed users
    existing = {r['username'] for r in conn.execute(
        "SELECT username FROM users WHERE username IN ('owner','admin')"
    ).fetchall()}
    if 'owner' not in existing:
        conn.execute("INSERT INTO users (username, password, user_type) VALUES (?,?,?)",
                     ('owner', 'owner', 'owner'))
    if 'admin' not in existing:
        conn.execute("INSERT INTO users (username, password, user_type) VALUES (?,?,?)",
                     ('admin', 'admin', 'admin'))

    conn.commit()
    conn.close()

# สร้างไฟล์ DB ครั้งแรกถ้ายังไม่มี
if not os.path.exists(DB_PATH):
    init_db()
