from flask import render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user
from . import bp
from app.forms.review import ReviewForm
from app.models.property import Amenity

# ✅ แสดงหน้าหลัก (GET)
@bp.get("/")
def index():
    """
    แสดงหน้าหลักโดยดึงข้อมูลหอพักที่อัปเดตล่าสุด 8 รายการ
    """
    svc = current_app.extensions["container"]["search_service"]
    filters = {"sort": "updated_at_desc"}
    per_page = 8
    result = svc.search(filters, page=1, per_page=per_page)
    return render_template("public/index.html", **result)


# ✅ เพิ่มรีวิว (POST)
@bp.post("/property/<int:prop_id>/review")
def property_add_review(prop_id):
    """
    จัดการการส่งฟอร์มเพื่อเพิ่มรีวิวสำหรับหอพัก
    """
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id)

    # หากหอพักไม่ได้รับการอนุมัติหรือไม่พบ ให้ Redirect กลับ
    if not prop or prop.workflow_status != 'approved':
        return redirect(url_for("public.property_detail", prop_id=prop_id))

    form = ReviewForm()
    if form.validate_on_submit():
        review_svc = current_app.extensions["container"]["review_service"]
        user_ref_id = current_user.ref_id if current_user.is_authenticated else None

        review_svc.add_review(
            property_id=prop_id,
            user_id=user_ref_id,
            comment=form.comment.data,
            rating=int(form.rating.data)  # แปลง rating เป็น int
        )
        flash("รีวิวของคุณถูกบันทึกแล้ว", "success")

    # กลับไปยังหน้ารายละเอียดหอพักเดิม
    return redirect(url_for("public.property_detail", prop_id=prop_id))


# ✅ แสดงรายละเอียดหอพัก (GET)
@bp.get("/property/<int:prop_id>")
def property_detail(prop_id: int):
    """
    แสดงหน้ารายละเอียดของหอพัก พร้อมรีวิวและคะแนนเฉลี่ย
    """
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id)

    if not prop or prop.workflow_status != 'approved':
        return render_template("public/detail.html", prop=None), 404
    
    # บันทึกประวัติการเข้าชม
    history_svc = current_app.extensions["container"]["history_service"]
    history_svc.add_viewed_property(prop_id)

    review_svc = current_app.extensions["container"]["review_service"]
    reviews_data = review_svc.get_reviews_and_average_rating(prop_id)

    return render_template(
        "public/detail.html",
        prop=prop,
        form=ReviewForm(),  # สร้างฟอร์มรีวิวใหม่ทุกครั้ง
        reviews=reviews_data["reviews"],
        avg_rating=reviews_data["average_rating"]
    )


# ✅ แสดงหน้าค้นหา (GET)
@bp.get("/search")
def search():
    """
    แสดงหน้าค้นหาพร้อมตัวกรองและผลลัพธ์
    """
    svc = current_app.extensions["container"]["search_service"]
    
    # จัดการข้อมูลจากฟอร์มค้นหา
    room_type_select = request.args.get("room_type") or None
    room_type_value = room_type_select
    if room_type_select == 'other':
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
        "room_type_select": room_type_select,
        "other_room_type": request.args.get("other_room_type") or None,
    }

    all_amenities = Amenity.query.order_by(Amenity.label_th).all()
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=12, type=int)
    
    # สร้าง filters สำหรับส่งไป service โดยไม่รวมค่าที่ไม่จำเป็น
    search_filters = filters.copy()
    search_filters.pop("room_type_select", None)
    search_filters.pop("other_room_type", None)

    result_data = svc.search(search_filters, page=page, per_page=per_page)

    return render_template(
        "public/search.html",
        amenities=all_amenities,
        filters=filters,
        amenities_list=amenities_list,
        **result_data
    )

# ✅ แสดงหน้าประวัติการเข้าชม (GET)
@bp.get("/history")
def history():
    """แสดงหน้าประวัติการเข้าชม"""
    return render_template("public/history.html")

# ✅ แสดงหน้าติดต่อเรา (GET)
@bp.get("/contact")
def contact():
    """แสดงหน้าติดต่อเรา"""
    return render_template("public/contact.html")


# ✅ แสดงหน้า Privacy Policy (GET)
@bp.get("/privacy")
def privacy():
    """แสดงหน้า Privacy Policy"""
    return render_template("public/privacy.html")


# ✅ แสดงหน้า Terms of Service (GET)
@bp.get("/terms")
def terms():
    """แสดงหน้า Terms of Service"""
    return render_template("public/terms.html")