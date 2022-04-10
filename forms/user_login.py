from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, TextAreaField, IntegerField, \
    FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField('Логин / Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    nickname = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    group = StringField('Группа в лицее (пример: https://lyceum.yandex.ru/courses/539/groups/4631)',
                        validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
