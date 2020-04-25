import os
import dotenv
import requests
from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_app.edutatar import (
    check_login,
    get_diary,
    get_home_params,
    login_edu,
    my_facultatives,
    my_stars,
    facultative_info,
)
from flask_app.forms import LoginForm

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


sessions = {}

for user in User.query.all():
    s = requests.Session()
    login_edu(s, user.login, user.password)
    sessions[user.login] = s

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
    return redirect(url_for('diary'))


@application.route('/marks', methods=['GET'])
@login_required
def marks():
    data = {'login': current_user.login,
            'name': current_user.name, 'avatar': current_user.avatar}
    stars = my_stars(sessions[current_user.login])
    return render_template('marks.html', data=data, stars=stars[0], term=stars[1])


@application.route('/marks/<int:term>', methods=['GET'])
@login_required
def marks_with_term(term):
    data = {'login': current_user.login,
            'name': current_user.name, 'avatar': current_user.avatar}
    stars = my_stars(sessions[current_user.login], term=term)
    return render_template('marks.html', data=data, stars=stars[0], term=str(stars[1]))


@application.route('/facultatives', methods=['GET'])
@login_required
def facultatives():
    data = {'login': current_user.login,
            'name': current_user.name, 'avatar': current_user.avatar}
    facs = my_facultatives(sessions[current_user.login])
    return render_template('facultatives.html', data=data, facs=facs)


@application.route('/facultative/<int:index>')
@login_required
def facultative(index):
    data = {'login': current_user.login,
            'name': current_user.name, 'avatar': current_user.avatar}
    info = facultative_info(sessions[current_user.login], index=index)
    return render_template('facultative.html', data=data, info=info)


@application.route('/diary')
@login_required
def diary():
    data = {'login': current_user.login,
            'name': current_user.name, 'avatar': current_user.avatar}
    diary = get_diary(sessions[current_user.login])
    return render_template('diary.html', data=data, diary=diary[0], next_page=diary[1], prev_page=diary[2])


@application.route('/diary/<int:date>')
@login_required
def diary_with_date(date):
    data = {'login': current_user.login,
            'name': current_user.name, 'avatar': current_user.avatar}
    diary = get_diary(
        sessions[current_user.login], url=f'https://edu.tatar.ru/user/diary/week?date={date}')
    return render_template('diary.html', data=data, diary=diary[0], next_page=diary[1], prev_page=diary[2])


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        s = requests.Session()
        login_edu(s, login, password)
        code = check_login(s)
        next = request.args.get('next')
        if code:
            user = User.query.filter_by(login=form.login.data).first()
            if not user:
                user_data = get_home_params(s)
                if not user_data['avatar']:
                    user_data['avatar'] = url_for(
                        'static', filename='img/grayman.png')
                new_user = User(
                    login=form.login.data, password=password, name=user_data[
                        'name'], avatar=user_data['avatar']
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                login_edu(s, login, password)
                sessions[new_user.login] = s
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
