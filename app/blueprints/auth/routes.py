from flask import render_template, redirect, url_for, flash, current_app, request, session
from flask_login import login_required, current_user
from . import bp
from app.forms.auth import OwnerRegisterForm, CombinedLoginForm
from app.forms.upload import EmptyForm
from app.models.user import Owner, Admin
from werkzeug.security import generate_password_hash

@bp.route("/owner/register", methods=["GET","POST"])
def owner_register():
    form = OwnerRegisterForm()
    if form.validate_on_submit():
        svc = current_app.extensions["container"]["auth_service"]
        new_owner = svc.register_owner(form.data)
        
        session['toast_message'] = {
            'message': f"สมัครสมาชิกสำเร็จ! บัญชีของคุณ '{new_owner.full_name_th}' กำลังรอการอนุมัติ",
            'category': 'success'
        }
        session['toast_admin_notification'] = {
            'message': f"มี Owner ใหม่สมัครเข้ามา: {new_owner.full_name_th}",
            'category': 'info'
        }
        
        return redirect(url_for("auth.login"))
        
    return render_template("auth/owner_register.html", form=form)

@bp.route("/login", methods=["GET","POST"])
def login():
    if not Admin.query.filter_by(username="admin").first():
        a = Admin(username="admin", password_hash=generate_password_hash("admin"), display_name="Administrator")
        from app.extensions import db
        db.session.add(a); db.session.commit()

    form = CombinedLoginForm()
    
    if form.validate_on_submit():
        username_or_email = form.username.data
        password = form.password.data
        svc = current_app.extensions["container"]["auth_service"]
        user_repo = current_app.extensions["container"]["user_repo"]

        admin = svc.verify_admin(username_or_email, password)
        if admin:
            svc.login_admin(admin)
            return redirect(url_for("admin.dashboard"))

        owner = user_repo.get_owner_by_email(username_or_email)
        
        if owner:
            is_verified_and_active = svc.verify_owner(username_or_email, password)
            if is_verified_and_active:
                svc.login_owner(owner)
                return redirect(url_for("owner.dashboard"))
            
            if not owner.is_active: 
                flash("บัญชีของคุณยังไม่ได้รับการอนุมัติจากผู้ดูแลระบบ", "warning")
                return render_template("auth/login.html", form=form)

        flash("ข้อมูลเข้าใช้งานไม่ถูกต้อง กรุณาตรวจสอบชื่อผู้ใช้/อีเมล และรหัสผ่าน", "danger")
            
    return render_template("auth/login.html", form=form)

@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    form = EmptyForm()
    if form.validate_on_submit():
        current_app.extensions["container"]["auth_service"].logout()
    else:
        flash("Invalid logout request.", "danger")
    return redirect(url_for("public.index"))