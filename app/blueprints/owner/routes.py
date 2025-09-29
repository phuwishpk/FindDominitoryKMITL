from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from . import bp
from app.forms.owner import PropertyForm
from app.forms.upload import UploadImageForm, ReorderImagesForm
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
    return render_template("owner/dashboard.html", props=props)

@bp.route("/property/new", methods=["GET","POST"])
@login_required
@owner_required
def new_property():
    form = PropertyForm()
    all_amenities = Amenity.query.all()
    if form.validate_on_submit():
        prop_svc = current_app.extensions["container"]["property_service"]
        
        form_data = form.data.copy()
        form_data.pop('csrf_token', None)
        form_data['amenities'] = request.form.getlist('amenities')

        prop = prop_svc.create(current_user.ref_id, form_data)
        flash("สร้างประกาศสำเร็จแล้ว สามารถจัดการรูปภาพต่อได้เลย", "success")
        return redirect(url_for("owner.edit_property", prop_id=prop.id))
    return render_template("owner/form.html", form=form, all_amenities=all_amenities)

@bp.route("/property/<int:prop_id>/edit", methods=["GET","POST"])
@login_required
@owner_required
def edit_property(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return redirect(url_for("owner.dashboard"))
    
    form = PropertyForm(obj=prop)
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
        
        form_data = form.data.copy()
        form_data.pop('csrf_token', None)
        form_data['amenities'] = request.form.getlist('amenities')

        prop_svc.update(current_user.ref_id, prop_id, form_data)
        flash("อัปเดตข้อมูลแล้ว", "success")

        if "save_and_exit" in request.form:
            return redirect(url_for("owner.dashboard"))
        else: # save_property was clicked
            return redirect(url_for("owner.edit_property", prop_id=prop.id))

    return render_template("owner/form.html",
                           form=form, prop=prop,
                           upload_form=upload_form, reorder_form=reorder_form,
                           all_amenities=all_amenities,
                           approval_note=approval_note)

@bp.post("/property/<int:prop_id>/image")
@login_required
@owner_required
def upload_image(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return redirect(url_for("owner.dashboard"))
    form = UploadImageForm()
    if form.validate_on_submit() and form.image.data:
        count = PropertyImage.query.filter_by(property_id=prop.id).count()
        if count >= PropertyPolicy.MAX_IMAGES:
            flash(f"อัปโหลดได้สูงสุด {PropertyPolicy.MAX_IMAGES} รูป", "warning")
            return redirect(url_for("owner.edit_property", prop_id=prop.id))
        upload_svc = current_app.extensions["container"]["upload_service"]
        path = upload_svc.save_image(current_user.ref_id, form.image.data)
        max_pos = (PropertyImage.query.with_entities(func.max(PropertyImage.position))
                   .filter_by(property_id=prop.id).scalar()) or 0
        img = PropertyImage(property_id=prop.id, file_path=path, position=max_pos+1)
        db.session.add(img); db.session.commit()
        flash("อัปโหลดรูปสำเร็จ", "success")
    else:
        flash("ตรวจสอบไฟล์ที่อัปโหลดอีกครั้ง", "danger")
    return redirect(url_for("owner.edit_property", prop_id=prop.id))

@bp.post("/property/<int:prop_id>/image/<int:image_id>/delete")
@login_required
@owner_required
def delete_image(prop_id: int, image_id: int):
    prop = Property.query.get_or_404(prop_id)
    img = PropertyImage.query.get_or_404(image_id)
    if prop.owner_id != current_user.ref_id or img.property_id != prop.id:
        return redirect(url_for("owner.dashboard"))
    db.session.delete(img); db.session.commit()
    flash("ลบรูปแล้ว", "success")
    return redirect(url_for("owner.edit_property", prop_id=prop.id))

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
        return redirect(url_for("owner.edit_property", prop_id=prop.id))
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
    return redirect(url_for("owner.edit_property", prop_id=prop.id))

@bp.post("/property/<int:prop_id>/submit")
@login_required
@owner_required
def submit_for_approval(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.owner_id != current_user.ref_id:
        return redirect(url_for("owner.dashboard"))
    if prop.workflow_status == 'draft' or prop.workflow_status == 'rejected':
        approval_svc = current_app.extensions["container"]["approval_service"]
        approval_svc.submit(prop, current_user.ref_id)
        flash("ส่งประกาศเพื่อขออนุมัติแล้ว", "success")
    else:
        flash("ไม่สามารถส่งประกาศนี้ได้", "warning")
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