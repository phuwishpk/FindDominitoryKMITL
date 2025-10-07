from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Optional

class RejectForm(FlaskForm):
    note = TextAreaField(
        'เหตุผลในการไม่อนุมัติ', 
        validators=[
            DataRequired("กรุณาระบุเหตุผลในการไม่อนุมัติ"), 
            Length(max=500, message="เหตุผลต้องไม่เกิน 500 ตัวอักษร")
        ],
        render_kw={"placeholder": "ระบุเหตุผลในการปฏิเสธคำขออนุมัติ..."}
    )
    submit = SubmitField('ปฏิเสธคำขอ')

# --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
class AdminEditOwnerForm(FlaskForm):
    """
    ฟอร์มสำหรับ Admin ในการแก้ไขข้อมูล Owner
    """
    full_name_th = StringField('ชื่อ-สกุล (ไทย)', validators=[DataRequired(), Length(max=120)])
    email = StringField('อีเมล', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('เบอร์โทร', validators=[Optional(), Length(max=20)])
    is_active = BooleanField('บัญชีนี้สามารถใช้งานได้ (Active)')
    submit = SubmitField('บันทึกการเปลี่ยนแปลง')
# --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---