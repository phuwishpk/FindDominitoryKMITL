# phuwishpk/finddominitorykmitl/FindDominitoryKMITL-owner-improvements/app/blueprints/owner/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from . import bp
from app.forms.owner import PropertyForm
# 💡 แก้ไขการนำเข้า: นำเข้า EmptyForm ด้วย
from app.forms.upload import UploadImageForm, ReorderImagesForm, EmptyForm 
from app.models.property import Property, PropertyImage, Amenity
from app.models.approval import ApprovalRequest
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
    props = Property.query.filter_by(owner_id=current_user.ref_id).all()
    # 💡 เพิ่มการสร้าง EmptyForm และส่งไปยัง Template
    submit_form = EmptyForm()
    return render_template("owner/dashboard.html", props=props, submit_form=submit_form)


@bp.route("/property/new", methods=["GET","POST"])
@login_required
@owner_required
def new_property():
    form = PropertyForm()
    all_amenities = Amenity.query.all()
    
    # --- vvv ส่วนที่แก้ไข vvv ---
    # เตรียมตัวแปรสำหรับเก็บ amenities ที่เลือกไว้
    selected_amenities = []
    if request.method == "POST":
        # ถ้าเป็นการส่งข้อมูลมา ให้ดึงค่าที่เลือกไว้จากฟอร์ม
        selected_amenities = request.form.getlist('amenities')
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

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
        # --- vvv ส่วนที่แก้ไข vvv ---
        # ส่ง flash message พิเศษเพื่อสั่งให้ JavaScript ล้าง sessionStorage
        flash('clear_form_storage', 'script_command')
        # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
        return redirect(url_for("owner.dashboard"))
        
    return render_template("owner/form.html", 
        form=form, 
        all_amenities=all_amenities, 
        prop=None, 
        upload_form=UploadImageForm(), # เพิ่ม upload_form ที่นี่
        PropertyPolicy=PropertyPolicy,
        # --- vvv ส่วนที่แก้ไข vvv ---
        selected_amenities=selected_amenities
        # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
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

    # --- vvv ส่วนที่แก้ไข vvv ---
    # จัดการค่า amenities ที่ถูกเลือก
    if request.method == "POST":
        # ถ้าฟอร์มถูกส่งมา (และอาจจะไม่ผ่าน validation) ให้ใช้ค่าจากฟอร์ม
        selected_amenities = request.form.getlist('amenities')
    else:
        # ถ้าเป็นการโหลดหน้าครั้งแรก (GET) ให้ใช้ค่าจากฐานข้อมูล
        selected_amenities = [amenity.code for amenity in prop.amenities]
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

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
        
        # --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
        # 1. จัดการการลบรูปภาพ
        images_to_delete_str = request.form.get('images_to_delete', '')
        if images_to_delete_str:
            image_ids_to_delete = [int(id_) for id_ in images_to_delete_str.split(',') if id_.isdigit()]
            if image_ids_to_delete:
                # Query เพื่อความปลอดภัยว่ารูปที่ลบเป็นของ property นี้จริงๆ
                images_to_delete = db.session.query(PropertyImage).filter(
                    PropertyImage.property_id == prop_id,
                    PropertyImage.id.in_(image_ids_to_delete)
                ).all()
                for img in images_to_delete:
                    db.session.delete(img)
        # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

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
                           # --- vvv ส่วนที่แก้ไข vvv ---
                           selected_amenities=selected_amenities
                           # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
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

@bp.post("/property/<int:prop_id>/image/<int:image_id>/delete")
@login_required
@owner_required
def delete_image(prop_id: int, image_id: int):
    prop = Property.query.get_or_404(prop_id)
    img = PropertyImage.query.get_or_404(image_id)
    if prop.owner_id != current_user.ref_id or img.property_id != prop.id:
        return redirect(url_for("owner.dashboard"))
    db.session.delete(img)
    db.session.commit()
    flash("ลบรูปแล้ว", "success")
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
        # ใช้ submit_property ที่มีอยู่ใน ApprovalService
        approval_svc.submit_property(property_id=prop_id, owner_id=current_user.ref_id)
        flash("ส่งประกาศเพื่อขออนุมัติแล้ว", "success")
    except ValueError as e:
        flash(f"ไม่สามารถส่งประกาศได้: {str(e)}", "danger")
    
    return redirect(url_for("owner.dashboard"))

@bp.post("/property/<int:prop_id>/delete")
@login_required
@owner_required
def delete_property(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return redirect(url_for("owner.dashboard"))
    db.session.delete(prop)
    db.session.commit()
    flash("ลบประกาศแล้ว", "success")
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