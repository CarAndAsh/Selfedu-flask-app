from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
b_app = Bootstrap(app)


links = {'/': 'Главная',
         '/materials': 'Статьи',
         '/login': 'Авторизация',
         '/about': 'О проекте'}


@app.route('/')
def main_page():
    return render_template('base.html', links=links)


@app.errorhandler(404)
def error_404(error):
    return render_template('error_404.html', links=links)


if __name__ == '__main__':
    app.run(debug=True)
