from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user

# --- vvv ส่วนที่แก้ไข vvv ---
from . import bp # เพิ่มบรรทัดนี้เพื่อ import 'bp' จาก __init__.py
# --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---

from app.forms.auth import OwnerRegisterForm, CombinedLoginForm
from app.models.user import Owner, Admin
from werkzeug.security import generate_password_hash

@bp.route("/owner/register", methods=["GET","POST"])
def owner_register():
    form = OwnerRegisterForm()
    if form.validate_on_submit():
        svc = current_app.extensions["container"]["auth_service"]
        svc.register_owner(form.data)
        flash("สมัครสมาชิกสำเร็จ! บัญชีของคุณจะถูกตรวจสอบโดยผู้ดูแลระบบก่อนเข้าใช้งาน", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/owner_register.html", form=form)

@bp.route("/login", methods=["GET","POST"])
def login():
    if not Admin.query.filter_by(username="admin").first():
        a = Admin(username="admin", password_hash=generate_password_hash("admin"), display_name="Administrator")
        from app.extensions import db
        db.session.add(a); db.session.commit()

    form = CombinedLoginForm(role=request.args.get("role","owner"))
    
    if form.validate_on_submit():
        role = form.role.data
        svc = current_app.extensions["container"]["auth_service"]
        
        if role == "owner":
            user_repo = current_app.extensions["container"]["user_repo"]
            owner = user_repo.get_owner_by_email(form.username.data)
            
            if owner and not owner.is_active:
                flash("บัญชีของคุณยังไม่ได้รับการอนุมัติจากผู้ดูแลระบบ", "warning")
            elif svc.verify_owner(form.username.data, form.password.data):
                svc.login_owner(owner)
                return redirect(url_for("owner.dashboard"))
            else:
                flash("ข้อมูลเข้าใช้งานไม่ถูกต้อง (Owner)")

        else: # Admin
            admin = svc.verify_admin(form.username.data, form.password.data)
            if admin:
                svc.login_admin(admin)
                return redirect(url_for("admin.dashboard"))
            flash("ข้อมูลเข้าใช้งานไม่ถูกต้อง (Admin)")
            
    return render_template("auth/login.html", form=form)

@bp.get("/logout")
@login_required
def logout():
    current_app.extensions["container"]["auth_service"].logout()
    return redirect(url_for("public.index"))