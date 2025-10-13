from flask import render_template, redirect, url_for, flash, current_app, request
from . import bp
from app.forms.auth import OwnerRegisterForm, OwnerLoginForm, AdminLoginForm, CombinedLoginForm
from app.models.user import Owner, Admin
from flask_login import login_required
from werkzeug.security import generate_password_hash

@bp.route("/owner/register", methods=["GET","POST"])
def owner_register():
    form = OwnerRegisterForm()
    if form.validate_on_submit():
        svc = current_app.extensions["container"]["auth_service"]
        svc.register_owner(form.data)
        flash("สมัครสำเร็จ")
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
            if svc.verify_owner(form.username.data, form.password.data):
                owner = Owner.query.filter_by(email=form.username.data).first()
                svc.login_owner(owner)
                return redirect(url_for("owner.dashboard"))
            flash("ข้อมูลเข้าใช้งานไม่ถูกต้อง (Owner)")
        else:
            admin = svc.verify_admin(form.username.data, form.password.data)
            if admin:
                svc.login_admin(admin)
                return redirect(url_for("admin.queue"))
            flash("ข้อมูลเข้าใช้งานไม่ถูกต้อง (Admin)")
    return render_template("auth/login.html", form=form)

@bp.get("/logout")
@login_required
def logout():
    current_app.extensions["container"]["auth_service"].logout()
    return redirect(url_for("public.index"))
