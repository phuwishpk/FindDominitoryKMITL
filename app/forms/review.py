from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ReviewForm(FlaskForm):
    rating = SelectField(
        "ให้คะแนน",
        choices=[("5","5"), ("4","4"), ("3","3"), ("2","2"), ("1","1")],
        validators=[DataRequired(message="กรุณาให้คะแนน")]
    )
    comment = TextAreaField(
        "ความคิดเห็น",
        validators=[DataRequired(message="กรุณาพิมพ์ความคิดเห็น"), Length(max=1000)]
    )
    submit = SubmitField("ส่งความคิดเห็น")