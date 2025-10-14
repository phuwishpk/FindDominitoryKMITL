from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ReviewForm(FlaskForm):
    rating = SelectField(
        "ให้คะแนน",
        choices=[(str(i), f"{i} ดาว") for i in range(1, 6)],
        validators=[DataRequired()]
    )
    comment = TextAreaField("ความคิดเห็น", validators=[DataRequired()])
    submit = SubmitField("ส่งความคิดเห็น")
