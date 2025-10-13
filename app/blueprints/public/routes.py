from flask import render_template, request, current_app
from . import bp

@bp.get("/")
def index():
    """
    รับ query-string จากผู้ใช้ (เช่น ?q=&min=&max=&amenities=...),
    ส่งต่อให้ SearchService, render templates/public/index.html
    """
    svc = current_app.extensions["container"]["search_service"]

    # รวบรวม filters จาก query string
    filters = {
        "q": request.args.get("q") or None,
        "road": request.args.get("road") or None,
        "soi": request.args.get("soi") or None,
        "min_price": request.args.get("min_price"),
        "max_price": request.args.get("max_price"),
        "room_type": request.args.get("room_type") or None,
        "amenities": request.args.get("amenities") or None,
        "availability": request.args.get("availability") or None,
        "sort": request.args.get("sort") or None,
        # (Optional) near and radius_km can be added here
    }

    # ดึงค่า page และ per_page
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=12, type=int)

    # เรียกใช้ service เพื่อค้นหา
    result = svc.search(filters, page=page, per_page=per_page) 
    return render_template("public/index.html", **result)

@bp.get("/search")
def search():
    """แสดงหน้าค้นหาพร้อมส่งข้อมูลสิ่งอำนวยความสะดวกสำหรับตัวกรอง"""
    # [FIXED] ย้าย import Amenity มาไว้ที่นี่เพื่อแก้ Circular Import
    from app.models.property import Amenity 
    
    amenities = Amenity.query.order_by(Amenity.label_th).all()
    # ในอนาคต ส่วนนี้จะรับค่าจากฟอร์มเพื่อไปค้นหาข้อมูลจริง
    # ตอนนี้จะแสดงหน้าฟอร์มพร้อมตัวเลือกก่อน
    return render_template("public/search.html", amenities=amenities)

@bp.get("/property/<int:prop_id>")
def property_detail(prop_id: int):
    # ... (โค้ดส่วนที่เหลือ) ...
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id)
    if not prop or prop.workflow_status != 'approved':
        return render_template("public/detail.html", prop=None), 404
    return render_template("public/detail.html", prop=prop)