from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from wtforms import ValidationError

# ถ้าอยากใช้ยูทิลของคุณเองต่อไปด้วย ก็ยัง import ได้
from app.utils.validation import is_valid_citizen_id, validate_pdf_file


def _strip(s):
    return s.strip() if isinstance(s, str) else s

def _digits_only(s):
    return ''.join(ch for ch in s if ch.isdigit()) if isinstance(s, str) else s


class OwnerRegisterForm(FlaskForm):
    full_name_th = StringField(
        'ชื่อ-สกุล (ไทย)',
        filters=[_strip],
        validators=[DataRequired(), Length(max=120)]
    )
    full_name_en = StringField(
        'Full Name (EN)',
        filters=[_strip],
        validators=[Optional(), Length(max=120)]
    )
    citizen_id = StringField(
        'เลขบัตรประชาชน',
        # ลอกขีด/ช่องว่างออกก่อน แล้วค่อยตรวจ
        filters=[_digits_only],
        validators=[
            DataRequired(),
            Regexp(r'^\d{13}$', message='กรุณากรอกเลขบัตรประชาชน 13 หลัก')
        ]
    )
    email = StringField(
        'อีเมล',
        filters=[_strip, str.lower],
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    phone = StringField(
        'เบอร์โทร',
        filters=[_strip, _digits_only],
        validators=[Optional(), Length(max=20)]
    )
    password = PasswordField(
        'รหัสผ่าน',
        validators=[DataRequired(), Length(min=6, max=128)]
    )

    # ถ้าบังคับแนบไฟล์ ให้ใช้ FileRequired(); ถ้าไม่บังคับ ให้ใช้ Optional()
    occupancy_pdf = FileField(
        'หนังสือแจ้งมีผู้เข้าพัก (PDF)',
        validators=[
            Optional(),
            FileAllowed(['pdf'], 'อัปโหลดเฉพาะไฟล์ PDF เท่านั้น'),
            FileSize(max_size=10 * 1024 * 1024, message='ไฟล์ต้องไม่เกิน 10 MB'),
        ]
    )

    # --- custom validators ---
    def validate_citizen_id(self, field):
        # เสริมด้วยตรรกะของคุณ (ตรวจสอบ checksum ของเลขบัตรฯ) ถ้ามี
        if not is_valid_citizen_id(field.data):
            raise ValidationError('เลขบัตรประชาชนไม่ถูกต้อง')

    def validate_occupancy_pdf(self, field):
        # ถ้าอยากใช้ตัวตรวจของคุณเองเพิ่มเติม (เช่น ตรวจว่าเป็น PDF จริงด้วย magic number)
        if field.data:
            validate_pdf_file(field.data, max_mb=10)


class OwnerLoginForm(FlaskForm):
    email = StringField(
        'อีเมล',
        filters=[_strip, str.lower],
        validators=[DataRequired(), Email()]
    )
    password = PasswordField('รหัสผ่าน', validators=[DataRequired()])


class AdminLoginForm(FlaskForm):
    username = StringField(
        'ชื่อผู้ใช้',
        filters=[_strip],
        validators=[DataRequired(), Length(max=80)]
    )
    password = PasswordField('รหัสผ่าน', validators=[DataRequired()])
