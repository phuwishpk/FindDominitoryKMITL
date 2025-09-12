from flask_wtf import FlaskForm
from wtforms import FileField, FieldList, HiddenField
from wtforms.validators import Optional
from app.utils.validation import validate_image_file
from wtforms import ValidationError

class UploadImageForm(FlaskForm):
    image = FileField("รูปภาพ", validators=[Optional()])
    def validate_image(self, field):
        if field.data:
            validate_image_file(field.data, max_mb=3)

class ReorderImagesForm(FlaskForm):
    positions = FieldList(HiddenField("positions"), min_entries=0)
