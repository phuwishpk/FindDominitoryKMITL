from flask import render_template, request, current_app
from . import bp

@bp.get("/")
def index():
    """
    รับ query-string จากผู้ใช้ (เช่น ?q=&min=&max=&amenities=...),
    ส่งต่อให้ SearchService, render templates/public/index.html
    """
    # ดึง SearchService จาก DI container
    svc = current_app.extensions["container"]["search_service"]

    # รวบรวม filters จาก query string
    filters = {
        "q": request.args.get("q") or None,
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

    # ส่งผลลัพธ์ไป render ที่หน้าเว็บ
    return render_template("public/index.html", **result)

@bp.get("/property/<int:prop_id>")
def property_detail(prop_id: int):
    """
    ดึงประกาศ 1 รายการ (approved เท่านั้น) พร้อมรูป/amenities,
    render หน้า detail
    """
    # ดึง PropertyRepo จาก DI container
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id) # repo.get ควรจะกรองเฉพาะ approved แล้ว

    # ถ้าไม่พบข้อมูล จะแสดงหน้า 404 Not Found
    if not prop:
        return render_template("public/detail.html", prop=None), 404

    # ส่งข้อมูล property ไปแสดงผลที่หน้า detail
    return render_template("public/detail.html", prop=prop)