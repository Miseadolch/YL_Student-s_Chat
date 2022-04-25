from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, TextAreaField, IntegerField, \
    FileField
from wtforms.validators import DataRequired


class EditChatForm(FlaskForm):
    title = StringField('Название чата', validators=[DataRequired()])
    collaborators = StringField('Удалите или добавьте никнеймы пользователей '
                                '(при удалении пользователя из чата не забывайте удалять лишние пробелы)')
    submit = SubmitField('Изменить')
