# app/blueprints/owner/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime
import json
from . import bp
from app.forms.owner import PropertyForm, RequestReviewDeletionForm
from app.forms.upload import UploadImageForm, ReorderImagesForm, EmptyForm
from app.models.property import Property, PropertyImage, Amenity
from app.models.approval import ApprovalRequest, AuditLog
from app.models.review import Review
from app.extensions import owner_required, db

try:
    from app.services.policies.property_policy import PropertyPolicy
except Exception:
    class PropertyPolicy:
        MAX_IMAGES = 6
        @staticmethod
        def can_upload_more(current_count: int) -> bool:
            return current_count < 6

@bp.get("/dashboard")
@login_required
@owner_required
def dashboard():
    props = Property.query.filter_by(owner_id=current_user.ref_id, deleted_at=None).all()
    rejected_notes = {}
    rejected_prop_ids = [p.id for p in props if p.workflow_status == 'rejected']
    if rejected_prop_ids:
        latest_requests_sq = db.session.query(
            ApprovalRequest.property_id,
            func.max(ApprovalRequest.id).label('max_id')
        ).filter(
            ApprovalRequest.property_id.in_(rejected_prop_ids)
        ).group_by(ApprovalRequest.property_id).subquery()
        notes_query = db.session.query(
            ApprovalRequest.property_id,
            ApprovalRequest.note
        ).join(
            latest_requests_sq,
            ApprovalRequest.id == latest_requests_sq.c.max_id
        ).filter(ApprovalRequest.note.isnot(None))
        rejected_notes = dict(notes_query.all())
    submit_form = EmptyForm()
    delete_form = EmptyForm()
    return render_template("owner/dashboard.html",
                           props=props,
                           submit_form=submit_form,
                           delete_form=delete_form,
                           rejected_notes=rejected_notes)

@bp.route("/property/new", methods=["GET","POST"])
@login_required
@owner_required
def new_property():
    form = PropertyForm()
    all_amenities = Amenity.query.all()
    selected_amenities = []
    if request.method == "POST":
        selected_amenities = request.form.getlist('amenities')
    if form.validate_on_submit():
        prop_svc = current_app.extensions["container"]["property_service"]
        upload_svc = current_app.extensions["container"]["upload_service"]
        form_data = form.data.copy()
        form_data.pop('csrf_token', None)
        form_data['amenities'] = request.form.getlist('amenities')
        prop = prop_svc.create(current_user.ref_id, form_data)
        images = form.images.data
        if images and images[0].filename:
            for i, file_storage in enumerate(images):
                if i >= PropertyPolicy.MAX_IMAGES:
                    flash(f"อัปโหลดได้สูงสุด {PropertyPolicy.MAX_IMAGES} รูปเท่านั้น", "warning")
                    break
                if file_storage:
                    path = upload_svc.save_image(current_user.ref_id, file_storage)
                    img = PropertyImage(property_id=prop.id, file_path=path, position=i + 1)
                    db.session.add(img)
            db.session.commit()
        flash("สร้างประกาศสำเร็จแล้ว", "success")
        flash('clear_form_storage', 'script_command')
        return redirect(url_for("owner.dashboard"))
    return render_template("owner/form.html",
        form=form,
        all_amenities=all_amenities,
        prop=None,
        upload_form=UploadImageForm(),
        PropertyPolicy=PropertyPolicy,
        selected_amenities=selected_amenities
    )

