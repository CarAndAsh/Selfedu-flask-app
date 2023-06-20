import os
from itertools import cycle

from flask import Flask, render_template, request, flash, redirect, g, abort, make_response, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

from blog_db import FDataBase
from forms import LoginForm, RegisterForm, AddPostForm
from user_login import UserLogin
from admin.admin import admin

# TODO correct work with post URL.


blog = Flask(__name__)
blog.config['SECRET_KEY'] = 'q12we34rt56y'
blog.config['DATABASE'] = 'tmp/blog_DB.db'
blog.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1MB

b_blog = Bootstrap(blog)
blog.config.update(dict(DATABASE=os.path.join(blog.root_path, 'blog_DB.db')))

blog.register_blueprint(admin, url_prefix='/admin')
log_blog = LoginManager(blog)
log_blog.login_message = 'Пожалуйста, войдите в ваш аккаунт для просмотра статей'
log_blog.login_message_category = 'warning'
log_blog.login_view = 'login_page'


# links = {'/': 'Главная',
#          '/materials': 'Статьи',
#          '/login': 'Авторизация',
#          '/about': 'О проекте'}
@log_blog.user_loader
def load_user(user_id):
    print('loading user')
    return UserLogin().from_db(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(blog.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    cur = db.cursor()
    with open('db_scripts.sql') as file:
        scripts = file.read()
    cur.executescript(scripts)
    db.commit()
    db.close()


dbase = None


@blog.before_request
def get_dbase():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@blog.route('/')
def main_page():
    return render_template('main.html', title='Главная', links=dbase.get_menu(),
                           posts=dbase.get_posts())


@blog.route('/post/<alias>')
@login_required
def post_page(alias):
    post = dbase.get_post(alias)
    if not post:
        abort(404)
    return render_template('post.html', title='Статья', links=dbase.get_menu(), post=post)


@blog.route('/add_post', methods=['GET', 'POST'])
def add_post():
    post_form = AddPostForm()
    if post_form.validate_on_submit():
        req_data = (post_form.header.data, post_form.post_url.data, post_form.post_url.data)
        if all(req_data):
            res = dbase.add_post(*req_data)
            if not res:
                flash('Ошибка добавления статьи', 'danger')
            else:
                flash('Успешное добавление статьи', 'success')
        else:
            flash('Ошибка добавления статьи', 'danger')

    return render_template('add_post.html', links=dbase.get_menu(), title='Добавление статьи', form=post_form)


@blog.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@blog.route('/about')
def info_page():
    return render_template('about.html', links=dbase.get_menu())


@blog.route('/login', methods=['POST', 'GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('profile_page'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        user = dbase.get_user_by_email(email)
        if user and check_password_hash(user['password'], login_form.pswd.data):
            logged_user = UserLogin().create(user)
            rm = True if login_form.rm.data else False
            login_user(logged_user, remember=rm)
            return redirect(request.args.get('next') or url_for('profile_page'))
        flash('Wrong email or password', 'danger')

    return render_template('login.html', title='Авторизация', links=dbase.get_menu(), form=login_form)


@blog.route('/register', methods=['POST', 'GET'])
def register_page():
    reg_form = RegisterForm()
    if reg_form.validate_on_submit():
        username = reg_form.name.data
        email = reg_form.email.data
        pswd = reg_form.pswd.data
        pswd_hash = generate_password_hash(pswd)
        res = dbase.add_user(username, email, pswd_hash)
        if res:
            flash('Вы успешно зарегистрировались', 'success')
            return redirect(url_for('login_page'))
        else:
            flash('Ошибка при добавлении в БД', 'danger')

    return render_template('register.html', title='Регистрация', links=dbase.get_menu(), form=reg_form)


@blog.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', user_info=current_user, title='Профиль', links=dbase.get_menu())


@blog.route('/user_avatar')
@login_required
def user_avatar():
    img = current_user.get_avatar(blog)
    if not img:
        return ''

    ava = make_response(img)
    ava.headers['Content-Type'] = 'image'
    return ava


@blog.route('/avatar_upload', methods=['POST', 'GET'])
@login_required
def avatar_upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verify_ext(file.filename):
            try:
                img = file.read()
                update = dbase.update_user_avatar(img, current_user.get_id())
                if not update:
                    flash('Не удалось обновить аватар пользователя', 'danger')
                flash('Аватар пользователя успешно обновлен', 'success')
            except FileNotFoundError as err:
                flash('Ошибка чтения файла', 'danger')
        else:
            flash('Используйте *.bmp, *.jpg, *.jpeg, *.png файлы для  аватара', 'danger')
    return redirect(url_for('profile_page'))


@blog.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash('Вы успешно вышли из аккаунта', 'success')
    return redirect(url_for('login_page'))


@blog.errorhandler(404)
def error_404(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('error_404.html', title='Страница не найдена', links=dbase.get_menu())


@blog.errorhandler(413)
def error_413(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('error_404.html', title='413', links=dbase.get_menu())


if __name__ == '__main__':
    blog.config.from_object(__name__)
    blog.run()
