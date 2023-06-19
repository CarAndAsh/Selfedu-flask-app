from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, URLField, TextAreaField
from wtforms.validators import Email, Length, DataRequired, URL, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email : ', validators=[DataRequired(), Email(message='Вы ввели неверный e-mail')])
    pswd = PasswordField('Пароль : ', validators=[DataRequired(), Length(min=4, max=10,
                                                                         message='Длина пароля должна быть от 4 до 10 символов')])
    rm = BooleanField('Запомнить меня ')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Логин : ')
    email = StringField('Email : ', validators=[DataRequired(), Email(
        message='Введенный e-mail не соответсвует образцу exaple@email.com')])
    pswd = PasswordField('Пароль : ', validators=[DataRequired(), Length(min=4, max=10,
                                                                         message='Длина пароля должна быть от 4 до 10 символов')])
    submit_pswd = PasswordField('Повторите пароль : ', validators=[DataRequired(), EqualTo('pswd', message='Пароли не совпадают')])
    submit = SubmitField('Зарегистрироваться')


class AddPostForm(FlaskForm):
    header = StringField('Заголовок статьи : ', validators=[DataRequired('Введите заголовок статьи')])
    post_url = URLField('URL статьи : ', validators=[URL()])
    post = TextAreaField('Текст статьи : ', validators=[])
    submit = SubmitField('Добавить статью')
