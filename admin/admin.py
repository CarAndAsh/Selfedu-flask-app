import sqlite3

from flask import Blueprint, render_template, request, url_for, flash, redirect, session, g

admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates')


def admin_login():
    session['admin_logged'] = 1


def is_logged():
    return True if session.get('admin_logged') else False


def admin_logout():
    session.pop('admin_logged', None)


links = {'./': 'Главная',
         './login': 'Авторизация',
         './list-pubs': 'Статьи',
         './list-users': 'Пользователи',
         './about': 'Справка'}

db = None


@admin.before_request
def before_req():
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_req(request):
    global db
    db = None
    return request


@admin.route('/')
def main_admin():
    if not is_logged():
        return redirect(url_for('.login_admin'))
    return render_template('admin/main.html', title='Главная', menu=links)


@admin.route('/login', methods=['GET', 'POST'])
def login_admin():
    if is_logged():
        return redirect(url_for('.main_admin'))
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['pswd'] == '1234':
            admin_login()
            return redirect(url_for('.main_admin'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('admin/login.html', title='Авторизация', menu=links)


@admin.route('/list-pubs')
def list_pubs():
    if not is_logged():
        return redirect(url_for('.login_admin'))
    lst = []
    if db:
        try:
            cur = db.cursor()
            cur.execute('SELECT title, post, url FROM posts')
            lst = cur.fetchall()
        except sqlite3.Error as err:
            print('Ошибка получения статей из БД' + str(err))
        return render_template('admin/list_pubs.html', pubs=lst, title='Список статей', menu=links)


@admin.route('/list-users')
def list_users():
    if not is_logged():
        return redirect(url_for('.login_admin'))
    lst = []
    if db:
        try:
            cur = db.cursor()
            cur.execute('SELECT name, email FROM users')
            lst = cur.fetchall()
        except sqlite3.Error as err:
            print('Ошибка получения пользователей из БД' + str(err))
        return render_template('admin/list_users.html', users=lst, title='Список пользователей', menu=links)


@admin.route('/logout', methods=['GET', 'POST'])
def logout_admin():
    if not is_logged():
        return redirect(url_for('.login'))
    admin_logout()
    return redirect(url_for('.login'))


@admin.errorhandler(404)
def admin_404(error):
    return render_template('admin/404.html', title='Страница не найдена', menu=links)
