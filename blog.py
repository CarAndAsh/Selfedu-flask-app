import os
from itertools import cycle
from flask import Flask, render_template, request, flash, redirect, g, abort, make_response, url_for
from flask_bootstrap import Bootstrap
import sqlite3

from werkzeug.security import generate_password_hash

from blog_db import FDataBase

blog = Flask(__name__)
blog.config['SECRET_KEY'] = 'q12we34rt56y'
blog.config['DATABASE'] = 'tmp/blog_DB.db'
b_blog = Bootstrap(blog)
blog.config.update(dict(DATABASE=os.path.join(blog.root_path, 'blog_DB.db')))


# links = {'/': 'Главная',
#          '/materials': 'Статьи',
#          '/login': 'Авторизация',
#          '/about': 'О проекте'}


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
    login = ''
    if request.method == 'POST':
        make_response().set_cookie('log_as', max_age=0)

        cat = 'warning'
        if (username := request.form['username']) and (login := request.cookies.get('log_as')):
            cat = 'success'
            msg = f'Вы попытались зарегистрироваться или войти как {username}'
            if request.form.get('remember'):
                msg += ' и запомнить этого пользователя'
        else:
            msg = f'Пожалуйста, введите логин и пароль'
        flash(msg, cat)

        make_response().set_cookie('log_as', f'{username}')

    return render_template('login.html', links=dbase.get_menu(), login=login)


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


@blog.errorhandler(404)
def error_404(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('error_404.html', links=dbase.get_menu())


if __name__ == '__main__':
    blog.config.from_object(__name__)
    blog.run()
