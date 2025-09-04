# user/routes.py
from flask import render_template, request, url_for, redirect
from . import user_bp
from core.db import get_db_connection, init_db
import json

# เผื่อไฟล์ DB ถูกลบ
init_db()

@user_bp.route('/')
def _root_redirect():
    from flask import redirect, url_for
    return redirect(url_for('user.user_home'))


# --------- ยูทิลเล็ก ๆ ----------
def _first_image_from_json(images_json: str):
    """รับสตริง JSON (list ของ url) แล้วคืนภาพแรก ถ้าไม่มีคืน None"""
    if not images_json:
        return None
    try:
        arr = json.loads(images_json)
        if isinstance(arr, list) and arr:
            return arr[0]
    except Exception:
        pass
    return None

# --------- Routes ฝั่งผู้ใช้ ----------
@user_bp.route('/u')
def user_home():
    """
    หน้าหลัก: แสดงหอพักแบบการ์ด + ค้นหาชื่อ + ช่วงราคา
    พารามิเตอร์:
      q         = คำค้นชื่อหอ
      price     = ช่วงราคา (any, 0-3000, 3000-5000, 5000-8000, 8000+)
    """
    q = request.args.get('q', '').strip()
    price = request.args.get('price', 'any')

    # เราจะเลือก min_price ของแต่ละหอจากตาราง rooms
    # เฉพาะหอที่อนุมัติแล้ว (is_approved = 1)
    sql = '''
      SELECT d.*,
             MIN(r.price) AS min_price,
             MAX(r.price) AS max_price,
             MIN(r.images) AS any_images_json
      FROM dorms d
      LEFT JOIN rooms r ON r.dorm_id = d.id
      WHERE d.is_approved = 1
    '''
    params = []

    if q:
        sql += " AND d.name LIKE ?"
        params.append(f"%{q}%")

    sql += " GROUP BY d.id"

    # ฟิลเตอร์ช่วงราคาโดยใช้ min_price (หรือ max_price เผื่อไม่มีห้องให้โชว์)
    # กลยุทธ์: ถ้าเลือกช่วงราคา จะให้ min_price อยู่ในช่วงนั้น
    price_ranges = {
        '0-3000':   (0, 3000),
        '3000-5000': (3000, 5000),
        '5000-8000': (5000, 8000),
        '8000+':    (8000, 10**9),
    }

    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    cards = []
    for r in rows:
        # กำหนดภาพปกจากภาพแรกของห้องใดก็ได้ (ถ้ามี)
        cover_img = None
        if r['any_images_json']:
            cover_img = _first_image_from_json(r['any_images_json'])

        # กรองช่วงราคาหลัง GROUP BY (ง่าย และยืดหยุ่น)
        if price in price_ranges and r['min_price'] is not None:
            lo, hi = price_ranges[price]
            if not (lo <= r['min_price'] <= hi):
                continue

        cards.append({
            'id': r['id'],
            'name': r['name'],
            'min_price': r['min_price'],
            'max_price': r['max_price'],
            'cover_img': cover_img
        })

    return render_template('user/index.html',
                           q=q,
                           price=price,
                           cards=cards)

@user_bp.route('/u/dorm/<int:dorm_id>')
def user_dorm_detail(dorm_id):
    """
    หน้าเนื้อหารายละเอียดหอพัก
    """
    conn = get_db_connection()
    dorm  = conn.execute('SELECT * FROM dorms WHERE id=? AND is_approved=1', (dorm_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms WHERE dorm_id=?', (dorm_id,)).fetchall()
    conn.close()

    if not dorm:
        return "Dormitory not found or not approved.", 404

    # เตรียมภาพโชว์รวม (หยิบภาพแรกของแต่ละห้อง)
    gallery = []
    for rm in rooms:
        img = _first_image_from_json(rm['images'])
        if img:
            gallery.append(img)

    return render_template('user/dorm_detail.html',
                           dorm=dorm,
                           rooms=rooms,
                           gallery=gallery)
