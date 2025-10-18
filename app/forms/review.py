from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ReviewForm(FlaskForm):
    rating = SelectField(
        "ให้คะแนน",
        choices=[(str(i), f"{i} ดาว") for i in range(1, 6)],
        validators=[DataRequired(message="กรุณาให้คะแนน")]
    )
    comment = TextAreaField("ความคิดเห็น", validators=[
        DataRequired(message="กรุณากรอกความคิดเห็น"),
        Length(min=10, max=500, message="ความคิดเห็นต้องมีความยาวระหว่าง 10 ถึง 500 ตัวอักษร")
    ])
    submit = SubmitField("ส่งความคิดเห็น")