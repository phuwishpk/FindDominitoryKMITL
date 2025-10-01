# app/forms/admin.py
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RejectForm(FlaskForm):
    """
    ฟอร์มสำหรับรับเหตุผลในการปฏิเสธคำขออนุมัติ
    """
    note = TextAreaField(
        'เหตุผลในการไม่อนุมัติ', 
        validators=[
            DataRequired(message="กรุณาระบุเหตุผลในการไม่อนุมัติ"), 
            Length(max=500)
        ],
        render_kw={"placeholder": "ระบุเหตุผลในการปฏิเสธคำขออนุมัติ..."}
    )
    submit = SubmitField('ปฏิเสธคำขอ')

class EmptyForm(FlaskForm):
    """ฟอร์มว่างสำหรับรับ CSRF token เท่านั้น (ใช้ในการอนุมัติ)"""
    pass