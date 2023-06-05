from flask import Flask, render_template, request, flash, redirect
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'q12we34rt56y'
b_app = Bootstrap(app)

links = {'/': 'Главная',
         '/materials': 'Статьи',
         '/login': 'Авторизация',
         '/about': 'О проекте'}


@app.route('/')
def main_page():
    return render_template('main.html', links=links)


@app.route('/materials')
def materials_page():
    return render_template('materials.html', links=links)


@app.route('/about')
def info_page():
    return render_template('about.html', links=links)


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        cat = 'warning'
        if username:
            cat = 'success'
            msg = f'Вы попытались зарегистрироваться или войти как {username}'
        else:
            msg = f'Пожалуйста, введите логин и пароль'
        flash(msg, cat)
    return render_template('login.html', links=links)


@app.errorhandler(404)
def error_404(error):
    return render_template('error_404.html', links=links)


if __name__ == '__main__':
    app.run(debug=True)
