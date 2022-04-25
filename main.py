import io
import datetime
import os
from flask_socketio import SocketIO, send
from PIL import Image
from flask import Flask
from flask import render_template, request, redirect, abort, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.chats import Chats
from data.ankets import Ankets
from data import users_api
from forms.del_akount_form import DelAkountForm
from forms.edit_anket_form import EditAnketForm
from forms.begin_change_password_form import BeginChangePasswordForm
from forms.change_password_form import ChangePasswordForm
from forms.change_group_form import ChangeGroupForm
from forms.change_nick import ChangeNickForm
from forms.anket_form import AnketForm
from forms.chats_form import ChatForm
from forms.edit_chat_from import EditChatForm
from data.messages import Messages
from data.users import User
from forms.message_form import MessageForm
from forms.user_login import RegisterForm, LoginForm

db_session.global_init("db/students_chat.db")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
socketio = SocketIO(app, cors_allowed_origins='*')

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('error404.html'), 404


@app.errorhandler(401)
def unauthorized(error):
    return render_template('error401.html'), 401


@app.errorhandler(500)
def bad_request(error):
    return render_template('error500.html'), 500


def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/chat/<int:chat_id>/<int:user_id>", methods=['POST', 'GET'])
def own_chat(chat_id, user_id):
    form = MessageForm()
    db_sess = db_session.create_session()
    chat = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id).first()
    except Exception:
        return redirect('/logout')
    try:
        author = chat.collaborators.split(' ')[0]
    except Exception:
        return redirect('/chat/1/{}'.format(current_user.id))
    user.chat_now = chat.id
    db_sess.commit()
    if author != "all":
        author = int(author)
    else:
        author = -1
    messages = db_sess.query(Messages).filter(Messages.chat_id == chat.id).all()
    user_chats = db_sess.query(Chats).filter(
        (Chats.collaborators.like("%{}%".format(current_user.id))) | (
            Chats.collaborators.like("%all%"))).all()

    if len(str(datetime.datetime.now().minute)) == 1:
        minut = '0' + str(datetime.datetime.now().minute)
    else:
        minut = str(datetime.datetime.now().minute)
    if len(str(datetime.datetime.now().hour)) == 1:
        hour = '0' + str(datetime.datetime.now().hour)
    else:
        hour = str(datetime.datetime.now().hour)

    @socketio.on('message', namespace='/chat/{}'.format(chat.id))
    def handleMessage(msg):
        if msg.split('#')[0] == 'this soob will be deleted hash 8350e5a3e24c153df2275c9f80692773':
            message = db_sess.query(Messages).filter(Messages.id == msg.split('#')[1]).first()
            db_sess.delete(message)
            db_sess.commit()
            messages = db_sess.query(Messages).filter(Messages.chat_id == chat.id).all()
        else:
            mess = Messages()
            mess.chat_id = chat.id
            mess.user_id = current_user.id
            mess.text = msg
            if len(str(datetime.datetime.now().minute)) == 1:
                minut = '0' + str(datetime.datetime.now().minute)
            else:
                minut = str(datetime.datetime.now().minute)
            if len(str(datetime.datetime.now().hour)) == 1:
                hour = '0' + str(datetime.datetime.now().hour)
            else:
                hour = str(datetime.datetime.now().hour)
            mess.send_time = hour + ':' + minut
            db_sess.add(mess)
            db_sess.commit()
            messages = db_sess.query(Messages).filter(Messages.chat_id == chat.id).all()
        if len(messages) == 0:
            if len(db_sess.query(Messages).filter().all()) == 0:
                last = 1
            else:
                last = db_sess.query(Messages).filter().all()[-1].id + 1
        else:
            last = db_sess.query(Messages).filter(Messages.chat_id == chat.id).all()[-1].id
        send([msg, last, current_user.id], broadcast=True)

    return render_template("chat.html", form=form, photo=user.id, messages=messages, title=chat.title,
                           user_chats=user_chats, chat_id=chat_id, author=author,
                           send_t=hour + ':' + minut)


