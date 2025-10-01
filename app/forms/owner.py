# phuwishpk/finddominitorykmitl/FindDominitoryKMITL-develop-owner/app/forms/owner.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL
from wtforms import ValidationError


ROOM_TYPES = ("studio", "1br", "2br", "other")

class PropertyForm(FlaskForm):
    dorm_name = StringField("ชื่อหอ", validators=[DataRequired("กรุณากรอกชื่อหอพัก"), Length(max=120)])
    road = StringField("ถนน", validators=[Optional(), Length(max=255)])
    soi = StringField("ซอย", validators=[Optional(), Length(max=255)])
    room_type = StringField("ประเภทห้อง", validators=[DataRequired("กรุณากรอกประเภทห้อง"), Length(max=30)])
    rent_price = IntegerField("ค่าเช่า", validators=[DataRequired("กรุณากรอกค่าเช่า"), NumberRange(min=0)])
    contact_phone = StringField("เบอร์โทร", validators=[DataRequired("กรุณากรอกเบอร์โทรติดต่อ"), Length(max=20)])
    line_id = StringField("LINE ID", validators=[Optional(), Length(max=80)])
    facebook_url = StringField("Facebook", validators=[Optional(), URL("กรุณากรอก URL ให้ถูกต้อง"), Length(max=255)])
    water_rate = FloatField("ค่าน้ำ", validators=[DataRequired("กรุณากรอกค่าน้ำ"), NumberRange(min=0)])
    electric_rate = FloatField("ค่าไฟ", validators=[DataRequired("กรุณากรอกค่าไฟ"), NumberRange(min=0)])
    deposit_amount = IntegerField("เงินประกัน", validators=[DataRequired("กรุณากรอกเงินประกัน"), NumberRange(min=0)])
    location_pin_json = HiddenField("Location Pin JSON")
    additional_info = TextAreaField("ข้อมูลเพิ่มเติม", validators=[Optional(), Length(max=5000, message="ข้อมูลเพิ่มเติมต้องมีความยาวไม่เกิน 5000 ตัวอักษร")]) # <-- ส่วนที่เพิ่มเข้ามา

    def validate_room_type(self, field):
        if field.data and field.data.lower() not in ROOM_TYPES:
            raise ValidationError("ประเภทห้องต้องเป็นหนึ่งใน: " + ", ".join(ROOM_TYPES))