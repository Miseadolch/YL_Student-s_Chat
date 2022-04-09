from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, TextAreaField, IntegerField, \
    FileField
from wtforms.validators import DataRequired


class EditAnketForm(FlaskForm):
    theme = StringField('Тема анкеты', validators=[DataRequired()])
    opis = TextAreaField('Расскажите, в чем заключается суть Вашей анкеты, для чего ее создаете и кого бы хотели найти',
                         validators=[DataRequired()])
    submit = SubmitField('Редактировать')
