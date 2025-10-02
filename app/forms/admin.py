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
            DataRequired("กรุณาระบุเหตุผลในการไม่อนุมัติ"), 
            Length(max=500, message="เหตุผลต้องไม่เกิน 500 ตัวอักษร")
        ],
        render_kw={"placeholder": "ระบุเหตุผลในการปฏิเสธคำขออนุมัติ..."}
    )
    submit = SubmitField('ปฏิเสธคำขอ')