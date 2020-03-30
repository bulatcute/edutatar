from flask import Flask, render_template, url_for, request
from edutatar import login_edu
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        s = requests.session()
        code = login_edu(s, login, password)
        if code:
            pass
        else:
            return render_template("auth/login.html", message="Неправильный логин или пароль")
    else:
        pass

    return render_template('auth/login.html')


if __name__ == '__main__':
    app.run(debug=True)
