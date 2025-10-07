from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from . import bp
from app.extensions import admin_required, db
from app.models.property import Property
from app.models.user import Owner
from app.forms.upload import EmptyForm
from app.forms.admin import RejectForm, AdminEditOwnerForm
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from collections import OrderedDict

# ... (โค้ดส่วน index, dashboard, queue, review_property, approve, reject, logs, properties, delete_property ไม่มีการแก้ไข) ...
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
        "total_owners": Owner.query.count(),
        "total_properties": Property.query.count(),
        "pending_properties": len(approval_repo.get_pending_properties()),
        "pending_owners": len(user_repo.get_pending_owners())
    }
    pie_data_query = db.session.query(
        Property.road, func.count(Property.id).label('count')
    ).filter(Property.road != None, Property.road != '').group_by(Property.road).order_by(func.count(Property.id).desc()).limit(5).all()
    pie_chart = {
        "labels": [item[0] for item in pie_data_query],
        "data": [item[1] for item in pie_data_query]
    }
    line_chart_labels = []
    owner_data = OrderedDict()
    prop_data = OrderedDict()
    today = datetime.utcnow()
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i * 30)
        month_key = month_date.strftime("%b %Y")
        db_month_format = month_date.strftime("%Y-%m")
        line_chart_labels.append(month_key)
        owner_data[month_key] = Owner.query.filter(func.strftime('%Y-%m', Owner.created_at) == db_month_format).count()
        prop_data[month_key] = Property.query.filter(func.strftime('%Y-%m', Property.created_at) == db_month_format).count()
    line_chart = {
        "labels": line_chart_labels,
        "owners": list(owner_data.values()),
        "properties": list(prop_data.values())
    }
    return render_template("admin/dashboard.html", stats=stats, pie_chart=pie_chart, line_chart=line_chart)

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
    reject_form = RejectForm()
    approve_form = EmptyForm()
    return render_template("admin/review.html", 
                           prop=prop, 
                           owner=owner,
                           reject_form=reject_form,
                           approve_form=approve_form)

