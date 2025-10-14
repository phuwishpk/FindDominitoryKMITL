from flask import render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user
from . import bp
from app.forms.review import ReviewForm
from app.models.property import Amenity, Property

@bp.get("/")
def index():
    """
    แสดงหน้าหลักโดยดึงข้อมูลหอพักที่อัปเดตล่าสุด 8 รายการ
    """
    svc = current_app.extensions["container"]["search_service"]

    # เราจะส่ง filter 'sort' เพื่อบอกให้ repository เรียงข้อมูลตามวันที่อัปเดตล่าสุด
    # และกำหนด per_page เป็น 8 เพื่อดึงแค่ 8 รายการ
    filters = {"sort": "updated_at_desc"}
    per_page = 8

    result = svc.search(filters, page=1, per_page=per_page)
    return render_template("public/index.html", **result)


@bp.get("/search")
def search():
    """
    แสดงหน้าค้นหาพร้อมส่งข้อมูลสิ่งอำนวยความสะดวกสำหรับตัวกรอง
    และแสดงผลการค้นหาหากมี query parameters
    """
    svc = current_app.extensions["container"]["search_service"]

    # --- 1. รวบรวม Filters จาก URL (request.args) ---
    room_type_select = request.args.get("room_type") or None
    room_type_value = room_type_select

    if room_type_select == "other":
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
        # สำหรับ pre-fill ฟอร์ม
        "room_type_select": room_type_select,
        "other_room_type": request.args.get("other_room_type") or None,
    }

    # --- 2. ดึงข้อมูลสำหรับ Search Form ---
    all_amenities = Amenity.query.order_by(Amenity.label_th).all()

    # --- 3. ทำการค้นหา ---
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=12, type=int)

    # กรองค่าที่ไม่เกี่ยวกับการค้นหาออก
    search_filters = filters.copy()
    search_filters.pop("room_type_select", None)
    search_filters.pop("other_room_type", None)

    result_data = svc.search(search_filters, page=page, per_page=per_page)

    # --- 4. Render Template ---
    return render_template(
        "public/search.html",
        amenities=all_amenities,
        filters=filters,
        amenities_list=amenities_list,
        **result_data,
    )


@bp.route("/property/<int:prop_id>", methods=["GET", "POST"])
def property_detail(prop_id: int):
    """
    แสดงรายละเอียดหอพัก พร้อมฟอร์มรีวิว (หากผู้ใช้ล็อกอิน)
    """
    repo = current_app.extensions["container"]["property_repo"]
    review_svc = current_app.extensions["container"]["review_service"]
    prop = repo.get(prop_id)

    if not prop or prop.workflow_status != "approved":
        return render_template("public/detail.html", prop=None), 404

    form = ReviewForm()

    if form.validate_on_submit():
        user_id = current_user.ref_id if current_user.is_authenticated else None
        review_svc.add_review(
            property_id=prop.id,
            user_id=user_id,
            comment=form.comment.data,
            rating=int(form.rating.data),
        )
        flash("ขอบคุณสำหรับรีวิวของคุณ")
        return redirect(url_for("public.property_detail", prop_id=prop.id))

    review_data = review_svc.get_reviews_and_average_rating(prop_id)

    return render_template(
        "public/detail.html",
        prop=prop,
        form=form,
        reviews=review_data["reviews"],
        avg_rating=review_data["average_rating"],
    )


@bp.get("/contact")
def contact():
    """แสดงหน้าติดต่อเรา"""
    return render_template("public/contact.html")