@app.route('/profile/<int:chat_id>/<int:user_id>')
def profile(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('profile.html', title="Профиль", chat_id=chat_id, photo=user.id)


@app.route('/another_profile/<int:chat_id>/<int:user_id>')
def another_profile(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    ankets = db_sess.query(Ankets).filter(Ankets.author == user.id).all()[::-1]
    ankets.sort(key=lambda x: x.modified_date)
    ankets.sort(key=lambda x: x.group == user.group)
    ankets = ankets[::-1]
    ankets_first = []
    ankets_second = []
    p = 0
    for i in ankets:
        if p % 2 == 0:
            nick = db_sess.query(User).filter(User.id == int(i.author)).first().nickname
            ankets_first.append([nick, i])
        else:
            nick = db_sess.query(User).filter(User.id == int(i.author)).first().nickname
            ankets_second.append([nick, i])
        p += 1
    return render_template('another_profile.html', title="Профиль", chat_id=chat_id, photo=current_user.id, user=user,
                           ankets_first=ankets_first, ankets_second=ankets_second, prof_photo=user.id,
                           lenankt=len(ankets_first) + len(ankets_second))


@app.route('/register', methods=['POST', 'GET'])
def reg_users():
    db_sess = db_session.create_session()
    form = RegisterForm()
    user_first = db_sess.query(User).filter(User.id == 1).first()
    prov = 'abcdefghijklmnopqrstuvwxyz0123456789_-+=*^/()&?.:%;$№#"@!,~'
    prov_pass_letters = 'abcdefghijklmnopqrstuvwxyz'
    prov_pass_up_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    prov_pass_chis = '0123456789'
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        shet_letters = 0
        shet_up_letters = 0
        shet_pass_chis = 0
        for i in form.password.data:
            if i in prov_pass_letters:
                shet_letters += 1
            if i in prov_pass_up_letters:
                shet_up_letters += 1
            if i in prov_pass_chis:
                shet_pass_chis += 1
        if (shet_letters == 0) or (shet_up_letters == 0) or (shet_pass_chis == 0) or len(form.password.data) < 8:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароль не надежный. Пароль должен содержать минимум 8 символов, состоять "
                                           "только из латинских букв, иметь как минимум одну заглавную букву, "
                                           "одну прописную букву и одну цифру")
        if db_sess.query(User).filter((User.email == form.email.data) | (User.nickname == form.nickname.data)).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже существует")
        if ' ' in form.nickname.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="В никнеймах нельзя использовать пробел")
        if len(form.nickname.data) > 30:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Максимальная длина никнейма 30 символов")
        for i in form.nickname.data:
            if i.lower() not in prov:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message='Никнейм содержит недопустимые символы (допустимые '
                                               'символы abcdefghijklmnopqrstuvwxyz0123456789_-+=*^/()&?.:%;$№#"@!,~')
        if len(form.group.data.split("/")[-4:]) != 4 or form.group.data.split("/")[-4:][0] != "courses" or \
                form.group.data.split("/")[-4:][2] != "groups":
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Убедитесь, что группа введена корректно. "
                                                      "Пример окончания введенной ссылки courses/539/groups/4631")
        user = User(
            email=form.email.data,
            nickname=form.nickname.data,
            surname=form.surname.data,
            name=form.name.data,
            group="/".join(form.group.data.split("/")[-4:]),
            photo=user_first.photo
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/load_ava/{}'.format(int(user.id)))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/load_ava/<int:user_id>', methods=['GET', 'POST'])
def load_ava(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter((User.id == user_id)).first()
    user_first = db_sess.query(User).filter(User.id == 1).first()
    if request.method == 'POST':
        photo = request.files['file']
        if photo.filename != '':
            photo.save('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            user.photo = convert_to_binary_data('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            db_sess.commit()
        else:
            photo = Image.open(io.BytesIO(user_first.photo))
            photo.save('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            user.photo = convert_to_binary_data('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            db_sess.commit()
        return redirect('/login')
    return render_template('load_ava.html', title='Аватарка')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter((User.email == form.login.data) | (User.nickname == form.login.data)).first()
        if user:
            if user.sing_in == 0:
                user.sing_in = 1
                os.remove('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            if user.check_password(form.password.data):
                user.sing_in = 1
                db_sess.commit()
                login_user(user, remember=form.remember_me.data)
                photo = Image.open(io.BytesIO(user.photo))
                photo.save('static/img/photo_for_ava_for_user{}.png'.format(user.id))
                return redirect("/chat/1/{}".format(user.id))
            try:
                return render_template('login.html', message="Неверный логин или пароль", form=form,
                                       photo=current_user.id)
            except Exception:
                return render_template('login.html', message="Неверный логин или пароль", form=form)
        else:
            try:
                return render_template('login.html', message="Такого пользователя не существует", form=form,
                                       photo=current_user.id)
            except Exception:
                return render_template('login.html', message="Такого пользователя не существует", form=form)
    try:
        return render_template('login.html', title='Авторизация', form=form, photo=current_user.id)
    except Exception:
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/ankets/<int:chat_id>/<int:user_id>', methods=['GET'])
def ankets(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    ankets = db_sess.query(Ankets).all()[::-1]
    ankets.sort(key=lambda x: x.modified_date)
    ankets.sort(key=lambda x: x.group == user.group)
    ankets = ankets[::-1]
    ankets_first = []
    ankets_second = []
    p = 0
    for i in ankets:
        if p % 2 == 0:
            nick = db_sess.query(User).filter(User.id == int(i.author)).first().nickname
            ankets_first.append([nick, i])
        else:
            nick = db_sess.query(User).filter(User.id == int(i.author)).first().nickname
            ankets_second.append([nick, i])
        p += 1
    return render_template('ankets.html', title='Анкеты', photo=user.id, chat_id=chat_id, ankets_first=ankets_first,
                           ankets_second=ankets_second, lenankt=len(ankets_first) + len(ankets_second))


@app.route('/anketa/<int:anketa_id>/<int:chat_id>/<int:user_id>', methods=['POST', 'GET'])
def anketa(anketa_id, chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    anketa = db_sess.query(Ankets).filter(Ankets.id == anketa_id).first()
    author = db_sess.query(User).filter(User.id == int(anketa.author)).first()
    return render_template('anketa.html', photo=user.id, anketa=anketa, chat_id=chat_id,
                           author=author.nickname, photo_ankt=author.id)


@app.route('/create_chat/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def create_chat(chat_id, user_id):
    form = ChatForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        chat = Chats()
        print(len(form.title.data))
        if len(form.title.data) > 60:
            return render_template("create_chat.html", chat_id=chat_id, title="Создание чата", photo=user.id, form=form,
                                   message="Слишком длинное название чата")
        else:
            chat.title = form.title.data
        k = ''
        if form.collaborators.data.split(' ')[0] != '':
            if len(set(form.collaborators.data.split(' '))) == len(form.collaborators.data.split(' ')):
                for i in set(form.collaborators.data.split(' ')):
                    if db_sess.query(User).filter(User.nickname == i).first():
                        if db_sess.query(User).filter(User.nickname == i).first().id != user.id:
                            k += str(db_sess.query(User).filter(User.nickname == i).first().id) + ' '
                        else:
                            return render_template("create_chat.html", chat_id=chat_id, title="Создание чата",
                                                   photo=user.id,
                                                   form=form,
                                                   message="Создатель чата добавляется в чат автоматически")
                    else:
                        if i == '':
                            return render_template("create_chat.html", chat_id=chat_id, title="Создание чата",
                                                   photo=user.id, form=form,
                                                   message="Похоже, вы добавили лишний пробел")
                        else:
                            return render_template("create_chat.html", chat_id=chat_id, title="Создание чата",
                                                   photo=user.id, form=form,
                                                   message="Пользователя с никнеймом {} не существует".format(i))
            else:
                if form.collaborators.data.split(' ').count('') == 0:
                    return render_template("create_chat.html", chat_id=chat_id, title="Создание чата",
                                           photo=user.id, form=form,
                                           message="Некоторые пользователи добавлены повторно")
                else:
                    return render_template("create_chat.html", chat_id=chat_id, title="Создание чата",
                                           photo=user.id, form=form,
                                           message="Похоже, вы добавили лишний пробел")
        else:
            if len(form.collaborators.data.split(' ')) > 1:
                return render_template("create_chat.html", chat_id=chat_id, title="Создание чата",
                                       photo=user.id, form=form,
                                       message="Похоже, вы добавили лишний пробел")
        k = str(user.id) + ' ' + k[:-1]
        if k[-1] == ' ':
            k = k[:-1]
        chat.collaborators = k
        db_sess.add(chat)
        db_sess.commit()
        return redirect("/chat/{}/{}".format(chat.id, user.id))
    return render_template("create_chat.html", form=form, photo=user.id, chat_id=chat_id, title="Создание чата")


@app.route('/edit_chat/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_chat(chat_id, user_id):
    form = EditChatForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    chat = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    if request.method == "GET":
        form.title.data = chat.title
        k = ''
        if chat.collaborators.split(' ')[0] != '':
            for i in chat.collaborators.split(' '):
                if int(i) != current_user.id:
                    k += str(db_sess.query(User).filter(User.id == int(i)).first().nickname) + ' '
            if k != '' and k[-1] == ' ':
                k = k[:-1]
        form.collaborators.data = k
        if chat:
            if len(form.title.data) > 60:
                return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата", photo=user.id,
                                       form=form,
                                       message="Слишком длинное название чата")
            else:
                chat.title = form.title.data
            k = ''
            if form.collaborators.data.split(' ')[0] != '':
                for i in form.collaborators.data.split(' '):
                    if db_sess.query(User).filter(User.nickname == i).first():
                        if db_sess.query(User).filter(User.nickname == i).first().id != user.id:
                            k += str(db_sess.query(User).filter(User.nickname == i).first().id) + ' '
                        else:
                            return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                                   photo=user.id,
                                                   form=form,
                                                   message="Создатель чата добавляется в чат автоматически")
                    else:
                        if i == '':
                            return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                                   photo=user.id, form=form,
                                                   message="Похоже, вы добавили лишний пробел")
                        else:
                            return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                                   photo=user.id, form=form,
                                                   message="Пользователя с никнеймом {} не существует".format(i))
            k = str(user.id) + ' ' + k[:-1]
            if k[-1] == ' ':
                k = k[:-1]
            chat.collaborators = k
        else:
            abort(404)
    if form.validate_on_submit():
        if chat:
            if len(form.title.data) > 60:
                return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата", photo=user.id,
                                       form=form,
                                       message="Слишком длинное название чата")
            else:
                chat.title = form.title.data
            k = ''
            if form.collaborators.data.split(' ')[0] != '':
                if len(set(form.collaborators.data.split(' '))) == len(form.collaborators.data.split(' ')):
                    for i in set(form.collaborators.data.split(' ')):
                        if db_sess.query(User).filter(User.nickname == i).first():
                            if db_sess.query(User).filter(User.nickname == i).first().id != user.id:
                                k += str(db_sess.query(User).filter(User.nickname == i).first().id) + ' '
                            else:
                                return render_template("edit_chat.html", chat_id=chat_id, title="Создание чата",
                                                       photo=user.id,
                                                       form=form,
                                                       message="Создатель чата добавляется в чат автоматически")
                        else:
                            if i == '':
                                return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                                       photo=user.id, form=form,
                                                       message="Похоже, вы добавили лишний пробел")
                            else:
                                return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                                       photo=user.id, form=form,
                                                       message="Пользователя с никнеймом {} не существует".format(i))
                else:
                    if form.collaborators.data.split(' ').count('') == 0:
                        return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                               photo=user.id, form=form,
                                               message="Некоторые пользователи добавлены повторно")
                    else:
                        return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                               photo=user.id, form=form,
                                               message="Похоже, вы добавили лишний пробел")
            else:
                if len(form.collaborators.data) > 0:
                    return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
                                           photo=user.id, form=form,
                                           message="Похоже, вы добавили лишний пробел")
            k = str(user.id) + ' ' + k[:-1]
            if k[-1] == ' ':
                k = k[:-1]
            chat.collaborators = k
            db_sess.commit()
            return redirect("/chat/{}/{}".format(chat.id, user.id))
        else:
            abort(404)
    return render_template("edit_chat.html", chat_id=chat_id, title="Создание чата", photo=user.id, form=form)


