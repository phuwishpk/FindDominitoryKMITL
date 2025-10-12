from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange

class ReviewForm(FlaskForm):
    comment = TextAreaField('ความคิดเห็น', validators=[DataRequired()])
    rating = SelectField('ให้คะแนน', 
                         choices=[('5', '5 ดาว'), ('4', '4 ดาว'), ('3', '3 ดาว'), ('2', '2 ดาว'), ('1', '1 ดาว')],
                         validators=[DataRequired()])