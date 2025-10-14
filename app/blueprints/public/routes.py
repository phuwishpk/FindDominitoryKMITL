from flask import render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user
from . import bp
from app.forms.review import ReviewForm
from app.models.review import Review
from app.extensions import db
from app.models.property import Amenity, Property


@bp.get("/")
def index():
    """
    แสดงหน้าหลักโดยดึงข้อมูลหอพักที่อัปเดตล่าสุด 8 รายการ
    """
    svc = current_app.extensions["container"]["search_service"]

    filters = {
        "sort": "updated_at_desc"
    }
    per_page = 8

    result = svc.search(filters, page=1, per_page=per_page)
    return render_template("public/index.html", **result)


# ✅ เพิ่มรีวิว (POST)
@bp.post("/property/<int:prop_id>/review")
def property_add_review(prop_id):
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id)

    if not prop or prop.workflow_status != 'approved':
        return render_template("public/detail.html", prop=None), 404

    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(
            property_id=prop_id,
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(review)
        db.session.commit()
        flash("รีวิวของคุณถูกบันทึกแล้ว", "success")

    # ✅ กลับไปหน้าเดิม (อย่า render ตรงนี้ เพราะเราต้องดึงข้อมูลใหม่ใน property_detail)
    return redirect(url_for("public.property_detail", prop_id=prop_id))


# ✅ แสดงรายละเอียดหอพัก (GET)
@bp.get("/property/<int:prop_id>")
def property_detail(prop_id: int):
    repo = current_app.extensions["container"]["property_repo"]
    prop = repo.get(prop_id)

    if not prop or prop.workflow_status != 'approved':
        return render_template("public/detail.html", prop=None), 404

    # ✅ ดึงรีวิวทั้งหมด + คำนวณคะแนนเฉลี่ย
    reviews = Review.query.filter_by(property_id=prop_id).order_by(Review.created_at.desc()).all()
    avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0.0

    # ✅ สร้างฟอร์มใหม่ทุกครั้ง
    form = ReviewForm()

    return render_template(
        "public/detail.html",
        prop=prop,
        form=form,
        reviews=reviews,
        avg_rating=avg_rating
    )


@bp.get("/search")
def search():
    """
    แสดงหน้าค้นหาพร้อมตัวกรองและผลลัพธ์
    """
    svc = current_app.extensions["container"]["search_service"]

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


@bp.get("/contact")
def contact():
    """แสดงหน้าติดต่อเรา"""
    return render_template("public/contact.html")
