# app/forms/admin.py
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp

class RejectForm(FlaskForm):
    """
    ฟอร์มสำหรับรับเหตุผลในการปฏิเสธคำขออนุมัติ
    """
    note = TextAreaField(
        'เหตุผลในการไม่อนุมัติ', 
        validators=[
            DataRequired("กรุณาระบุเหตุผลในการไม่อนุมัติ"), 
            Length(max=500, message="เหตุผลต้องไม่เกิน 500 ตัวอักษร")
        ],
        render_kw={"placeholder": "ระบุเหตุผลในการปฏิเสธคำขออนุมัติ..."}
    )
    submit = SubmitField('ปฏิเสธคำขอ')

class AdminEditOwnerForm(FlaskForm):
    """
    ฟอร์มสำหรับ Admin ในการแก้ไขข้อมูล Owner (จำกัดให้แก้ไขได้เพียง is_active เท่านั้น)
    """
    # ฟิลด์ is_active ถูกคงไว้เพื่อแก้ไขสถานะการใช้งาน
    is_active = BooleanField('บัญชีนี้สามารถใช้งานได้ (Active)')
    # ฟิลด์ submit ถูกเปลี่ยนชื่อปุ่ม
    submit = SubmitField('บันทึกสถานะ')

# --- vvv ส่วนที่เพิ่มเข้ามาใหม่ vvv ---
class AmenityForm(FlaskForm):
    """
    ฟอร์มสำหรับ เพิ่ม/แก้ไข สิ่งอำนวยความสะดวก
    """
    code = StringField(
        'Code (ภาษาอังกฤษ, ห้ามเว้นวรรค)', 
        validators=[
            DataRequired(), 
            Length(max=32),
            Regexp(r'^[a-z0-9_]+$', message='Code ต้องเป็นภาษาอังกฤษตัวพิมพ์เล็ก, ตัวเลข, หรือ underscore (_) เท่านั้น')
        ]
    )
    label_th = StringField('ชื่อที่แสดง (ไทย)', validators=[DataRequired(), Length(max=120)])
    label_en = StringField('ชื่อที่แสดง (อังกฤษ)', validators=[Optional(), Length(max=120)])
    submit = SubmitField('บันทึก')

class AdminEditPropertyForm(FlaskForm):
    """
    ฟอร์มสำหรับ Admin ในการแก้ไขข้อมูลหอพัก
    """
    dorm_name = StringField("ชื่อหอ", validators=[DataRequired(), Length(max=120)])
    workflow_status = SelectField(
        "สถานะประกาศ",
        choices=[
            ('draft', 'Draft (แบบร่าง)'), 
            ('submitted', 'Submitted (รออนุมัติ)'),
            ('approved', 'Approved (อนุมัติแล้ว)'), 
            ('rejected', 'Rejected (ถูกปฏิเสธ)')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('บันทึกข้อมูลหอพัก')
# --- ^^^ สิ้นสุดส่วนที่เพิ่ม ^^^ ---
# ดึงจาก dev-jek