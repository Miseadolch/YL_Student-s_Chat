from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, TextAreaField, IntegerField, \
    FileField
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    title = StringField('Название чата', validators=[DataRequired()])
    collaborators = StringField('Введите через пробел никнеймы всех пользователей, которых хотите добавить в чат')
    submit = SubmitField('Создать')
