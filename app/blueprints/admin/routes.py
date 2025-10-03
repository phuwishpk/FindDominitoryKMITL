from flask import render_template, redirect, url_for, flash, current_app, request, jsonify
from flask_login import login_required, current_user
from . import bp
from app.extensions import admin_required, db
from app.models.property import Property
from app.models.user import Owner
from app.forms.upload import EmptyForm
from app.forms.admin import RejectForm
from sqlalchemy import func
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
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
    approval_repo = current_app.extensions["container"]["approval_repo"]
    stats = {
        "total_owners": Owner.query.count(),
        "total_properties": Property.query.count(),
        "pending_properties": len(approval_repo.get_pending_properties())
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
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
    search_query = request.args.get('q', None)
    approval_repo = current_app.extensions["container"]["approval_repo"]
    pending_props = approval_repo.get_pending_properties(search_query=search_query)
    return render_template("admin/queue.html", properties=pending_props)

@bp.route("/property/<int:prop_id>/review", methods=["GET"])
@login_required
@admin_required
def review_property(prop_id: int):
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
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
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
    prop = Property.query.get_or_404(prop_id)
    owner = Owner.query.get(prop.owner_id)
    return render_template("admin/property_detail.html", prop=prop, owner=owner)

@bp.route("/property/<int:prop_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve(prop_id: int):
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
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
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
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
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
    page = request.args.get("page", 1, type=int)
    approval_service = current_app.extensions["container"]["approval_service"]
    log_data = approval_service.get_audit_logs(page=page)
    return render_template("admin/logs.html", **log_data)

@bp.route("/properties")
@login_required
@admin_required
def properties():
    # ... (โค้ดส่วนนี้เหมือนเดิม) ...
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get('q', None)
    
    prop_repo = current_app.extensions["container"]["property_repo"]
    pagination = prop_repo.list_all_paginated(search_query=search_query, page=page, per_page=15)
    
    return render_template("admin/properties.html", pagination=pagination, search_query=search_query)

# ส่วนที่เพิ่มเข้ามาใหม่
@bp.route("/owners")
@login_required
@admin_required
def owners():
    """
    แสดงรายการ Owner ทั้งหมด พร้อมค้นหาและแบ่งหน้า
    """
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get('q', None)

    user_repo = current_app.extensions["container"]["user_repo"]
    pagination = user_repo.list_all_owners_paginated(search_query=search_query, page=page, per_page=15)

    return render_template("admin/owners.html", pagination=pagination, search_query=search_query)