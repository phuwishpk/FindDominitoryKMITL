from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL
from wtforms import ValidationError

ROOM_TYPES = ("studio", "1br", "2br", "other")

class PropertyForm(FlaskForm):
    dorm_name = StringField("ชื่อหอ", validators=[DataRequired(), Length(max=120)])
    room_type = StringField("ประเภทห้อง", validators=[DataRequired(), Length(max=30)])
    contact_phone = StringField("เบอร์โทร", validators=[Optional(), Length(max=20)])
    line_id = StringField("LINE ID", validators=[Optional(), Length(max=80)])
    facebook_url = StringField("Facebook", validators=[Optional(), URL(), Length(max=255)])

    rent_price = IntegerField("ค่าเช่า", validators=[Optional(), NumberRange(min=0, max=200000)])
    water_rate = FloatField("ค่าน้ำ", validators=[Optional(), NumberRange(min=0, max=10000)])
    electric_rate = FloatField("ค่าไฟ", validators=[Optional(), NumberRange(min=0, max=10000)])
    deposit_amount = IntegerField("เงินประกัน", validators=[Optional(), NumberRange(min=0, max=1000000)])

    lat = FloatField("ละติจูด", validators=[Optional()])
    lng = FloatField("ลองจิจูด", validators=[Optional()])

    def validate_room_type(self, field):
        if field.data and field.data not in ROOM_TYPES:
            raise ValidationError("room_type ต้องเป็นหนึ่งใน: " + ", ".join(ROOM_TYPES))