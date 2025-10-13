# File: app/blueprints/auth/routes.py

from flask import render_template, redirect, url_for, flash, current_app, request
from . import bp
# ⬇️ [app/forms/auth.py], [app/models/user.py]
from app.forms.auth import OwnerRegisterForm, OwnerLoginForm, AdminLoginForm, CombinedLoginForm
from app.models.user import Owner, Admin
from flask_login import login_required
from werkzeug.security import generate_password_hash

@bp.route("/owner/register", methods=["GET","POST"])
def owner_register():
    # ⬇️ [app/forms/auth.py] ใช้ฟอร์มลงทะเบียน
    form = OwnerRegisterForm()
    if form.validate_on_submit():
        # ⬇️ [app/__init__.py] ดึง AuthService จาก DI container
        svc = current_app.extensions["container"]["auth_service"]
        svc.register_owner(form.data)
        flash("สมัครสำเร็จ")
        # ⬇️ [app/blueprints/auth/routes.py] Redirect ไปหน้า Login
        return redirect(url_for("auth.login"))
    # ⬇️ [app/templates/auth/owner_register.html] แสดงฟอร์ม
    return render_template("auth/owner_register.html", form=form)

@bp.route("/login", methods=["GET","POST"])
def login():
    # Admin seeding logic (คงไว้ตามโค้ดเดิม)
    if not Admin.query.filter_by(username="admin").first():
        a = Admin(username="admin", password_hash=generate_password_hash("admin"), display_name="Administrator")
        from app.extensions import db
        db.session.add(a); db.session.commit()

    # ⬇️ [app/forms/auth.py] ใช้ CombinedLoginForm
    form = CombinedLoginForm(role=request.args.get("role","owner"))
    if form.validate_on_submit():
        role = form.role.data
        # ⬇️ [app/__init__.py] ดึง AuthService จาก DI container
        svc = current_app.extensions["container"]["auth_service"]
        
        if role == "owner":
            # ⬇️ [app/services/auth_service.py] เรียก verify_owner ซึ่งจะคืนค่า Owner object
            owner = svc.verify_owner(form.username.data, form.password.data)
            if owner:
                # ⬇️ [app/services/auth_service.py] เข้าสู่ระบบด้วย Owner object ที่ได้มา
                svc.login_owner(owner, remember=form.remember.data)
                # ⬇️ [app/blueprints/owner/routes.py] Redirect ไปหน้า Dashboard
                return redirect(url_for("owner.dashboard"))
            flash("ข้อมูลเข้าใช้งานไม่ถูกต้อง (Owner) หรือบัญชียังไม่ถูกเปิดใช้งาน")
        else: # admin
            # ⬇️ [app/services/auth_service.py] เรียก verify_admin
            admin = svc.verify_admin(form.username.data, form.password.data)
            if admin:
                # ⬇️ [app/services/auth_service.py] เข้าสู่ระบบด้วย Admin object
                svc.login_admin(admin, remember=form.remember.data)
                # ⬇️ [app/blueprints/admin/routes.py] Redirect ไปหน้า Admin Queue
                return redirect(url_for("admin.queue"))
            flash("ข้อมูลเข้าใช้งานไม่ถูกต้อง (Admin)")
            
    # ⬇️ [app/templates/auth/login.html] แสดงฟอร์ม login
    return render_template("auth/login.html", form=form)

# 🛠️ [app/blueprints/auth/routes.py] แก้ไข: เปลี่ยนจาก @bp.get เป็น @bp.route เพื่อรับทั้ง GET/POST (แก้ปัญหา 405)
@bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    current_app.extensions["container"]["auth_service"].logout()
    # ⬇️ [app/blueprints/public/routes.py] Redirect ไปหน้า Public Index
    return redirect(url_for("public.index"))
