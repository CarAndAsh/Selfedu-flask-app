import os
from itertools import cycle
from flask import Flask, render_template, request, flash, redirect, g, abort, make_response, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

from blog_db import FDataBase
from user_login import UserLogin

blog = Flask(__name__)
blog.config['SECRET_KEY'] = 'q12we34rt56y'
blog.config['DATABASE'] = 'tmp/blog_DB.db'
b_blog = Bootstrap(blog)
blog.config.update(dict(DATABASE=os.path.join(blog.root_path, 'blog_DB.db')))

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
    return render_template('main.html', links=dbase.get_menu(),
                           posts=dbase.get_posts())


@blog.route('/post/<alias>')
@login_required
def post_page(alias):
    post = dbase.get_post(alias)
    if not post:
        abort(404)
    return render_template('post.html', links=dbase.get_menu(), post=post)


@blog.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        req_data = (request.form['title'], request.form['post'], request.form['url'])
        if all(req_data):
            res = dbase.add_post(*req_data)
            if not res:
                flash('Ошибка добавления статьи', 'danger')
            else:
                flash('Успешное добавление статьи', 'success')
        else:
            flash('Ошибка добавления статьи', 'danger')

    return render_template('add_post.html', links=dbase.get_menu(), title='Добавление статьи')


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
    if request.method == 'POST':
        email = request.form['e-mail']
        user = dbase.get_user_by_email(email)
        if user and check_password_hash(user['password'], request.form['password']):
            logged_user = UserLogin().create(user)
            rm = True if request.form.get('remember') else False
            login_user(logged_user, remember=rm)
            return redirect(request.args.get('next') or url_for('profile_page'))
        flash('Wrong email or password', 'danger')

    return render_template('login.html', links=dbase.get_menu())


@blog.route('/register', methods=['POST', 'GET'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['e-mail']
        pswd = request.form['password']
        if username and email and pswd and (pswd == request.form['password_sbmt']):
            pswd_hash = generate_password_hash(pswd)
            res = dbase.add_user(username, email, pswd_hash)
            if res:
                flash('Вы успешно зарегистрировались', 'success')
                return redirect(url_for('login_page'))
            else:
                flash('Ошибка при добавлении в БД', 'danger')
        else:
            flash('Неверно заполнены поля', 'danger')
    return render_template('register.html', links=dbase.get_menu())


@blog.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', user_info=current_user.get_id(), links=dbase.get_menu())


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
    return render_template('error_404.html', links=dbase.get_menu())


if __name__ == '__main__':
    blog.config.from_object(__name__)
    blog.run()
