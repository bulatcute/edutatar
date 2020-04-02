from flask import Flask, render_template, redirect, url_for, request, make_response, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
from edutatar import login_edu, get_home_params, my_stars, check_login, my_facultatives
import requests
import dotenv
import os

dotenv.load_dotenv()

application = Flask(__name__)

application.config['SECRET_KEY'] = os.environ['SECRET_KEY']
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# region DATABASE SETUP

application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(application)


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
login_manager.init_app(application)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

# endregion

@application.route('/sw.js', methods=['GET'])
def sw():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'application/javascript'
    return response


@application.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('marks'))


@application.route('/marks', methods=['GET'])
@login_required
def marks():
    data = {'login': current_user.login, 'name': current_user.name, 'avatar': current_user.avatar}
    s = requests.session()
    login_edu(s, data['login'], current_user.password)
    stars = my_stars(s)
    return render_template('marks.html', data=data, stars=stars)


@application.route('/facultatives', methods=['GET'])
@login_required
def facultatives():
    data = {'login': current_user.login, 'name': current_user.name, 'avatar': current_user.avatar}
    s = requests.session()
    login_edu(s, data['login'], current_user.password)
    facs = my_facultatives(s)
    return render_template('facultatives.html', data=data, facs=facs)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        s = requests.session()
        login_edu(s, login, password)
        code = check_login(s)
        next = request.args.get('next')
        if code:
            user = User.query.filter_by(login=form.login.data).first()
            if not user:
                user_data = get_home_params(s)
                if not user_data['avatar']:
                    user_data['avatar'] = url_for('static', filename='img/grayman.png')
                new_user = User(
                    login=form.login.data, password=password, name=user_data['name'], avatar=user_data['avatar']
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


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    application.run(debug=True)
