from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from . import bp
from app.extensions import admin_required

@bp.route("/queue")
@login_required
@admin_required
def queue():
    """
    แสดงรายการที่รออนุมัติ
    """
    approval_repo = current_app.extensions["container"]["approval_repo"]
    pending_props = approval_repo.get_pending_properties()
    return render_template("admin/queue.html", properties=pending_props)


@bp.route("/property/<int:prop_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve(prop_id: int):
    """
    อนุมัติ Property
    """
    approval_service = current_app.extensions["container"]["approval_service"]
    note = request.form.get("note")
    try:
        approval_service.approve_property(
            admin_id=current_user.ref_id, prop_id=prop_id, note=note
        )
        flash("อนุมัติรายการสำเร็จ")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.queue"))


@bp.route("/property/<int:prop_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject(prop_id: int):
    """
    ปฏิเสธ Property
    """
    approval_service = current_app.extensions["container"]["approval_service"]
    note = request.form.get("note")
    try:
        approval_service.reject_property(
            admin_id=current_user.ref_id, prop_id=prop_id, note=note
        )
        flash("ปฏิเสธรายการสำเร็จ")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.queue"))


@bp.route("/logs")
@login_required
@admin_required
def logs():
    """
    แสดง AuditLog แบบ paginate
    """
    page = request.args.get("page", 1, type=int)
    approval_service = current_app.extensions["container"]["approval_service"]
    log_data = approval_service.get_audit_logs(page=page)
    return render_template("admin/logs.html", **log_data)