from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators, IntegerField
from flask_wtf import Form


class LoginForm(Form):
    login = StringField('Логин', [validators.InputRequired()], render_kw={"placeholder": "Логин"})
    password = PasswordField('Пароль', [validators.InputRequired()], render_kw={"placeholder": "Пароль"})
    submit = SubmitField('Войти')
