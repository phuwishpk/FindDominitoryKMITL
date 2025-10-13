# phuwishpk/finddominitorykmitl/FindDominitoryKMITL-owner-improvements/app/forms/owner.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, HiddenField, TextAreaField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL, ValidationError
from app.utils.validation import validate_image_file
from flask import request

ROOM_TYPE_CHOICES = [
    ('', '--- กรุณาเลือกประเภทห้อง ---'),
    ('standard', 'ห้องธรรมดา (Standard Room)'),
    ('studio', 'ห้องสตูดิโอ (Studio Room)'),
    ('suite', 'ห้องชุด (Suite Room)'),
    ('other', 'อื่นๆ (โปรดระบุ)')
]

class PropertyForm(FlaskForm):
    dorm_name = StringField("ชื่อหอ", validators=[DataRequired("กรุณากรอกชื่อหอพัก"), Length(max=120)])
    road = StringField("ถนน", validators=[DataRequired("กรุณากรอกชื่อถนน"), Length(max=255)])
    soi = StringField("ซอย", validators=[DataRequired("กรุณากรอกชื่อซอย"), Length(max=255)])
    room_type = SelectField(
        "ประเภทห้อง",
        choices=ROOM_TYPE_CHOICES,
        validators=[DataRequired("กรุณาเลือกประเภทห้อง")]
    )
    other_room_type = StringField(
        "ระบุประเภทห้อง",
        validators=[Optional(), Length(max=100, message="ประเภทห้องต้องมีความยาวไม่เกิน 100 ตัวอักษร")]
    )
    rent_price = IntegerField("ค่าเช่า", validators=[DataRequired("กรุณากรอกค่าเช่า"), NumberRange(min=0)])
    contact_phone = StringField("เบอร์โทร", validators=[DataRequired("กรุณากรอกเบอร์โทรติดต่อ"), Length(max=20)])
    line_id = StringField("LINE ID", validators=[Optional(), Length(max=80)])
    facebook_url = StringField("Facebook", validators=[Optional(), Length(max=255)])
    water_rate = FloatField("ค่าน้ำ", validators=[DataRequired("กรุณากรอกค่าน้ำ"), NumberRange(min=0)])
    electric_rate = FloatField("ค่าไฟ", validators=[DataRequired("กรุณากรอกค่าไฟ"), NumberRange(min=0)])
    deposit_amount = IntegerField("เงินประกัน", validators=[DataRequired("กรุณากรอกเงินประกัน"), NumberRange(min=0)])
    location_pin_json = HiddenField("Location Pin JSON", validators=[DataRequired("กรุณาปักหมุดตำแหน่งบนแผนที่")])
    additional_info = TextAreaField("ข้อมูลเพิ่มเติม", validators=[Optional(), Length(max=5000, message="ข้อมูลเพิ่มเติมต้องมีความยาวไม่เกิน 5000 ตัวอักษร")])
    images = MultipleFileField('รูปภาพ', validators=[])
    amenities = HiddenField()

    def validate_facebook_url(self, field):
        if field.data and field.data.strip() != '-':
            URL(message="กรุณากรอก URL ให้ถูกต้อง")(self, field)

    def validate_images(self, field):
        if field.data and field.data[0].filename:
            for file_storage in field.data:
                try:
                    validate_image_file(file_storage, max_mb=3)
                except ValidationError as e:
                    self.images.errors.append(str(e))

    def validate(self, **kwargs):
        is_valid = super().validate(**kwargs)
        if self.room_type.data == 'other' and not self.other_room_type.data:
            self.other_room_type.errors.append('กรุณาระบุประเภทห้อง เมื่อเลือก "อื่นๆ"')
            is_valid = False
        if not request.form.getlist('amenities'):
            self.amenities.errors.append('กรุณาเลือกสิ่งอำนวยความสะดวกอย่างน้อย 1 อย่าง')
            is_valid = False
        is_create_mode = 'prop_id' not in request.view_args
        if is_create_mode:
            uploaded_files = request.files.getlist(self.images.name)
            if not uploaded_files or not uploaded_files[0].filename:
                 self.images.errors.append('กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูป')
                 is_valid = False
        return is_valid