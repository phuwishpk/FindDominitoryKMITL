from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    author_name = StringField('ชื่อของคุณ', validators=[DataRequired(), Length(min=2, max=100)])
    body = TextAreaField('แสดงความคิดเห็น', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('ส่งความคิดเห็น')