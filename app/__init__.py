from flask import Flask
import os
import sqlite3

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_super_secret_key'

    # Initialize DB if it doesn't exist
    db_path = os.path.join(app.instance_path, '..', 'dorm_management.db')
    if not os.path.exists(db_path):
        init_db(db_path)

    # Register Blueprints
    from . import routes
    app.register_blueprint(routes.main_bp)

    from . import owner_routes
    app.register_blueprint(owner_routes.owner_bp)

    from . import admin_routes
    app.register_blueprint(admin_routes.admin_bp)

    return app

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    # ... (โค้ดสร้าง Table ทั้ง 3 ตารางเหมือนเดิม) ...
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
    
    # Add sample users
    conn.execute("INSERT OR IGNORE INTO users (username, password, user_type) VALUES ('owner', 'owner', 'owner')")
    conn.execute("INSERT OR IGNORE INTO users (username, password, user_type) VALUES ('admin', 'admin', 'admin')")
    conn.commit()
    conn.close()