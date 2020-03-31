from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_app.forms import LoginForm
from flask_app.edutatar import login_edu, get_home_params
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import dotenv
import os

dotenv.load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# region DATABASE SETUP

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False, unique=True)
    avatar = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


db.create_all()

# endregion

# region LOGIN SETUP

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# endregion

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        s = requests.session()
        code = login_edu(s, login, password)
        next = request.args.get('next')
        if code:
            user = User.query.filter_by(login=form.login.data).first()
            if not user:
                password_hashed = generate_password_hash(form.password.data, method='sha256')
                user_data = get_home_params(s)
                if not user_data['avatar']:
                    user_data['avatar'] = url_for('static', filename='img/grayman.png')
                new_user = User(
                    login=form.login.data, password=password_hashed, name=user_data['name'], avatar=user_data['avatar']
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
            else:
                login_user(user, remember=True)
            return redirect(next or url_for('index'))
        else:
            return render_template('auth/login.html', form=form, message="Неправильный логин или пароль")

    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
