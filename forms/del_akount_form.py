from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, TextAreaField, IntegerField, \
    FileField
from wtforms.validators import DataRequired


class DelAkountForm(FlaskForm):
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    submit = SubmitField('Удалить аккаунт')
