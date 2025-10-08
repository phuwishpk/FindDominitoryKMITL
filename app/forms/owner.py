# phuwishpk/finddominitorykmitl/FindDominitoryKMITL-develop-owner/app/forms/owner.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, HiddenField, TextAreaField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL
from wtforms import ValidationError
from app.utils.validation import validate_image_file
from flask import request

class PropertyForm(FlaskForm):
    dorm_name = StringField("ชื่อหอ", validators=[DataRequired("กรุณากรอกชื่อหอพัก"), Length(max=120)])
    
    # --- vvv ส่วนที่แก้ไข vvv ---
    road = StringField("ถนน", validators=[DataRequired("กรุณากรอกชื่อถนน"), Length(max=255)])
    soi = StringField("ซอย", validators=[DataRequired("กรุณากรอกชื่อซอย"), Length(max=255)])
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---
    
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
    
    # --- vvv ส่วนที่แก้ไข vvv ---
    location_pin_json = HiddenField("Location Pin JSON", validators=[DataRequired("กรุณาปักหมุดตำแหน่งบนแผนที่")])
    additional_info = TextAreaField("ข้อมูลเพิ่มเติม", validators=[Optional(), Length(max=5000, message="ข้อมูลเพิ่มเติมต้องมีความยาวไม่เกิน 5000 ตัวอักษร")])
    images = MultipleFileField('รูปภาพ', validators=[Optional()])
    # เพิ่ม field จำลองสำหรับแสดง error ของ amenities
    amenities = HiddenField() 
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---

    def validate_images(self, field):
        if field.data and field.data[0].filename:
            for file_storage in field.data:
                validate_image_file(file_storage, max_mb=3)

    def validate(self, **kwargs):
        # --- vvv ส่วนที่แก้ไข vvv ---
        # ทำ validation ของ parent class ก่อน
        is_valid = super().validate(**kwargs)
        
        # 1. ตรวจสอบ 'ระบุประเภทห้อง' ถ้าเลือก 'อื่นๆ'
        if self.room_type.data == 'อื่นๆ' and not self.other_room_type.data:
            self.other_room_type.errors.append('กรุณาระบุประเภทห้อง เมื่อเลือก "อื่นๆ"')
            is_valid = False
            
        # 2. ตรวจสอบว่ามีการเลือก 'สิ่งอำนวยความสะดวก' อย่างน้อย 1 อย่าง
        if not request.form.getlist('amenities'):
            self.amenities.errors.append('กรุณาเลือกสิ่งอำนวยความสะดวกอย่างน้อย 1 อย่าง')
            is_valid = False
            
        return is_valid
        # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---