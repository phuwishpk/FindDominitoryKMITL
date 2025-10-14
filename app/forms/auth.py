from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from wtforms import ValidationError
from app.utils.validation import is_valid_citizen_id, validate_pdf_file
from app.models.user import Owner

class OwnerRegisterForm(FlaskForm):
    full_name_th = StringField('ชื่อ-สกุล (ไทย)', validators=[DataRequired(), Length(max=120)])
    # --- vvv เพิ่มฟิลด์นี้ vvv ---
    full_name_en = StringField('ชื่อ-สกุล (อังกฤษ)', validators=[Optional(), Length(max=120)])
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
    email = StringField('อีเมล', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField('ยืนยันรหัสผ่าน', validators=[
        DataRequired(),
        EqualTo('password', message='รหัสผ่านต้องตรงกัน')
    ])
    citizen_id = StringField('เลขบัตรประชาชน', validators=[DataRequired(), Length(min=13, max=13)])
    phone = StringField('เบอร์โทร', validators=[Optional(), Length(max=20)])
    occupancy_pdf = FileField('หนังสือแจ้งมีผู้เข้าพัก (PDF)', validators=[Optional()])

    def validate_citizen_id(self, field):
        if not is_valid_citizen_id(field.data):
            raise ValidationError('เลขบัตรประชาชนไม่ถูกต้อง')
        if Owner.query.filter_by(citizen_id=field.data).first():
            raise ValidationError('เลขบัตรประชาชนนี้มีผู้ใช้งานในระบบแล้ว')

    def validate_email(self, field):
        if Owner.query.filter_by(email=field.data).first():
            raise ValidationError('อีเมลนี้มีผู้ใช้งานในระบบแล้ว')

    def validate_occupancy_pdf(self, field):
        if field.data:
            try:
                validate_pdf_file(field.data, max_mb=10)
            except ValidationError as e:
                raise ValidationError(str(e))

class CombinedLoginForm(FlaskForm):
    username = StringField('ชื่อผู้ใช้ / อีเมล', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=3, max=128)])
    remember = BooleanField('จำการเข้าสู่ระบบ')