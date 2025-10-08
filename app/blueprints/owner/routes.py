# phuwishpk/finddominitorykmitl/FindDominitoryKMITL-owner-improvements/app/blueprints/owner/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
# --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
from datetime import datetime
# --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
from . import bp
from app.forms.owner import PropertyForm
from app.forms.upload import UploadImageForm, ReorderImagesForm, EmptyForm 
from app.models.property import Property, PropertyImage, Amenity
from app.models.approval import ApprovalRequest, AuditLog # 💡 แก้ไข: นำเข้า AuditLog
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
    # --- vvv ส่วนที่แก้ไข: กรองรายการที่ยังไม่ถูกลบ vvv ---
    props = Property.query.filter_by(owner_id=current_user.ref_id, deleted_at=None).all()
    delete_form = EmptyForm() # 💡 เพิ่ม: สร้างฟอร์มสำหรับปุ่มลบ
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
    submit_form = EmptyForm()
    return render_template("owner/dashboard.html", props=props, submit_form=submit_form, delete_form=delete_form) # 💡 เพิ่ม: ส่ง delete_form


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
            form.room_type.data = 'อื่นๆ'
            form.other_room_type.data = prop.room_type

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
        return redirect(url_for("owner.dashboard"))
    form = ReorderImagesForm()
    if not form.validate_on_submit():
        flash("รูปแบบข้อมูลจัดเรียงไม่ถูกต้อง", "danger")
        return redirect(url_for("owner.edit_property", prop_id=prop.id, tab="images"))
    mapping = {}
    for field in form.positions:
        try:
            img_id, pos = field.data.split(":")
            mapping[int(img_id)] = int(pos)
        except Exception:
            continue
    imgs = PropertyImage.query.filter(
        PropertyImage.id.in_(mapping.keys()),
        PropertyImage.property_id == prop.id
    ).all()
    for im in imgs:
        im.position = mapping.get(im.id, im.position)
    db.session.commit()
    flash("จัดเรียงรูปแล้ว", "success")
    return redirect(url_for("owner.edit_property", prop_id=prop.id, tab="images"))

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
    return redirect(url_for("owner.dashboard"))

# --- vvv ส่วนที่เพิ่มเข้ามาใหม่: Trash System vvv ---

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
    flash(f"ย้ายประกาศ '{prop.dorm_name}' ไปยังถังขยะแล้ว", "success")
    return redirect(url_for('owner.dashboard'))

@bp.route("/trash")
@login_required
@owner_required
def trash():
    page = request.args.get("page", 1, type=int)
    per_page = 10 
    
    # ดึงเฉพาะรายการที่ถูกลบของ owner คนปัจจุบัน
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
    flash(f"ลบประกาศ '{dorm_name}' ออกจากระบบอย่างถาวรแล้ว", "success")
    return redirect(url_for('owner.trash'))

# --- ^^^ สิ้นสุดการแก้ไข ^^^ ---