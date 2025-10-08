from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms import ValidationError
from app.utils.validation import is_valid_citizen_id, validate_pdf_file
# --- vvv ส่วนที่เพิ่มเข้ามา vvv ---
from app.models.user import Owner
# --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---

class OwnerRegisterForm(FlaskForm):
    full_name_th = StringField('ชื่อ-สกุล (ไทย)', validators=[DataRequired(), Length(max=120)])
    full_name_en = StringField('Full Name (EN)', validators=[Optional(), Length(max=120)])
    citizen_id = StringField('เลขบัตรประชาชน', validators=[DataRequired(), Length(min=13, max=13)])
    email = StringField('อีเมล', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('เบอร์โทร', validators=[Optional(), Length(max=20)])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=6, max=128)])
    occupancy_pdf = FileField('หนังสือแจ้งมีผู้เข้าพัก (PDF)', validators=[Optional()])

    def validate_citizen_id(self, field):
        # --- vvv ส่วนที่แก้ไข vvv ---
        # ตรวจสอบ format ของเลขบัตรประชาชน
        if not is_valid_citizen_id(field.data):
            raise ValidationError('เลขบัตรประชาชนไม่ถูกต้อง')
        # ตรวจสอบว่าเลขบัตรนี้มีในระบบแล้วหรือยัง
        if Owner.query.filter_by(citizen_id=field.data).first():
            raise ValidationError('เลขบัตรประชาชนนี้มีผู้ใช้งานในระบบแล้ว')
        # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

    # --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
    def validate_email(self, field):
        # ตรวจสอบว่าอีเมลนี้มีในระบบแล้วหรือยัง
        if Owner.query.filter_by(email=field.data).first():
            raise ValidationError('อีเมลนี้มีผู้ใช้งานในระบบแล้ว')
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

    def validate_occupancy_pdf(self, field):
        if field.data:
            validate_pdf_file(field.data, max_mb=10)

class OwnerLoginForm(FlaskForm):
    email = StringField('อีเมล', validators=[DataRequired(), Email()])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired()])

class AdminLoginForm(FlaskForm):
    username = StringField('ชื่อผู้ใช้', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired()])

class CombinedLoginForm(FlaskForm):
    username = StringField('ชื่อผู้ใช้ / อีเมล', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=3, max=128)])
    role = SelectField('ประเภทผู้ใช้', choices=[('owner','Owner'), ('admin','Admin')], default='owner')
    remember = BooleanField('จำการเข้าสู่ระบบ')