from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, TextAreaField, IntegerField, \
    FileField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    login = StringField('Login / Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Enter')


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    nickname = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    group = StringField('Group in lyceum', validators=[DataRequired()])
    submit = SubmitField('Enter')


class ForgotForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])


class PasswordResetForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=4, max=80)])