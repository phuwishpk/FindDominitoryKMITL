from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from . import bp
from app.extensions import admin_required, db
from app.models.property import Property, Amenity
from app.models.user import Owner
from app.models.approval import AuditLog
from app.forms.upload import EmptyForm
from app.forms.admin import RejectForm, AdminEditOwnerForm, AmenityForm, AdminEditPropertyForm
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from collections import OrderedDict

@bp.route("/")
@login_required
@admin_required
def index():
    return redirect(url_for("admin.dashboard"))

@bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    approval_repo = current_app.extensions["container"]["approval_repo"]
    user_repo = current_app.extensions["container"]["user_repo"]

    stats = {
        "total_owners": Owner.query.filter(Owner.deleted_at.is_(None)).count(),
        "total_properties": Property.query.filter(Property.deleted_at.is_(None)).count(),
        "pending_properties": len(approval_repo.get_pending_properties()),
        "pending_owners": len(user_repo.get_pending_owners())
    }
    pie_data_query = db.session.query(
        Property.road, func.count(Property.id).label('count')
    ).filter(Property.road != None, Property.road != '').group_by(Property.road).order_by(func.count(Property.id).desc()).limit(5).all()
    pie_chart = { "labels": [item[0] for item in pie_data_query], "data": [item[1] for item in pie_data_query] }
    line_chart_labels, owner_data, prop_data = [], OrderedDict(), OrderedDict()
    today = datetime.utcnow()
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i * 30)
        month_key, db_month_format = month_date.strftime("%b %Y"), month_date.strftime("%Y-%m")
        line_chart_labels.append(month_key)
        owner_data[month_key] = Owner.query.filter(func.strftime('%Y-%m', Owner.created_at) == db_month_format).count()
        prop_data[month_key] = Property.query.filter(func.strftime('%Y-%m', Property.created_at) == db_month_format).count()
    line_chart = { "labels": line_chart_labels, "owners": list(owner_data.values()), "properties": list(prop_data.values()) }
    return render_template("admin/dashboard.html", stats=stats, pie_chart=pie_chart, line_chart=line_chart)

# --- Property Approval Workflow ---
@bp.route("/queue")
@login_required
@admin_required
def queue():
    search_query = request.args.get('q', None)
    approval_repo = current_app.extensions["container"]["approval_repo"]
    pending_props = approval_repo.get_pending_properties(search_query=search_query)
    return render_template("admin/queue.html", properties=pending_props)

