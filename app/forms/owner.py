from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL
from wtforms import ValidationError

ROOM_TYPES = ("studio", "1br", "2br", "other")

class PropertyForm(FlaskForm):
    # --- ส่วนที่บังคับกรอก ---
    dorm_name = StringField("ชื่อหอ", validators=[DataRequired("กรุณากรอกชื่อหอพัก"), Length(max=120)])
    room_type = StringField("ประเภทห้อง", validators=[DataRequired("กรุณากรอกประเภทห้อง"), Length(max=30)])
    rent_price = IntegerField("ค่าเช่า", validators=[DataRequired("กรุณากรอกค่าเช่า"), NumberRange(min=0)])
    
    # --- ส่วนที่ไม่บังคับ แต่ถ้ากรอกต้องถูกรูปแบบ ---
    contact_phone = StringField("เบอร์โทร", validators=[Optional(), Length(max=20)])
    line_id = StringField("LINE ID", validators=[Optional(), Length(max=80)])
    facebook_url = StringField("Facebook", validators=[Optional(), URL(), Length(max=255)])

    water_rate = FloatField("ค่าน้ำ", validators=[Optional(), NumberRange(min=0)])
    electric_rate = FloatField("ค่าไฟ", validators=[Optional(), NumberRange(min=0)])
    deposit_amount = IntegerField("เงินประกัน", validators=[Optional(), NumberRange(min=0)])

    lat = FloatField("ละติจูด", validators=[Optional()])
    lng = FloatField("ลองจิจูด", validators=[Optional()])

    def validate_room_type(self, field):
        if field.data and field.data.lower() not in ROOM_TYPES:
            raise ValidationError("ประเภทห้องต้องเป็นหนึ่งใน: " + ", ".join(ROOM_TYPES))