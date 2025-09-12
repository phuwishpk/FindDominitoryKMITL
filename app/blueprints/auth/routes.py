from flask import render_template, redirect, url_for, flash, current_app
from . import bp
from app.forms.auth import OwnerRegisterForm, OwnerLoginForm, AdminLoginForm
from app.models.user import Owner
from flask_login import login_required, current_user

@bp.route("/owner/register", methods=["GET","POST"])
def owner_register():
    form = OwnerRegisterForm()
    if form.validate_on_submit():
        svc = current_app.extensions["container"]["auth_service"]
        svc.register_owner(form.data)
        flash("สมัครสำเร็จ")
        return redirect(url_for("auth.owner_login"))
    return render_template("auth/owner_register.html", form=form)

@bp.route("/owner/login", methods=["GET","POST"])
def owner_login():
    form = OwnerLoginForm()
    if form.validate_on_submit():
        svc = current_app.extensions["container"]["auth_service"]
        if svc.verify_owner(form.email.data, form.password.data):
            owner = Owner.query.filter_by(email=form.email.data).first()
            # remember=True ได้โดยแก้ใน service เป็น login_user(principal, remember=True)
            svc.login_owner(owner)
            return redirect(url_for("owner.dashboard"))
        flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    return render_template("auth/owner_login.html", form=form)

@bp.route("/admin/login", methods=["GET","POST"])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        svc = current_app.extensions["container"]["auth_service"]
        admin = svc.verify_admin(form.username.data, form.password.data)
        if admin:
            svc.login_admin(admin)  # ตั้ง remember ใน service ได้
            return redirect(url_for("admin.queue"))
        flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    return render_template("auth/admin_login.html", form=form)

@bp.get("/logout")
@login_required
def logout():
    current_app.extensions["container"]["auth_service"].logout()
    return redirect(url_for("public.index"))