@bp.route("/property/<int:prop_id>/edit", methods=["GET","POST"])
@login_required
@owner_required
def edit_property(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return redirect(url_for("owner.dashboard"))
    form = PropertyForm(obj=prop)
    predefined_choices = [choice[0] for choice in form.room_type.choices]
    if request.method == "POST":
        selected_amenities = request.form.getlist('amenities')
    else:
        selected_amenities = [amenity.code for amenity in prop.amenities]
    if request.method == "GET":
        if prop.room_type not in predefined_choices:
            form.room_type.data = 'other'
            form.other_room_type.data = prop.room_type
        if prop.location_pin:
            form.location_pin_json.data = json.dumps(prop.location_pin)
        if prop.line_id is None:
            form.line_id.data = "-"
        if prop.facebook_url is None:
            form.facebook_url.data = "-"
    upload_form = UploadImageForm()
    reorder_form = ReorderImagesForm()
    all_amenities = Amenity.query.all()
    approval_note = None
    if prop.workflow_status == 'rejected':
        last_request = ApprovalRequest.query.filter_by(property_id=prop.id).order_by(ApprovalRequest.created_at.desc()).first()
        if last_request:
            approval_note = last_request.note
    if form.validate_on_submit() and ("save_property" in request.form or "save_and_exit" in request.form):
        prop_svc = current_app.extensions["container"]["property_service"]
        form_data = PropertyForm(request.form).data
        form_data.pop('csrf_token', None)
        form_data['amenities'] = request.form.getlist('amenities')
        images_to_delete_str = request.form.get('images_to_delete', '')
        if images_to_delete_str:
            image_ids_to_delete = [int(id_) for id_ in images_to_delete_str.split(',') if id_.isdigit()]
            if image_ids_to_delete:
                images_to_delete = db.session.query(PropertyImage).filter(
                    PropertyImage.property_id == prop_id,
                    PropertyImage.id.in_(image_ids_to_delete)
                ).all()
                for img in images_to_delete:
                    db.session.delete(img)
        prop_svc.update(current_user.ref_id, prop_id, form_data)
        
        # --- vvv เพิ่ม Real-Time Emit: แก้ไข Property โดย Owner vvv ---
        socketio.emit('property_updated', {'id': prop_id, 'status': prop.workflow_status}, namespace='/') 
        # --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---
        
        flash("อัปเดตข้อมูลแล้ว", "success")
        if "save_and_exit" in request.form:
            return redirect(url_for("owner.dashboard"))
        else:
            return redirect(url_for("owner.edit_property", prop_id=prop.id))
    return render_template("owner/form.html",
                           form=form, prop=prop,
                           upload_form=upload_form, reorder_form=reorder_form,
                           all_amenities=all_amenities,
                           approval_note=approval_note,
                           PropertyPolicy=PropertyPolicy,
                           selected_amenities=selected_amenities
                           )

@bp.post("/property/<int:prop_id>/image")
@login_required
@owner_required
def upload_image(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return redirect(url_for("owner.dashboard"))
    form = UploadImageForm()
    if form.validate_on_submit() and form.image.data and form.image.data[0].filename:
        upload_svc = current_app.extensions["container"]["upload_service"]
        for i, file_storage in enumerate(form.image.data):
            count = PropertyImage.query.filter_by(property_id=prop.id).count()
            if count >= PropertyPolicy.MAX_IMAGES:
                flash(f"อัปโหลดได้สูงสุด {PropertyPolicy.MAX_IMAGES} รูปเท่านั้น", "warning")
                break
            if file_storage:
                path = upload_svc.save_image(current_user.ref_id, file_storage)
                max_pos = (PropertyImage.query.with_entities(func.max(PropertyImage.position))
                           .filter_by(property_id=prop.id).scalar()) or 0
                img = PropertyImage(property_id=prop.id, file_path=path, position=max_pos + 1)
                db.session.add(img)
        db.session.commit()
        flash("อัปโหลดรูปสำเร็จ", "success")
    else:
        flash("กรุณาเลือกไฟล์รูปภาพ", "danger")
    return redirect(url_for("owner.edit_property", prop_id=prop.id, tab="images"))

@bp.post("/property/<int:prop_id>/images/reorder")
@login_required
@owner_required
def reorder_images(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return jsonify({"success": False, "message": "Permission denied."}), 403

    data = request.get_json()
    image_ids = data.get('order')

    if not isinstance(image_ids, list):
        return jsonify({"success": False, "message": "Invalid data format."}), 400

    images = PropertyImage.query.filter(
        PropertyImage.property_id == prop.id,
        PropertyImage.id.in_(image_ids)
    ).all()

    id_to_image_map = {img.id: img for img in images}

    for i, img_id in enumerate(image_ids):
        if img_id in id_to_image_map:
            id_to_image_map[img_id].position = i + 1

    db.session.commit()
    return jsonify({"success": True, "message": "จัดเรียงรูปภาพสำเร็จ"})

@bp.post("/property/<int:prop_id>/submit")
@login_required
@owner_required
def submit_for_approval(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return redirect(url_for("owner.dashboard"))
    approval_svc = current_app.extensions["container"]["approval_service"]
    try:
        approval_svc.submit_property(property_id=prop_id, owner_id=current_user.ref_id)
        flash("ส่งประกาศเพื่อขออนุมัติแล้ว", "success")

        # --- vvv เพิ่ม Real-Time Emit: ส่งขออนุมัติ VVV ---
        # สัญญาณสำหรับหน้า Public/Owner 
        socketio.emit('property_updated', {'id': prop_id, 'status': 'submitted'}, namespace='/')
        # สัญญาณสำหรับ Admin Dashboard
        socketio.emit('admin_dashboard_update', {'type': 'queue_change'}, namespace='/') 
        # --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---

    except ValueError as e:
        flash(f"ไม่สามารถส่งประกาศได้: {str(e)}", "danger")
    return redirect(url_for("owner.dashboard"))

@bp.post("/property/<int:prop_id>/toggle_availability")
@login_required
@owner_required
def toggle_availability(prop_id: int):
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("owner.dashboard"))
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        flash("Permission denied.", "danger")
        return redirect(url_for("owner.dashboard"))
    if prop.availability_status == 'vacant':
        prop.availability_status = 'occupied'
        new_status_th = "ห้องเต็ม"
    else:
        prop.availability_status = 'vacant'
        new_status_th = "ห้องว่าง"
    db.session.commit()
    flash(f"เปลี่ยนสถานะของ '{prop.dorm_name}' เป็น '{new_status_th}' เรียบร้อยแล้ว", "success")

    # --- vvv เพิ่ม Real-Time Emit: เปลี่ยนสถานะว่าง/เต็ม VVV ---
    socketio.emit('property_updated', {'id': prop_id, 'status': prop.workflow_status, 'availability': prop.availability_status}, namespace='/')
    # --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---

    return redirect(url_for("owner.dashboard"))

@bp.post("/property/<int:prop_id>/delete")
@login_required
@owner_required
def delete_property(prop_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for('owner.dashboard'))
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        flash("Permission denied.", "danger")
        return redirect(url_for("owner.dashboard"))
    prop.deleted_at = datetime.utcnow()
    db.session.add(AuditLog.log("owner", current_user.ref_id, "soft_delete_property", prop_id))
    db.session.commit()
    
    # --- vvv เพิ่ม Real-Time Emit: ลบหอพัก (Soft Delete) VVV ---
    socketio.emit('property_updated', {'id': prop_id, 'status': 'deleted'}, namespace='/')
    # --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---
    
    flash(f"ย้ายประกาศ '{prop.dorm_name}' ไปยังถังขยะแล้ว", "success")
    return redirect(url_for('owner.dashboard'))

@bp.route("/trash")
@login_required
@owner_required
def trash():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    pagination = db.paginate(
        Property.query.filter(
            Property.owner_id == current_user.ref_id,
            Property.deleted_at.isnot(None)
        ).order_by(Property.deleted_at.desc()),
        page=page, per_page=per_page, error_out=False
    )
    restore_form = EmptyForm()
    delete_form = EmptyForm()
    return render_template("owner/trash.html", pagination=pagination, restore_form=restore_form, delete_form=delete_form)

@bp.post("/property/<int:prop_id>/restore")
@login_required
@owner_required
def restore_property(prop_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('owner.trash'))
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        flash("Permission denied.", "danger")
        return redirect(url_for("owner.trash"))
    prop.deleted_at = None
    db.session.add(AuditLog.log("owner", current_user.ref_id, "restore_property", prop_id))
    db.session.commit()
    
    # --- vvv เพิ่ม Real-Time Emit: กู้คืนหอพัก VVV ---
    socketio.emit('property_updated', {'id': prop_id, 'status': prop.workflow_status}, namespace='/')
    # --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---
    
    flash(f"กู้คืนประกาศ '{prop.dorm_name}' สำเร็จ", "success")
    return redirect(url_for('owner.trash'))

@bp.post("/property/<int:prop_id>/permanent_delete")
@login_required
@owner_required
def permanently_delete_property(prop_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('owner.trash'))
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        flash("Permission denied.", "danger")
        return redirect(url_for("owner.trash"))
    dorm_name = prop.dorm_name
    db.session.add(AuditLog.log("owner", current_user.ref_id, "permanent_delete_property", meta={"deleted_name": dorm_name, "property_id": prop_id}))
    db.session.delete(prop)
    db.session.commit()
    
    # --- vvv เพิ่ม Real-Time Emit: ลบหอพักถาวร VVV ---
    socketio.emit('property_updated', {'id': prop_id, 'status': 'deleted_permanently'}, namespace='/')
    # --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---
    
    flash(f"ลบประกาศ '{dorm_name}' ออกจากระบบอย่างถาวรแล้ว", "success")
    return redirect(url_for('owner.trash'))

@bp.route("/property/<int:prop_id>/reviews")
@login_required
@owner_required
def property_reviews(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้", "danger")
        return redirect(url_for('owner.dashboard'))
    
    review_repo = current_app.extensions["container"]["review_repo"]
    
    reviews = review_repo.get_by_property_id(prop_id) 
    
    form = RequestReviewDeletionForm()
    
    return render_template("owner/property_reviews.html", prop=prop, reviews=reviews, form=form)


@bp.route("/review/<int:review_id>/request-delete", methods=["POST"])
@login_required
@owner_required
def request_delete_review(review_id: int):
    form = RequestReviewDeletionForm()
    review = current_app.extensions["container"]["review_repo"].get(review_id)
    if not review:
        flash("ไม่พบรีวิวที่ต้องการ", "danger")
        return redirect(url_for('owner.dashboard'))

    if form.validate_on_submit():
        review_mgmt_svc = current_app.extensions["container"]["review_management_service"]
        try:
            review_mgmt_svc.request_deletion(
                owner_id=current_user.ref_id,
                review_id=review_id,
                reason=form.reason.data
            )
            flash("ส่งคำร้องขอลบคอมเมนต์สำเร็จแล้ว", "success")
            
            # --- vvv เพิ่ม Real-Time Emit: ส่งคำร้องลบคอมเมนต์ VVV ---
            socketio.emit('admin_dashboard_update', {'type': 'review_queue_change'}, namespace='/')
            # --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---
            
        except (PermissionError, ValueError) as e:
            flash(str(e), "danger")
    else:
        flash("กรุณากรอกเหตุผลในการขอลบ (ขั้นต่ำ 10 ตัวอักษร)", "danger")

    return redirect(url_for('owner.property_reviews', prop_id=review.property_id))


@bp.route("/review-reports")
@login_required
@owner_required
def review_reports():
    report_repo = current_app.extensions["container"]["review_report_repo"]
    reports = report_repo.get_reports_by_owner(current_user.ref_id)
    return render_template("owner/review_reports.html", reports=reports)
