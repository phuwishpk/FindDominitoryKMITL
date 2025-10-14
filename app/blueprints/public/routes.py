from flask import render_template, request, current_app
from . import bp
from app.models.property import Amenity, Property # <-- เพิ่มการ import Property

@bp.get("/")
def index():
    """
    (แก้ไข) แสดงหน้าหลักโดยดึงข้อมูลหอพักที่อัปเดตล่าสุด 8 รายการ
    """
    svc = current_app.extensions["container"]["search_service"]
    
    # --- ส่วนที่แก้ไข ---
    # เราจะส่ง filter 'sort' เพื่อบอกให้ repository เรียงข้อมูลตามวันที่อัปเดตล่าสุด
    # และกำหนด per_page เป็น 8 เพื่อดึงแค่ 8 รายการ
    filters = { 
        "sort": "updated_at_desc" 
    }
    per_page = 8
    # --- สิ้นสุดการแก้ไข ---
    
    result = svc.search(filters, page=1, per_page=per_page) 
    return render_template("public/index.html", **result)

@bp.get("/search")
def search():
    """
    (แก้ไข) แสดงหน้าค้นหาพร้อมส่งข้อมูลสิ่งอำนวยความสะดวกสำหรับตัวกรอง
    และแสดงผลการค้นหาหากมี query parameters
    """
    svc = current_app.extensions["container"]["search_service"]
    
    # --- 1. รวบรวม Filters จาก URL (request.args) ---
    room_type_select = request.args.get("room_type") or None
    room_type_value = room_type_select
    
    if room_type_select == 'other':
        # ถ้าเลือก 'อื่นๆ' ให้ใช้ค่าจากช่อง 'ระบุประเภทห้องอื่นๆ'
        room_type_value = request.args.get("other_room_type") or "other"

    amenities_list = request.args.getlist("amenities")
    
    filters = {
        "q": request.args.get("q") or None,
        "road": request.args.get("road") or None,
        "soi": request.args.get("soi") or None,
        "room_type": room_type_value,
        "min_price": request.args.get("min_price") or None,
        "max_price": request.args.get("max_price") or None,
        "amenities": ",".join(amenities_list) if amenities_list else None,
        
        # เพิ่ม 2 รายการนี้เพื่อให้ส่งค่ากลับไป pre-fill ฟอร์มได้ถูกต้อง
        "room_type_select": room_type_select, 
        "other_room_type": request.args.get("other_room_type") or None,
    }

    # --- 2. ดึงข้อมูลสำหรับ Search Form ---
    all_amenities = Amenity.query.order_by(Amenity.label_th).all()

    # --- 3. ทำการค้นหา ---
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=12, type=int)
    
    # สร้าง dict สำหรับส่งให้ service (ไม่รวมค่าที่ใช้สำหรับ pre-fill)
    search_filters = filters.copy()
    search_filters.pop("room_type_select", None)
    search_filters.pop("other_room_type", None)

    # search_service.search() จะคืน dict ที่มี items, page, total, etc.
    result_data = svc.search(search_filters, page=page, per_page=per_page) 
    
    # --- 4. Render Template ---
    return render_template(
        "public/search.html", 
        amenities=all_amenities,       # สำหรับ Checkbox
        filters=filters,               # สำหรับ pre-fill ฟอร์ม
        amenities_list=amenities_list, # สำหรับ pre-check checkboxes
        **result_data                  # ส่งผลการค้นหา (items, page, total, etc.)
    )

@bp.get("/property/<int:prop_id>")
def property_detail(prop_id: int):
    # ... (โค้ดส่วนนี้เหมือนเดิม)
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id)
    if not prop or prop.workflow_status != 'approved':
        return render_template("public/detail.html", prop=None), 404
    return render_template("public/detail.html", prop=prop)

@bp.get("/contact")
def contact():
    """แสดงหน้าติดต่อเรา"""
    return render_template("public/contact.html")