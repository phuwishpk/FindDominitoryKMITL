# phuwishpk/finddominitorykmitl/FindDominitoryKMITL-develop-owner/app/forms/owner.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, HiddenField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL
from wtforms import ValidationError

class PropertyForm(FlaskForm):
    dorm_name = StringField("ชื่อหอ", validators=[DataRequired("กรุณากรอกชื่อหอพัก"), Length(max=120)])
    road = StringField("ถนน", validators=[Optional(), Length(max=255)])
    soi = StringField("ซอย", validators=[Optional(), Length(max=255)])
    
    room_type = SelectField(
        "ประเภทห้อง",
        choices=[
            ('', '--- กรุณาเลือกประเภทห้อง ---'),
            ('ห้องธรรมดา (Standard Room)', 'ห้องธรรมดา (Standard Room)'),
            ('ห้องสตูดิโอ (Studio Room)', 'ห้องสตูดิโอ (Studio Room)'),
            ('ห้องชุด (Suite Room)', 'ห้องชุด (Suite Room)'),
            ('อื่นๆ', 'อื่นๆ (โปรดระบุ)')
        ],
        validators=[DataRequired("กรุณาเลือกประเภทห้อง")]
    )
    
    other_room_type = StringField(
        "ระบุประเภทห้อง",
        validators=[Optional(), Length(max=100, message="ประเภทห้องต้องมีความยาวไม่เกิน 100 ตัวอักษร")]
    )

    rent_price = IntegerField("ค่าเช่า", validators=[DataRequired("กรุณากรอกค่าเช่า"), NumberRange(min=0)])
    contact_phone = StringField("เบอร์โทร", validators=[DataRequired("กรุณากรอกเบอร์โทรติดต่อ"), Length(max=20)])
    line_id = StringField("LINE ID", validators=[Optional(), Length(max=80)])
    facebook_url = StringField("Facebook", validators=[Optional(), URL("กรุณากรอก URL ให้ถูกต้อง"), Length(max=255)])
    water_rate = FloatField("ค่าน้ำ", validators=[DataRequired("กรุณากรอกค่าน้ำ"), NumberRange(min=0)])
    electric_rate = FloatField("ค่าไฟ", validators=[DataRequired("กรุณากรอกค่าไฟ"), NumberRange(min=0)])
    deposit_amount = IntegerField("เงินประกัน", validators=[DataRequired("กรุณากรอกเงินประกัน"), NumberRange(min=0)])
    location_pin_json = HiddenField("Location Pin JSON")
    additional_info = TextAreaField("ข้อมูลเพิ่มเติม", validators=[Optional(), Length(max=5000, message="ข้อมูลเพิ่มเติมต้องมีความยาวไม่เกิน 5000 ตัวอักษร")])

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        
        if self.room_type.data == 'อื่นๆ' and not self.other_room_type.data:
            self.other_room_type.errors.append('กรุณาระบุประเภทห้อง เมื่อเลือก "อื่นๆ"')
            return False
            
        return True