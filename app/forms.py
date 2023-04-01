from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(message='Обязательное поле')],
        render_kw={'required': False, 'placeholder': 'Логин'})
    password = PasswordField(
        validators=[InputRequired(message='Обязательное поле')],
        render_kw={'required': False, 'placeholder': 'Пароль'})
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(message='Обязательное поле'),
                    Length(min=4, max=20, message='Имя пользователя должно состоять из 4 - 20 символов')],
        render_kw={'required': False, 'minlength': False, 'maxlength': False, 'placeholder': 'Логин'}
    )
    password = PasswordField(
        validators=[InputRequired(message='Обязательное поле'),
                    Length(min=8, max=20, message='Пароль должен состоять из 8 - 20 символов')],
        render_kw={'required': False, 'minlength': False, 'maxlength': False, 'placeholder': 'Пароль'})
    confirm_password = PasswordField(
        validators=[InputRequired(message='Обязательное поле'),
                    EqualTo('password', message='Пароли должны совпадать')],
        render_kw={'required': False, 'placeholder': 'Повторите пароль'})
    secret_key = PasswordField(
        validators=[InputRequired(message='Обязательное поле')],
        render_kw={'required': False, 'placeholder': 'Ключ разработчика'})
    submit = SubmitField('Зарегистрироваться')
