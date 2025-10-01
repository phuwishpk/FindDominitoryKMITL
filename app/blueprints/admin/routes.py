from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from . import bp
from app.extensions import admin_required
from app.models.property import Property, PropertyImage # 💡 เพิ่ม PropertyImage สำหรับใช้ใน review.html
from app.models.user import Owner, Admin # 💡 แก้ไข: เปลี่ยนจาก 'User' เป็น 'Owner' และ 'Admin'
# 💡 นำเข้าฟอร์มที่จำเป็น
from app.forms.upload import EmptyForm # ใช้สำหรับ CSRF token ในฟอร์ม Approve
from app.forms.admin import RejectForm # (สมมติว่าคุณได้สร้างไฟล์ forms/admin.py ไว้แล้วตามคำแนะนำก่อนหน้า)

@bp.get("/queue")
@login_required
@admin_required
def queue():
    """
    แสดงรายการที่รออนุมัติ
    """
    approval_repo = current_app.extensions["container"]["approval_repo"]
    # 💡 ใช้ get_pending_properties()
    pending_props = approval_repo.get_pending_properties()
    return render_template("admin/queue.html", props=pending_props)

# 💡 เพิ่ม Route สำหรับดูรายละเอียด (Review)
@bp.route("/property/<int:prop_id>/review", methods=["GET"])
@login_required
@admin_required
def review_property(prop_id: int):
    prop = Property.query.get_or_404(prop_id)
    
    # 💡 ใช้ Owner เพื่อดึงข้อมูลเจ้าของหอพัก
    owner = Owner.query.get(prop.owner_id) 
    
    # ดึงรูปภาพทั้งหมดของหอพัก
    images = prop.images 
    
    # สร้างฟอร์มสำหรับเหตุผลในการปฏิเสธ
    reject_form = RejectForm()
    
    # สร้างฟอร์มว่างสำหรับปุ่มอนุมัติ (หากไม่ต้องการส่งข้อมูลอื่น)
    approve_form = EmptyForm() 
    
    return render_template("admin/review.html", 
                           prop=prop, 
                           owner=owner,
                           images=images,
                           reject_form=reject_form,
                           approve_form=approve_form)


@bp.route("/property/<int:prop_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve(prop_id: int):
    """
    อนุมัติ Property
    """
    # 💡 ตรวจสอบ CSRF token ก่อนดำเนินการ
    if not EmptyForm(request.form).validate_on_submit():
        flash("CSRF Token ไม่ถูกต้อง", "danger")
        return redirect(url_for("admin.queue"))

    approval_service = current_app.extensions["container"]["approval_service"]
    try:
        approval_service.approve_property(
            admin_id=current_user.ref_id, prop_id=prop_id, note=None
        )
        flash(f"อนุมัติประกาศ '{prop_id}' เรียบร้อยแล้ว", "success")
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
    reject_form = RejectForm()
    
    if reject_form.validate_on_submit():
        note = reject_form.note.data
        approval_service = current_app.extensions["container"]["approval_service"]
        try:
            approval_service.reject_property(
                admin_id=current_user.ref_id, prop_id=prop_id, note=note
            )
            flash(f"ปฏิเสธประกาศ '{prop_id}' เรียบร้อยแล้ว", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("admin.queue"))
    
    # หากฟอร์มไม่ถูกต้อง ให้กลับไปหน้า Review พร้อมแสดงข้อผิดพลาด
    flash("กรุณาระบุเหตุผลในการไม่อนุมัติ", "danger")
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