@bp.route("/property/<int:prop_id>/review", methods=["GET"])
@login_required
@admin_required
def review_property(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    if prop.workflow_status not in ['submitted']:
        flash("This item is not in the approval queue.", "warning")
        return redirect(url_for("admin.queue"))
    owner = Owner.query.get(prop.owner_id)
    reject_form, approve_form = RejectForm(), EmptyForm()
    return render_template("admin/review.html", prop=prop, owner=owner, reject_form=reject_form, approve_form=approve_form)

@bp.route("/property/<int:prop_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve(prop_id: int):
    if not EmptyForm(request.form).validate_on_submit():
        flash("CSRF Token is invalid.", "danger")
        return redirect(url_for("admin.queue"))
    approval_service = current_app.extensions["container"]["approval_service"]
    try:
        approval_service.approve_property(admin_id=current_user.ref_id, prop_id=prop_id, note=None)
        flash("Property approved successfully.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.queue"))

@bp.route("/property/<int:prop_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject(prop_id: int):
    reject_form = RejectForm()
    if reject_form.validate_on_submit():
        approval_service = current_app.extensions["container"]["approval_service"]
        try:
            approval_service.reject_property(admin_id=current_user.ref_id, prop_id=prop_id, note=reject_form.note.data)
            flash("Property rejected successfully.", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("admin.queue"))
    flash("Please provide a reason for rejection.", "danger")
    return redirect(url_for("admin.review_property", prop_id=prop_id))

# --- Property Management & Trash Can ---
@bp.route("/properties")
@login_required
@admin_required
def properties():
    page, search_query = request.args.get("page", 1, type=int), request.args.get('q', None)
    prop_repo = current_app.extensions["container"]["property_repo"]
    pagination = prop_repo.list_all_paginated(search_query=search_query, page=page, per_page=15)
    delete_form = EmptyForm()
    return render_template("admin/properties.html", pagination=pagination, search_query=search_query, delete_form=delete_form)

@bp.route("/property/<int:prop_id>/view")
@login_required
@admin_required
def view_property(prop_id: int):
    prop = Property.query.get(prop_id)
    if not prop:
        flash(f"ไม่พบข้อมูลหอพัก ID: {prop_id} (อาจถูกลบออกจากระบบอย่างถาวรแล้ว)", "warning")
        return redirect(url_for('admin.properties'))
    owner = Owner.query.get(prop.owner_id)
    return render_template("admin/property_detail.html", prop=prop, owner=owner)

@bp.route("/property/<int:prop_id>/admin_edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_property(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    form = AdminEditPropertyForm(obj=prop)
    if form.validate_on_submit():
        prop.dorm_name = form.dorm_name.data
        prop.workflow_status = form.workflow_status.data
        db.session.add(AuditLog.log("admin", current_user.ref_id, "admin_edit_property", prop_id))
        db.session.commit()
        flash(f"อัปเดตข้อมูลหอพัก '{prop.dorm_name}' เรียบร้อยแล้ว", "success")
        return redirect(url_for('admin.properties'))
    return render_template("admin/edit_property.html", prop=prop, form=form)

@bp.route("/property/<int:prop_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_property(prop_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for('admin.properties'))
    prop = Property.query.get_or_404(prop_id)
    prop.deleted_at = datetime.utcnow()
    db.session.add(AuditLog.log("admin", current_user.ref_id, "soft_delete_property", prop_id))
    db.session.commit()
    flash(f"ย้ายหอพัก '{prop.dorm_name}' ไปยังถังขยะแล้ว", "success")
    return redirect(url_for('admin.properties'))

@bp.route("/properties/trash")
@login_required
@admin_required
def deleted_properties():
    page = request.args.get("page", 1, type=int)
    prop_repo = current_app.extensions["container"]["property_repo"]
    pagination = prop_repo.get_deleted_properties_paginated(page=page, per_page=15)
    restore_form, delete_form = EmptyForm(), EmptyForm()
    return render_template("admin/deleted_properties.html", pagination=pagination, restore_form=restore_form, delete_form=delete_form)

@bp.route("/property/<int:prop_id>/restore", methods=["POST"])
@login_required
@admin_required
def restore_property(prop_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.deleted_properties'))
    prop = Property.query.get_or_404(prop_id)
    prop.deleted_at = None
    db.session.add(AuditLog.log("admin", current_user.ref_id, "restore_property", prop_id))
    db.session.commit()
    flash(f"กู้คืนหอพัก '{prop.dorm_name}' สำเร็จ", "success")
    return redirect(url_for('admin.deleted_properties'))

@bp.route("/property/<int:prop_id>/permanent_delete", methods=["POST"])
@login_required
@admin_required
def permanently_delete_property(prop_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.deleted_properties'))
    prop_repo = current_app.extensions["container"]["property_repo"]
    prop = prop_repo.get(prop_id)
    if prop:
        dorm_name = prop.dorm_name
        db.session.add(AuditLog.log("admin", current_user.ref_id, "permanent_delete_property", meta={"deleted_name": dorm_name, "property_id": prop_id}))
        prop_repo.delete(prop)
        flash(f"ลบหอพัก '{dorm_name}' ออกจากระบบอย่างถาวรแล้ว", "success")
    else:
        flash("ไม่พบหอพักที่ต้องการลบ", "warning")
    return redirect(url_for('admin.deleted_properties'))

# --- Owner Management & Trash Can ---
@bp.route("/owners")
@login_required
@admin_required
def owners():
    page, search_query = request.args.get("page", 1, type=int), request.args.get('q', None)
    user_repo = current_app.extensions["container"]["user_repo"]
    pagination = user_repo.list_all_owners_paginated(search_query=search_query, page=page, per_page=15)
    delete_form = EmptyForm()
    return render_template("admin/owners.html", pagination=pagination, search_query=search_query, delete_form=delete_form)

@bp.route("/owners/<int:owner_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_owner(owner_id: int):
    owner = Owner.query.get_or_404(owner_id)
    form = AdminEditOwnerForm(obj=owner)
    if form.validate_on_submit():
        if owner.email != form.email.data and Owner.query.filter_by(email=form.email.data).first():
            flash('อีเมลนี้มีผู้ใช้งานแล้ว', 'danger')
            return render_template("admin/edit_owner.html", form=form, owner=owner)
        owner.full_name_th, owner.email, owner.phone, owner.is_active = form.full_name_th.data, form.email.data, form.phone.data, form.is_active.data
        db.session.add(AuditLog.log("admin", current_user.ref_id, "admin_edit_owner", meta={"owner_id": owner_id, "owner_name": owner.full_name_th}))
        db.session.commit()
        flash(f"อัปเดตข้อมูลของ '{owner.full_name_th}' เรียบร้อยแล้ว", "success")
        return redirect(url_for('admin.owners'))
    return render_template("admin/edit_owner.html", form=form, owner=owner)

@bp.route("/owners/queue")
@login_required
@admin_required
def owner_queue():
    user_repo = current_app.extensions["container"]["user_repo"]
    pending_owners = user_repo.get_pending_owners()
    return render_template("admin/owner_queue.html", pending_owners=pending_owners)

@bp.route("/owners/<int:owner_id>/review")
@login_required
@admin_required
def review_owner(owner_id: int):
    user_repo = current_app.extensions["container"]["user_repo"]
    owner = user_repo.get_owner_by_id(owner_id)
    return render_template("admin/review_owner.html", owner=owner)

@bp.route("/owners/<int:owner_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_owner(owner_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for("admin.owner_queue"))
    user_repo, owner = current_app.extensions["container"]["user_repo"], user_repo.get_owner_by_id(owner_id)
    if owner and owner.approval_status == 'pending':
        owner.is_active, owner.approval_status = True, 'approved'
        db.session.add(AuditLog.log("admin", current_user.ref_id, "approve_owner", meta={"owner_id": owner_id, "owner_name": owner.full_name_th}))
        user_repo.save_owner(owner)
        flash(f"อนุมัติบัญชีของ {owner.full_name_th} สำเร็จ", "success")
    else:
        flash("ไม่สามารถดำเนินการได้", "danger")
    return redirect(url_for("admin.owner_queue"))

@bp.route("/owners/<int:owner_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_owner(owner_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for("admin.owner_queue"))
    user_repo, owner = current_app.extensions["container"]["user_repo"], user_repo.get_owner_by_id(owner_id)
    if owner and owner.approval_status == 'pending':
        owner.is_active, owner.approval_status = False, 'rejected'
        db.session.add(AuditLog.log("admin", current_user.ref_id, "reject_owner", meta={"owner_id": owner_id, "owner_name": owner.full_name_th}))
        user_repo.save_owner(owner)
        flash(f"ปฏิเสธบัญชีของ {owner.full_name_th} สำเร็จ", "success")
    else:
        flash("ไม่สามารถดำเนินการได้", "danger")
    return redirect(url_for("admin.owner_queue"))

@bp.route("/owners/<int:owner_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_owner(owner_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.owners'))
    owner = Owner.query.get_or_404(owner_id)
    owner.deleted_at = datetime.utcnow()
    db.session.add(AuditLog.log("admin", current_user.ref_id, "soft_delete_owner", meta={"owner_id": owner_id, "owner_name": owner.full_name_th}))
    db.session.commit()
    flash(f"ย้ายข้อมูล Owner '{owner.full_name_th}' ไปยังถังขยะแล้ว", "success")
    return redirect(url_for('admin.owners'))

@bp.route("/owners/trash")
@login_required
@admin_required
def deleted_owners():
    page = request.args.get("page", 1, type=int)
    user_repo = current_app.extensions["container"]["user_repo"]
    pagination = user_repo.get_deleted_owners_paginated(page=page)
    restore_form, delete_form = EmptyForm(), EmptyForm()
    return render_template("admin/deleted_owners.html", pagination=pagination, restore_form=restore_form, delete_form=delete_form)

@bp.route("/owners/<int:owner_id>/restore", methods=["POST"])
@login_required
@admin_required
def restore_owner(owner_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.deleted_owners'))
    owner = Owner.query.get_or_404(owner_id)
    owner.deleted_at = None
    db.session.add(AuditLog.log("admin", current_user.ref_id, "restore_owner", meta={"owner_id": owner_id, "owner_name": owner.full_name_th}))
    db.session.commit()
    flash(f"กู้คืนข้อมูล Owner '{owner.full_name_th}' สำเร็จ", "success")
    return redirect(url_for('admin.deleted_owners'))

@bp.route("/owners/<int:owner_id>/permanent_delete", methods=["POST"])
@login_required
@admin_required
def permanently_delete_owner(owner_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.deleted_owners'))
    user_repo = current_app.extensions["container"]["user_repo"]
    owner = user_repo.get_owner_by_id(owner_id)
    if owner:
        owner_name = owner.full_name_th
        Property.query.filter_by(owner_id=owner.id).delete(synchronize_session=False)
        db.session.add(AuditLog.log("admin", current_user.ref_id, "permanent_delete_owner", meta={"deleted_name": owner_name, "owner_id": owner_id}))
        user_repo.permanently_delete_owner(owner)
        flash(f"ลบข้อมูล Owner '{owner_name}' และหอพักที่เกี่ยวข้องทั้งหมดออกจากระบบอย่างถาวรแล้ว", "success")
    else:
        flash("ไม่พบข้อมูล Owner", "warning")
    return redirect(url_for('admin.deleted_owners'))

# --- Master Data Management (Amenities) ---
@bp.route("/amenities", methods=["GET"])
@login_required
@admin_required
def amenities():
    amenities_list = Amenity.query.order_by(Amenity.label_th.asc()).all()
    form, delete_form = AmenityForm(), EmptyForm()
    return render_template("admin/amenities.html", amenities=amenities_list, form=form, delete_form=delete_form)

@bp.route("/amenities/add", methods=["POST"])
@login_required
@admin_required
def add_amenity():
    form = AmenityForm()
    if form.validate_on_submit():
        code = form.code.data.lower().strip()
        if Amenity.query.filter_by(code=code).first():
            flash(f"Code '{code}' นี้มีอยู่ในระบบแล้ว", 'danger')
        else:
            new_amenity = Amenity(code=code, label_th=form.label_th.data, label_en=form.label_en.data)
            db.session.add(new_amenity)
            db.session.add(AuditLog.log("admin", current_user.ref_id, "add_amenity", meta={"code": code, "label_th": new_amenity.label_th}))
            db.session.commit()
            flash('เพิ่มสิ่งอำนวยความสะดวกใหม่เรียบร้อยแล้ว', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('admin.amenities'))

@bp.route("/amenities/<int:amenity_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_amenity(amenity_id: int):
    amenity, form = Amenity.query.get_or_404(amenity_id), AmenityForm()
    if form.validate_on_submit():
        amenity.label_th, amenity.label_en = form.label_th.data, form.label_en.data
        db.session.add(AuditLog.log("admin", current_user.ref_id, "edit_amenity", meta={"code": amenity.code, "label_th": amenity.label_th}))
        db.session.commit()
        flash(f"แก้ไข '{amenity.label_th}' เรียบร้อยแล้ว", "success")
    else:
        flash('ข้อมูลที่ส่งมาไม่ถูกต้อง', 'danger')
    return redirect(url_for('admin.amenities'))

@bp.route("/amenities/<int:amenity_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_amenity(amenity_id: int):
    if not EmptyForm().validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.amenities'))
    amenity = Amenity.query.get_or_404(amenity_id)
    label_th, code = amenity.label_th, amenity.code
    db.session.add(AuditLog.log("admin", current_user.ref_id, "delete_amenity", meta={"code": code, "label_th": label_th}))
    db.session.delete(amenity)
    db.session.commit()
    flash(f"ลบ '{label_th}' ออกจากระบบเรียบร้อยแล้ว", "success")
    return redirect(url_for('admin.amenities'))

# --- Audit Logs ---
@bp.route("/logs")
@login_required
@admin_required
def logs():
    page = request.args.get("page", 1, type=int)
    approval_repo = current_app.extensions["container"]["approval_repo"]
    pagination = approval_repo.list_logs(page=page)
    return render_template("admin/logs.html", pagination=pagination)