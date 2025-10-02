from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from . import bp
from app.extensions import admin_required
from app.models.property import Property
from app.models.user import Owner 
from app.forms.upload import EmptyForm 
from app.forms.admin import RejectForm 


@bp.route("/queue")
@login_required
@admin_required
def queue():
    """
    แสดงรายการที่รออนุมัติ
    """
    approval_repo = current_app.extensions["container"]["approval_repo"]
    # 💡 ใช้ get_pending_properties()
    pending_props = approval_repo.get_pending_properties()
    return render_template("admin/queue.html", properties=pending_props)


# 💡 Route ใหม่: สำหรับดูรายละเอียดและ Map
@bp.route("/property/<int:prop_id>/review", methods=["GET"])
@login_required
@admin_required
def review_property(prop_id: int):
    """แสดงรายละเอียดของประกาศเพื่อตรวจสอบ (พร้อม Map)"""
    prop = Property.query.get_or_404(prop_id)
    
    # ตรวจสอบสถานะก่อนแสดง
    if prop.workflow_status not in ['submitted']: # ตรวจสอบเฉพาะ submitted
        flash("รายการนี้ไม่ได้อยู่ในคิวรออนุมัติ", "warning")
        return redirect(url_for("admin.queue"))
    
    # ดึงข้อมูลที่จำเป็น
    owner = Owner.query.get(prop.owner_id)
    reject_form = RejectForm()
    approve_form = EmptyForm()
    
    return render_template("admin/review.html", 
                           prop=prop, 
                           owner=owner,
                           reject_form=reject_form,
                           approve_form=approve_form)


@bp.route("/property/<int:prop_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve(prop_id: int):
    approval_service = current_app.extensions["container"]["approval_service"]
    if not EmptyForm(request.form).validate_on_submit():
        flash("CSRF Token ไม่ถูกต้อง", "danger")
        return redirect(url_for("admin.queue"))
    
    try:
        approval_service.approve_property(
            admin_id=current_user.ref_id, prop_id=prop_id, note=None 
        )
        flash("อนุมัติรายการสำเร็จ", "success")
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
            flash("ปฏิเสธรายการสำเร็จ", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("admin.queue"))
    
    # 💡 ถ้า Validate ไม่ผ่าน ให้ Redirect กลับไปหน้า Review เพื่อแสดง Error
    flash("กรุณาระบุเหตุผลในการปฏิเสธ", "danger")
    return redirect(url_for("admin.review_property", prop_id=prop_id))


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