# app/forms/owner.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL
from wtforms import ValidationError

# ตัวเลือกประเภทห้องพัก
ROOM_TYPES = [("studio", "สตูดิโอ"), ("1br", "1 ห้องนอน"), ("2br", "2 ห้องนอน"), ("other", "อื่นๆ")]

class MultiCheckboxField(SelectMultipleField):
    """
    Field สำหรับแสดง Amenity ในรูปแบบ Checkbox หลายรายการ
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class PropertyForm(FlaskForm):
    """
    ฟอร์มสำหรับสร้างและแก้ไขข้อมูลหอพัก (Property)
    """
    dorm_name = StringField(
        "ชื่อหอพัก",
        validators=[DataRequired(message="กรุณากรอกชื่อหอพัก"), Length(max=120)]
    )
    room_type = StringField(
        "ประเภทห้อง",
        validators=[DataRequired(message="กรุณาเลือกประเภทห้อง")]
    )
    contact_phone = StringField(
        "เบอร์โทรศัพท์ติดต่อ",
        validators=[Optional(), Length(max=20)]
    )
    line_id = StringField("LINE ID", validators=[Optional(), Length(max=80)])
    facebook_url = StringField(
        "Facebook URL",
        validators=[Optional(), URL(message="รูปแบบ URL ไม่ถูกต้อง"), Length(max=255)]
    )

    rent_price = IntegerField(
        "ค่าเช่า (บาท/เดือน)",
        validators=[Optional(), NumberRange(min=0, message="ค่าเช่าต้องเป็นตัวเลขจำนวนเต็มบวก")]
    )
    water_rate = FloatField(
        "ค่าน้ำ (บาท/หน่วย)",
        validators=[Optional(), NumberRange(min=0, message="ค่าน้ำต้องเป็นตัวเลขทศนิยมบวก")]
    )
    electric_rate = FloatField(
        "ค่าไฟ (บาท/หน่วย)",
        validators=[Optional(), NumberRange(min=0, message="ค่าไฟต้องเป็นตัวเลขทศนิยมบวก")]
    )
    deposit_amount = IntegerField(
        "ค่ามัดจำ (บาท)",
        validators=[Optional(), NumberRange(min=0, message="ค่ามัดจำต้องเป็นตัวเลขจำนวนเต็มบวก")]
    )

    lat = FloatField("ละติจูด", validators=[Optional()])
    lng = FloatField("ลองจิจูด", validators=[Optional()])

    # Field สำหรับ Amenities (Many-to-Many)
    amenities = MultiCheckboxField("สิ่งอำนวยความสะดวก", choices=[], coerce=int)


    def validate_room_type(self, field):
        """
        ตรวจสอบว่าข้อมูล room_type ที่ส่งมานั้นอยู่ใน ROOM_TYPES ที่กำหนดไว้หรือไม่
        """
        if field.data and field.data not in [choice[0] for choice in ROOM_TYPES]:
            raise ValidationError(f"ประเภทห้องต้องเป็นหนึ่งใน: {', '.join([c[0] for c in ROOM_TYPES])}")