@bp.route("/property/<int:prop_id>/view")
@login_required
@admin_required
def view_property(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    owner = Owner.query.get(prop.owner_id)
    return render_template("admin/property_detail.html", prop=prop, owner=owner)

@bp.route("/property/<int:prop_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve(prop_id: int):
    approval_service = current_app.extensions["container"]["approval_service"]
    if not EmptyForm(request.form).validate_on_submit():
        flash("CSRF Token is invalid.", "danger")
        return redirect(url_for("admin.queue"))
    try:
        approval_service.approve_property(
            admin_id=current_user.ref_id, prop_id=prop_id, note=None
        )
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
        note = reject_form.note.data
        approval_service = current_app.extensions["container"]["approval_service"]
        try:
            approval_service.reject_property(
                admin_id=current_user.ref_id, prop_id=prop_id, note=note
            )
            flash("Property rejected successfully.", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("admin.queue"))
    
    flash("Please provide a reason for rejection.", "danger")
    return redirect(url_for("admin.review_property", prop_id=prop_id))


@bp.route("/logs")
@login_required
@admin_required
def logs():
    page = request.args.get("page", 1, type=int)
    approval_service = current_app.extensions["container"]["approval_service"]
    log_data = approval_service.get_audit_logs(page=page)
    return render_template("admin/logs.html", **log_data)

@bp.route("/properties")
@login_required
@admin_required
def properties():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get('q', None)
    
    prop_repo = current_app.extensions["container"]["property_repo"]
    pagination = prop_repo.list_all_paginated(search_query=search_query, page=page, per_page=15)
    
    return render_template("admin/properties.html", pagination=pagination, search_query=search_query)

@bp.route("/property/<int:prop_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_property(prop_id: int):
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for('admin.properties'))

    prop_repo = current_app.extensions["container"]["property_repo"]
    prop = prop_repo.get(prop_id)

    if prop:
        prop_repo.delete(prop)
        flash(f"ลบหอพัก '{prop.dorm_name}' (ID: {prop_id}) เรียบร้อยแล้ว", "success")
    else:
        flash("ไม่พบหอพักที่ต้องการลบ", "warning")

    return redirect(url_for('admin.properties'))

@bp.route("/owners")
@login_required
@admin_required
def owners():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get('q', None)
    user_repo = current_app.extensions["container"]["user_repo"]
    pagination = user_repo.list_all_owners_paginated(search_query=search_query, page=page, per_page=15)
    
    delete_form = EmptyForm()
    return render_template("admin/owners.html", pagination=pagination, search_query=search_query, delete_form=delete_form)

# --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
@bp.route("/owners/<int:owner_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_owner(owner_id: int):
    owner = Owner.query.get_or_404(owner_id)
    form = AdminEditOwnerForm(obj=owner)

    if form.validate_on_submit():
        # ตรวจสอบว่าอีเมลมีการเปลี่ยนแปลงและไม่ซ้ำกับคนอื่น
        if owner.email != form.email.data and Owner.query.filter_by(email=form.email.data).first():
            flash('อีเมลนี้มีผู้ใช้งานแล้ว', 'danger')
            return render_template("admin/edit_owner.html", form=form, owner=owner)
            
        owner.full_name_th = form.full_name_th.data
        owner.email = form.email.data
        owner.phone = form.phone.data
        owner.is_active = form.is_active.data
        db.session.commit()
        flash(f"อัปเดตข้อมูลของ '{owner.full_name_th}' เรียบร้อยแล้ว", "success")
        return redirect(url_for('admin.owners'))

    return render_template("admin/edit_owner.html", form=form, owner=owner)
# --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---

@bp.route("/owners/<int:owner_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_owner(owner_id: int):
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.owners'))

    owner = Owner.query.get_or_404(owner_id)
    owner.deleted_at = datetime.utcnow()
    db.session.commit()
    
    flash(f"ย้ายข้อมูล Owner '{owner.full_name_th}' ไปยังถังขยะแล้ว", "success")
    return redirect(url_for('admin.owners'))

# --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
@bp.route("/owners/trash")
@login_required
@admin_required
def deleted_owners():
    page = request.args.get("page", 1, type=int)
    user_repo = current_app.extensions["container"]["user_repo"]
    pagination = user_repo.get_deleted_owners_paginated(page=page)
    
    restore_form = EmptyForm()
    delete_form = EmptyForm()
    
    return render_template("admin/deleted_owners.html", 
                           pagination=pagination, 
                           restore_form=restore_form, 
                           delete_form=delete_form)

@bp.route("/owners/<int:owner_id>/restore", methods=["POST"])
@login_required
@admin_required
def restore_owner(owner_id: int):
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.deleted_owners'))

    owner = Owner.query.get_or_404(owner_id)
    owner.deleted_at = None
    db.session.commit()
    flash(f"กู้คืนข้อมูล Owner '{owner.full_name_th}' สำเร็จ", "success")
    return redirect(url_for('admin.deleted_owners'))

@bp.route("/owners/<int:owner_id>/permanent_delete", methods=["POST"])
@login_required
@admin_required
def permanently_delete_owner(owner_id: int):
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for('admin.deleted_owners'))
    
    user_repo = current_app.extensions["container"]["user_repo"]
    owner = user_repo.get_owner_by_id(owner_id)
    if owner:
        # อาจจะต้องลบข้อมูลอื่นๆ ที่เกี่ยวข้องก่อน เช่น Property
        Property.query.filter_by(owner_id=owner.id).delete()
        user_repo.permanently_delete_owner(owner)
        flash(f"ลบข้อมูล Owner '{owner.full_name_th}' ออกจากระบบอย่างถาวรแล้ว", "success")
    else:
        flash("ไม่พบข้อมูล Owner", "warning")
        
    return redirect(url_for('admin.deleted_owners'))
# --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---

# ... (โค้ดส่วน owner_queue, review_owner, approve_owner, reject_owner ไม่มีการแก้ไข) ...
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
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for("admin.owner_queue"))
    
    user_repo = current_app.extensions["container"]["user_repo"]
    owner = user_repo.get_owner_by_id(owner_id)
    if owner and owner.approval_status == 'pending':
        owner.is_active = True
        owner.approval_status = 'approved'
        user_repo.save_owner(owner)
        flash(f"อนุมัติบัญชีของ {owner.full_name_th} สำเร็จ", "success")
    else:
        flash("ไม่สามารถดำเนินการได้", "danger")
    return redirect(url_for("admin.owner_queue"))

@bp.route("/owners/<int:owner_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_owner(owner_id: int):
    form = EmptyForm()
    if not form.validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for("admin.owner_queue"))

    user_repo = current_app.extensions["container"]["user_repo"]
    owner = user_repo.get_owner_by_id(owner_id)
    if owner and owner.approval_status == 'pending':
        owner.is_active = False
        owner.approval_status = 'rejected'
        user_repo.save_owner(owner)
        flash(f"ปฏิเสธบัญชีของ {owner.full_name_th} สำเร็จ", "success")
    else:
        flash("ไม่สามารถดำเนินการได้", "danger")
    return redirect(url_for("admin.owner_queue"))