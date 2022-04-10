from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, TextAreaField, IntegerField, \
    FileField
from wtforms.validators import DataRequired


class BeginChangePasswordForm(FlaskForm):
    password = PasswordField('Введите текущий пароль', validators=[DataRequired()])
    submit = SubmitField('Продолжить')
