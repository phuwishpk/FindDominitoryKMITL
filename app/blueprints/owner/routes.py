from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from . import bp
from app.forms.owner import PropertyForm
from app.forms.upload import UploadImageForm, ReorderImagesForm
from app.models.property import Property, PropertyImage
from app.services.policies.property_policy import PropertyPolicy
from app.extensions import owner_required
from app.extensions import db

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
    if form.validate_on_submit():
        prop_svc = current_app.extensions["container"]["property_service"]
        prop = prop_svc.create(current_user.ref_id, {
            "dorm_name": form.dorm_name.data,
            "room_type": form.room_type.data,
            "contact_phone": form.contact_phone.data,
            "line_id": form.line_id.data,
            "facebook_url": form.facebook_url.data,
            "rent_price": form.rent_price.data,
            "water_rate": form.water_rate.data,
            "electric_rate": form.electric_rate.data,
            "deposit_amount": form.deposit_amount.data,
            "lat": form.lat.data, "lng": form.lng.data,
        })
        flash("บันทึกแล้ว")
        return redirect(url_for("owner.edit_property", prop_id=prop.id))
    return render_template("owner/form.html", form=form)

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

    if form.validate_on_submit() and "save_property" in request.form:
        prop_svc = current_app.extensions["container"]["property_service"]
        prop_svc.update(current_user.ref_id, prop_id, {
            "dorm_name": form.dorm_name.data,
            "room_type": form.room_type.data,
            "contact_phone": form.contact_phone.data,
            "line_id": form.line_id.data,
            "facebook_url": form.facebook_url.data,
            "rent_price": form.rent_price.data,
            "water_rate": form.water_rate.data,
            "electric_rate": form.electric_rate.data,
            "deposit_amount": form.deposit_amount.data,
            "lat": form.lat.data, "lng": form.lng.data,
        })
        flash("อัปเดตแล้ว")
        return redirect(url_for("owner.edit_property", prop_id=prop.id))

    return render_template("owner/form.html",
                           form=form, prop=prop,
                           upload_form=upload_form, reorder_form=reorder_form)

# ---- Upload / Delete / Reorder ----
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
            flash("อัปโหลดได้สูงสุด 6 รูป")
            return redirect(url_for("owner.edit_property", prop_id=prop.id))
        upload_svc = current_app.extensions["container"]["upload_service"]
        path = upload_svc.save_image(current_user.ref_id, form.image.data)
        max_pos = (PropertyImage.query.with_entities(func.max(PropertyImage.position))
                   .filter_by(property_id=prop.id).scalar()) or 0
        img = PropertyImage(property_id=prop.id, file_path=path, position=max_pos+1)
        db.session.add(img); db.session.commit()
        flash("อัปโหลดรูปสำเร็จ")
    else:
        flash("ตรวจสอบไฟล์ที่อัปโหลดอีกครั้ง")
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
    flash("ลบรูปแล้ว")
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
        flash("รูปแบบข้อมูลจัดเรียงไม่ถูกต้อง")
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
    flash("จัดเรียงรูปแล้ว")
    return redirect(url_for("owner.edit_property", prop_id=prop.id))
