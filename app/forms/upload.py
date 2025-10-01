from flask_wtf import FlaskForm
from wtforms import MultipleFileField, FieldList, HiddenField # <-- แก้ไข import
from wtforms.validators import Optional
from app.utils.validation import validate_image_file

class UploadImageForm(FlaskForm):
    image = MultipleFileField('รูปภาพ', validators=[Optional()]) # <-- แก้ไขเป็น MultipleFileField

    def validate_image(self, field):
        # ตรวจสอบไฟล์ทุกไฟล์ที่ถูกอัปโหลดเข้ามา
        if field.data:
            for file_storage in field.data:
                if file_storage.filename: # ตรวจสอบว่ามีไฟล์จริงๆ
                    validate_image_file(file_storage, max_mb=3)

class ReorderImagesForm(FlaskForm):
    positions = FieldList(HiddenField('positions'), min_entries=0)