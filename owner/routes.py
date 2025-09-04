# owner/routes.py
from flask import render_template, request, redirect, url_for, session
from . import owner_bp
from core.db import get_db_connection, init_db
import json

init_db()

def require_owner():
    return session.get('user_type') == 'owner'

@owner_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=? AND user_type='owner'",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session.clear()
            session['username']  = user['username']
            session['user_id']   = user['id']
            session['user_type'] = user['user_type']
            return redirect(url_for('owner.dashboard'))
        return render_template('owner/login.html', error='Invalid owner username or password')
    return render_template('owner/login.html')

@owner_bp.route('/')
def dashboard():
    if not require_owner():
        return redirect(url_for('owner.login'))
    uid = session.get('user_id')
    conn = get_db_connection()
    dorms = conn.execute('SELECT * FROM dorms WHERE owner_id=?', (uid,)).fetchall()
    conn.close()
    return render_template('owner/dashboard.html', username=session.get('username'), dorms=dorms)

@owner_bp.route('/add_dorm', methods=['GET', 'POST'])
def add_dorm():
    if not require_owner():
        return redirect(url_for('owner.login'))
    if request.method == 'POST':
        name = request.form['dorm_name']
        try:
            water_fee       = float(request.form['water_fee'])
            electricity_fee = float(request.form['electricity_fee'])
            deposit         = float(request.form['deposit'])
            location_lat    = float(request.form['location_lat'])
            location_long   = float(request.form['location_long'])
        except (ValueError, KeyError):
            return "Invalid data format for numeric fields.", 400

        contact_line  = request.form.get('contact_line')
        contact_phone = request.form.get('contact_phone')

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO dorms (owner_id, name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long, is_approved)
            VALUES (?,?,?,?,?,?,?,?,?,2)
        ''', (session.get('user_id'), name, water_fee, electricity_fee, deposit, contact_line, contact_phone, location_lat, location_long))
        conn.commit()
        conn.close()
        return redirect(url_for('owner.dashboard'))
    return render_template('owner/dorm_details.html', dorm=None, rooms=[])

@owner_bp.route('/dorm/<int:dorm_id>')
def dorm_details(dorm_id):
    if not require_owner():
        return redirect(url_for('owner.login'))
    conn = get_db_connection()
    dorm  = conn.execute('SELECT * FROM dorms WHERE id=? AND owner_id=?', (dorm_id, session.get('user_id'))).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id=?', (dorm_id,)).fetchall()
    conn.close()
    if dorm is None:
        return "Dorm not found or not your dorm.", 404
    return render_template('owner/dorm_details.html', dorm=dorm, rooms=rooms)

@owner_bp.route('/add_room/<int:dorm_id>', methods=['POST'])
def add_room(dorm_id):
    if not require_owner():
        return redirect(url_for('owner.login'))

    room_type = request.form['room_type']
    try:
        price = float(request.form['price'])
        room_count = int(request.form['room_count'])
    except (ValueError, KeyError):
        return "Invalid data format for numeric fields.", 400

    images = request.form.getlist('images')
    images_json = json.dumps(images)

    conn = get_db_connection()
    owns = conn.execute('SELECT 1 FROM dorms WHERE id=? AND owner_id=?', (dorm_id, session.get('user_id'))).fetchone()
    if not owns:
        conn.close()
        return "Not authorized to add rooms to this dorm.", 403

    conn.execute('INSERT INTO rooms (dorm_id, room_type, price, room_count, images) VALUES (?,?,?,?,?)',
                 (dorm_id, room_type, price, room_count, images_json))
    conn.commit()
    conn.close()
    return redirect(url_for('owner.dorm_details', dorm_id=dorm_id))

@owner_bp.route('/approve_dorm/<int:dorm_id>', methods=['POST'])
def approve_dorm(dorm_id):
    if not require_owner():
        return redirect(url_for('owner.login'))
    conn = get_db_connection()
    conn.execute('UPDATE dorms SET is_approved=2 WHERE id=? AND owner_id=?', (dorm_id, session.get('user_id')))
    conn.commit()
    conn.close()
    return redirect(url_for('owner.dorm_details', dorm_id=dorm_id))

@owner_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('owner.login'))
