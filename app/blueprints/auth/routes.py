from flask import render_template, redirect, url_for, flash, current_app, request, session
from flask_login import login_required, current_user
from . import bp
from app.forms.auth import OwnerRegisterForm, CombinedLoginForm, ForgotPasswordForm, ResetPasswordForm
from app.forms.upload import EmptyForm
from app.models.user import Owner, Admin
from werkzeug.security import generate_password_hash
from app.extensions import db # <<< เพิ่ม import db

# --- vvv เพิ่ม import สำหรับส่งอีเมล vvv ---
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# --- ^^^ สิ้นสุดการ import ^^^ ---

# --- vvv แก้ไขฟังก์ชันสำหรับส่งอีเมล vvv ---
def send_reset_email(owner):
    token = owner.get_reset_token()
    
    msg = MIMEMultipart()
    msg['From'] = current_app.config['MAIL_DEFAULT_SENDER'][1]
    msg['To'] = owner.email
    msg['Subject'] = "คำขอรีเซ็ตรหัสผ่านสำหรับ FindDorm KMITL"
    
    html_body = render_template('email/reset_password.html', owner=owner, token=token)
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            # ตรวจสอบการตั้งค่าก่อนเรียกใช้ starttls และ login
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            if current_app.config['MAIL_USERNAME']:
                server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.send_message(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        
    # <<< ส่วนที่ 1: เพิ่มการคืนค่า token
    return token
# --- ^^^ สิ้นสุดฟังก์ชันส่งอีเมล ^^^ ---


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

@bp.route("/reset-password", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        owner = Owner.query.filter_by(email=form.email.data).first()
        if owner:
            # --- vvv ส่วนที่ 2: แก้ไขการเรียกใช้และ Redirect vvv ---
            token = send_reset_email(owner) # รับค่า token ที่ถูกส่งคืนมา
            flash('(Token ถูกสร้างแล้ว) เปลี่ยนรหัสผ่านและยืนยันได้เลย', 'info')
            return redirect(url_for('auth.reset_password', token=token)) # Redirect พร้อมส่ง token ไปด้วย
            # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
        else:
            flash('ไม่พบอีเมลนี้ในระบบ กรุณาตรวจสอบอีกครั้ง', 'warning')
    return render_template('auth/forgot_password_request.html', form=form)


@bp.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    owner = Owner.verify_reset_token(token)
    if not owner:
        flash('Token สำหรับรีเซ็ตรหัสผ่านไม่ถูกต้องหรือหมดอายุแล้ว', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        owner.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('รหัสผ่านของคุณถูกเปลี่ยนเรียบร้อยแล้ว สามารถเข้าสู่ระบบได้เลย', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', form=form)