@app.route('/yes_no_chat/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_no_chat(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template("yes_no_chat.html", photo=user.id, chat_id=chat_id, title="Подтверждение удаления чата")


@app.route('/yes-del/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_del(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    chat = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    messages = db_sess.query(Messages).filter(Messages.chat_id == chat_id).all()
    for i in messages:
        db_sess.delete(i)
        db_sess.commit()
    if chat:
        db_sess.delete(chat)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/chat/1/{}".format(user.id))


@app.route('/yes_no_exit/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_no_exit(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template("yes_no_exit.html", photo=user.id, chat_id=chat_id, title="Подтверждение выхода из чата")


@app.route('/yes-exit/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_exit(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    chat = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    if chat:
        k = ''
        for i in chat.collaborators.split(' '):
            if int(i) != current_user.id:
                k = k + i + ' '
        k = k[:-1]
        chat.collaborators = k
        db_sess.commit()
    else:
        abort(404)
    return redirect("/chat/1/{}".format(user.id))


@app.route('/create-anket/<int:chat_id>/<int:user_id>', methods=['POST', 'GET'])
def create_anket(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = AnketForm()
    if form.validate_on_submit():
        if (len(form.theme.data) == 0) or (len(form.theme.data) > 60) or (form.theme.data[0] == ' '):
            if form.opis.data[0] == ' ' or form.opis.data[0] == '':
                return render_template('create_anket.html', title='Создание анкеты', form=form, chat_id=chat_id,
                                       photo=user.id, message="Минимально количество символов в теме: 1, "
                                                              "Заполните поле описания анкеты")
            return render_template('create_anket.html', title='Создание анкеты', form=form, chat_id=chat_id,
                                   photo=user.id, message="Минимально количество символов в теме: 1, "
                                                          "Максимальное количество символов в теме: 60")
        else:
            db_sess = db_session.create_session()
            anketa = Ankets(
                author=user.id,
                theme=form.theme.data,
                group=user.group,
                opis=form.opis.data
            )
            db_sess.add(anketa)
            db_sess.commit()
            return redirect("/ankets/{}/{}".format(chat_id, user_id))
    return render_template('create_anket.html', title='Создание анкеты', form=form, chat_id=chat_id, photo=user.id)


@app.route('/yes_no_akount/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_no_akount(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = DelAkountForm()
    if form.validate_on_submit():
        if user.check_password(form.password.data):
            return redirect("/del-akount/{}".format(user_id))
        else:
            return render_template("yes_no_akount.html", photo=user.id, chat_id=chat_id,
                                   title="Подтверждение удаления аккаунта", message="Неверный пароль", form=form)
    return render_template("yes_no_akount.html", photo=user.id, chat_id=chat_id,
                           title="Подтверждение удаления аккаунта", form=form)


@app.route('/yes_no_ex_ak/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_no_ex_ak(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template("yes_no_ex_ak.html", photo=user.id, chat_id=chat_id,
                           title="Подтверждение выхода из аккаунта")


@app.route('/change_ava/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def change_ava(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter((User.id == user_id)).first()
    user_first = db_sess.query(User).filter(User.id == user_id).first()
    if request.method == 'POST':
        photo = request.files['file']
        if photo.filename != '':
            photo.save('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            user.photo = convert_to_binary_data('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            db_sess.commit()
        else:
            photo = Image.open(io.BytesIO(user_first.photo))
            photo.save('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            user.photo = convert_to_binary_data('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
            db_sess.commit()
        return redirect('/yes_change_ava/{}/{}'.format(chat_id, user_id))
    return render_template("change_ava.html", photo=user.id, chat_id=chat_id, title="Смена аватарки")


@app.route('/yes_change_ava/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_change_ava(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    os.remove('static/img/etot_parol_nikto_ne_uznaet{}.png'.format(user.id))
    photo = Image.open(io.BytesIO(user.photo))
    photo.save('static/img/photo_for_ava_for_user{}.png'.format(user.id))
    return redirect('/profile/{}/{}'.format(chat_id, user_id))


@app.route('/change_nick/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def change_nick(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    prov = 'abcdefghijklmnopqrstuvwxyz0123456789_-+=*^/()&?.:%;$№#"@!,~'
    form = ChangeNickForm()
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.nickname == form.login.data).first():
            return render_template("change_nick.html", photo=user.id, chat_id=chat_id, title="Смена никнейма",
                                   form=form, message="Такой пользователь уже существует")
        if ' ' in form.login.data:
            return render_template("change_nick.html", photo=user.id, chat_id=chat_id, title="Смена никнейма",
                                   form=form, message="В никнеймах нельзя использовать пробел")
        if len(form.login.data) > 30:
            return render_template('change_nick.html', title='Смена никнейма', photo=user.id, chat_id=chat_id,
                                   form=form, message="Максимальная длина никнейма 30 символов")
        for i in form.login.data:
            if i.lower() not in prov:
                return render_template('change_nick.html', title='Смена никнейма',
                                       form=form, photo=user.id, chat_id=chat_id,
                                       message='Никнейм содержит недопустимые символы (допустимые '
                                               'символы abcdefghijklmnopqrstuvwxyz0123456789_-+=*^/()&?.:%;$№#"@!,~')
        if user.check_password(form.password.data):
            user.nickname = form.login.data
            db_sess.commit()
            return redirect('/profile/{}/{}'.format(chat_id, user_id))
        return render_template("change_nick.html", photo=user.id, chat_id=chat_id, title="Смена никнейма", form=form,
                               message="Неверный логин или пароль")
    return render_template("change_nick.html", photo=user.id, chat_id=chat_id, title="Смена никнейма", form=form)


@app.route('/begin_change_password/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def begin_change_password(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = BeginChangePasswordForm()
    if form.validate_on_submit():
        if user.check_password(form.password.data):
            return redirect('/change_password/{}/{}'.format(chat_id, user_id))
        return render_template("begin_change_password.html", photo=user.id, chat_id=chat_id, title="Смена пароля",
                               form=form,
                               message="Неверный пароль")
    return render_template("begin_change_password.html", photo=user.id, chat_id=chat_id, title="Смена пароля",
                           form=form)


@app.route('/change_password/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def change_password(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = ChangePasswordForm()
    prov_pass_letters = 'abcdefghijklmnopqrstuvwxyz'
    prov_pass_up_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    prov_pass_chis = '0123456789'
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("change_password.html", photo=user.id, chat_id=chat_id, title="Смена пароля",
                                   form=form, message="Пароли не совпадают")
        shet_letters = 0
        shet_up_letters = 0
        shet_pass_chis = 0
        for i in form.password.data:
            if i in prov_pass_letters:
                shet_letters += 1
            if i in prov_pass_up_letters:
                shet_up_letters += 1
            if i in prov_pass_chis:
                shet_pass_chis += 1
        if (shet_letters == 0) or (shet_up_letters == 0) or (shet_pass_chis == 0) or len(form.password.data) < 8:
            return render_template("change_password.html", title="Смена пароля",
                                   form=form, photo=user.id, chat_id=chat_id,
                                   message="Пароль не надежный. Пароль должен содержать минимум 8 символов, состоять "
                                           "только из латинских букв, иметь как минимум одну заглавную букву, "
                                           "одну прописную букву и одну цифру")
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect('/logout')
    return render_template("change_password.html", photo=user.id, chat_id=chat_id, title="Смена пароля", form=form)


@app.route('/del-akount/<int:user_id>', methods=['GET', 'POST'])
@login_required
def del_akount(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    chats = db_sess.query(Chats).filter(Chats.collaborators.like("%{}%".format(str(user.id)))).all()
    ankets = db_sess.query(Ankets).filter(Ankets.author == user_id).all()
    if user:
        for i in chats:
            k = i.collaborators.split(' ')
            k.remove(str(user.id))
            i.collaborators = ' '.join(k)
        for i in ankets:
            db_sess.delete(i)
        os.remove('static/img/photo_for_ava_for_user{}.png'.format(user.id))
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/login")


@app.route('/change_ankets/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def change_ankets(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    ankets = db_sess.query(Ankets).filter(Ankets.author == user_id).all()[::-1]
    ankets_first = []
    ankets_second = []
    p = 0
    for i in ankets:
        if p % 2 == 0:
            ankets_first.append(i)
        else:
            ankets_second.append(i)
        p += 1
    return render_template("change_ankets.html", photo=user.id, chat_id=chat_id, title="Управление анкетами",
                           ankets_first=ankets_first, ankets_second=ankets_second,
                           lenankt=len(ankets_first) + len(ankets_second))


@app.route('/yes_no_del_ankt/<int:anket_id>/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_no_del_ankt(anket_id, chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template("yes_no_del_ankt.html", photo=user.id, chat_id=chat_id, anket_id=anket_id,
                           title="Подтверждение удаления анкеты")


@app.route('/yes_del_ankt/<int:anket_id>/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def yes_del_ankt(anket_id, chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    anket = db_sess.query(Ankets).filter(Ankets.id == anket_id).first()
    if anket:
        db_sess.delete(anket)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/change_ankets/{}/{}".format(chat_id, user.id))


@app.route('/edit_ankt/<int:anket_id>/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def edit_ankt(anket_id, chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    anket = db_sess.query(Ankets).filter(Ankets.id == anket_id).first()
    form = EditAnketForm()
    if request.method == "GET":
        form.theme.data = anket.theme
        form.opis.data = anket.opis
        if (len(form.theme.data) == 0) or (len(form.theme.data) > 60) or (form.theme.data[0] == ' '):
            if form.opis.data[0] == ' ' or form.opis.data[0] == '':
                return render_template("edit_ankt.html", photo=user.id, chat_id=chat_id, anket_id=anket_id,
                                       title="Редактирование анкеты",
                                       message="Минимально количество символов в теме: 1, "
                                               "Заполните поле описания анкеты", form=form)
            return render_template("edit_ankt.html", photo=user.id, chat_id=chat_id, anket_id=anket_id,
                                   title="Редактирование анкеты",
                                   message="Минимально количество символов в теме: 1, "
                                           "Максимальное количество символов в теме: 30", form=form)
        else:
            anket.theme = form.theme.data
            anket.opis = form.opis.data
    if form.validate_on_submit():
        if (len(form.theme.data) == 0) or (len(form.theme.data) > 60) or (form.theme.data[0] == ' '):
            if form.opis.data[0] == ' ' or form.opis.data[0] == '':
                return render_template("edit_ankt.html", photo=user.id, chat_id=chat_id, anket_id=anket_id,
                                       title="Редактирование анкеты",
                                       message="Минимально количество символов в теме: 1, "
                                               "Заполните поле описания анкеты", form=form)
            return render_template("edit_ankt.html", photo=user.id, chat_id=chat_id, anket_id=anket_id,
                                   title="Редактирование анкеты",
                                   message="Минимально количество символов в теме: 1, "
                                           "Максимальное количество символов в теме: 30", form=form)
        else:
            anket.theme = form.theme.data
            anket.opis = form.opis.data
            db_sess.commit()
            return redirect("/change_ankets/{}/{}".format(chat_id, user.id))
    return render_template("edit_ankt.html", photo=user.id, chat_id=chat_id, anket_id=anket_id,
                           title="Редактирование анкеты", form=form)


@app.route('/change_group/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
def change_group(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = ChangeGroupForm()
    if form.validate_on_submit():
        if user.check_password(form.password.data):
            if len(form.group.data.split("/")[-4:]) != 4 or form.group.data.split("/")[-4:][0] != "courses" or \
                    form.group.data.split("/")[-4:][2] != "groups":
                return render_template('change_group.html', title='Смена группы обучения',
                                       form=form, message="Убедитесь, что группа введена корректно. "
                                                          "Пример окончания введенной ссылки courses/539/groups/4631")
            else:
                user.group = "/".join(form.group.data.split("/")[-4:])
                db_sess.commit()
                return redirect('/profile/{}/{}'.format(chat_id, user_id))
        return render_template("change_group.html", photo=user.id, chat_id=chat_id, title="Смена группы обучения",
                               form=form, message="Неверный пароль")
    return render_template("change_group.html", photo=user.id, chat_id=chat_id, title="Смена группы обучения",
                           form=form)


@app.route('/auto_create_chat/<int:anket_id>/<int:first_id>/<int:second_id>', methods=['GET', 'POST'])
@login_required
def auto_create_chat(anket_id, first_id, second_id):
    db_sess = db_session.create_session()
    anketa = db_sess.query(Ankets).filter(Ankets.id == anket_id).first()
    user_first = db_sess.query(User).filter(User.id == first_id).first()
    user_second = db_sess.query(User).filter(User.id == second_id).first()
    chat = Chats()
    chat.title = anketa.theme
    chat.collaborators = str(user_first.id) + " " + str(user_second.id)
    db_sess.add(chat)
    db_sess.commit()
    return redirect("/chat/{}/{}".format(chat.id, user_second.id))


@app.route('/auto_create_solo_chat/<int:first_id>/<int:second_id>', methods=['GET', 'POST'])
@login_required
def auto_create_solo_chat(first_id, second_id):
    db_sess = db_session.create_session()
    user_first = db_sess.query(User).filter(User.id == first_id).first()
    user_second = db_sess.query(User).filter(User.id == second_id).first()
    chat = Chats()
    chat.title = user_first.nickname + ' и ' + user_second.nickname
    chat.collaborators = str(user_first.id) + " " + str(user_second.id)
    db_sess.add(chat)
    db_sess.commit()
    return redirect("/chat/{}/{}".format(chat.id, user_second.id))


@app.route('/questions/<int:chat_id>/<int:user_id>')
def questoins(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template("questions.html", photo=user.id, chat_id=chat_id, title="Задать вопрос")


@app.route('/chat_profile/<int:chat_id>/<int:user_id>')
def chat_profile(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    chat = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    if chat.collaborators.split(' ')[0] != 'all':
        admin = db_sess.query(User).filter(User.id == int(chat.collaborators.split(' ')[0])).first()
    else:
        admin = ""
    sp = []
    if chat.collaborators.split(' ')[0] != 'all':
        for i in chat.collaborators.split(' '):
            if int(i) != 1:
                sp.append(db_sess.query(User).filter(User.id == int(i)).first())
    else:
        sp = db_sess.query(User).all()[1:]
    return render_template("chat_profile.html", photo=user.id, chat_id=chat_id, title=chat.title, admin=admin,
                           members=sp)


if __name__ == '__main__':
    db_session.global_init("db/students_chat.db")
    app.register_blueprint(users_api.blueprint)
    app.run(port=5000, host='127.0.0.1')
