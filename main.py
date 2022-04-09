import io
import os

from PIL import Image
from flask import Flask
from flask import render_template, request, redirect, abort, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.chats import Chats
from data.ankets import Ankets
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/main_chat/<int:user_id>", methods=['POST', 'GET'])
def main_chat(user_id):
    form = MessageForm()
    db_sess = db_session.create_session()
    chat = db_sess.query(Chats).filter(Chats.id == 1).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    photo = Image.open(io.BytesIO(user.photo))
    photo.save('static/img/photo_for_ava_for_user{}.png'.format(user.id))
    author = chat.collaborators.split(' ')[0]
    if author != "all":
        author = int(author)
    else:
        author = -1
    if form.validate_on_submit():
        if form.message.data is not None and form.message.data != "":
            mess = Messages()
            mess.chat_id = chat.id
            mess.user_id = user_id
            mess.text = form.message.data
            db_sess.add(mess)
            db_sess.commit()
        form.message.data = ""
        db_sess.commit()
    form.message.data = ""
    messages = db_sess.query(Messages).filter(Messages.chat_id == chat.id).all()
    user_chats = db_sess.query(Chats).filter(
        (Chats.collaborators.like("%{}%".format(current_user.id))) | (
            Chats.collaborators.like("%all%"))).all()
    return render_template("chat.html", form=form, photo=user.id, messages=messages, title=chat.title,
                           user_chats=user_chats, chat_id=1, author=author)


@app.route("/chat/<int:chat_id>/<int:user_id>", methods=['POST', 'GET'])
def own_chat(chat_id, user_id):
    form = MessageForm()
    db_sess = db_session.create_session()
    chat = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    author = chat.collaborators.split(' ')[0]
    if author != "all":
        author = int(author)
    else:
        author = -1
    if form.validate_on_submit():
        if form.message.data is not None and form.message.data != "":
            mess = Messages()
            mess.chat_id = chat.id
            mess.user_id = user_id
            mess.text = form.message.data
            db_sess.add(mess)
            db_sess.commit()
        form.message.data = ""
        db_sess.commit()
    form.message.data = ""
    messages = db_sess.query(Messages).filter(Messages.chat_id == chat.id).all()
    user_chats = db_sess.query(Chats).filter(
        (Chats.collaborators.like("%{}%".format(current_user.id))) | (
            Chats.collaborators.like("%all%"))).all()
    return render_template("chat.html", form=form, photo=user.id, messages=messages, title=chat.title,
                           user_chats=user_chats, chat_id=chat_id, author=author)


@app.route('/profile/<int:chat_id>/<int:user_id>')
def profile(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template('profile.html', title="Профиль", chat_id=chat_id, photo=user.id)


@app.route('/register', methods=['POST', 'GET'])
def reg_users():
    db_sess = db_session.create_session()
    form = RegisterForm()
    user_first = db_sess.query(User).filter(User.id == 1).first()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter((User.email == form.email.data) | (User.nickname == form.nickname.data)).first():
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Такой пользователь уже существует")
        if ' ' in form.nickname.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="В никнеймах нельзя использовать пробел")
        user = User(
            email=form.email.data,
            nickname=form.nickname.data,
            surname=form.surname.data,
            name=form.name.data,
            group=form.group.data,
            photo=user_first.photo
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/load_ava/{}'.format(int(user.id)))
    return render_template('register.html', title='Registration', form=form)


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
                return redirect("/main_chat/{}".format(user.id))
            return render_template('login.html', message="Неверный логин или пароль", form=form)
        else:
            return render_template('login.html', message="Такого пользователя не существует", form=form)
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
    ankets = db_sess.query(Ankets).all()
    ankets_first = []
    ankets_second = []
    p = 0
    for i in ankets:
        if p % 2 == 0:
            ankets_first.append(i)
        else:
            ankets_second.append(i)
        p += 1
    return render_template('ankets.html', title='Анкеты', photo=user.id, chat_id=chat_id, ankets_first=ankets_first,
                           ankets_second=ankets_second)


@app.route('/create_chat/<int:chat_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def create_chat(chat_id, user_id):
    form = ChatForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        chat = Chats()
        if len(form.title.data) >= 30:
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
            if len(form.collaborators.data.split(' ')) > 1:
                return render_template("edit_chat.html", chat_id=chat_id, title="Редактирование чата",
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
            if len(form.title.data) >= 30:
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
            k = str(user.id) + ' ' + k[:-1]
            if k[-1] == ' ':
                k = k[:-1]
            chat.collaborators = k
        else:
            abort(404)
    if form.validate_on_submit():
        if chat:
            if len(form.title.data) >= 30:
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
    if chat:
        db_sess.delete(chat)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/main_chat/{}".format(user.id))


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
    return redirect("/main_chat/{}".format(user.id))


@app.route('/create-anket/<int:chat_id>/<int:user_id>', methods=['POST', 'GET'])
def create_anket(chat_id, user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = AnketForm()
    if form.validate_on_submit():
        if (len(form.theme.data) == 0) or (len(form.theme.data) > 30) or (form.theme.data[0] == ' '):
            if form.opis.data[0] == ' ' or form.opis.data[0] == '':
                return render_template('create_anket.html', title='Создание анкеты', form=form, chat_id=chat_id,
                                       photo=user.id, message="Минимально количество символов в теме: 1, "
                                                              "Заполните поле описания анкеты")
            return render_template('create_anket.html', title='Создание анкеты', form=form, chat_id=chat_id,
                                   photo=user.id, message="Минимально количество символов в теме: 1, "
                                                          "Максимальное количество символов в теме: 30")
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
    form = ChangeNickForm()
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.nickname == form.login.data).first():
            return render_template("change_nick.html", photo=user.id, chat_id=chat_id, title="Смена никнейма",
                                   form=form, message="Такой пользователь уже существует")
        if ' ' in form.login.data:
            return render_template("change_nick.html", photo=user.id, chat_id=chat_id, title="Смена никнейма",
                                   form=form, message="В никнеймах нельзя использовать пробел")
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
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("change_password.html", photo=user.id, chat_id=chat_id, title="Смена пароля",
                                   form=form, message="Пароли не совпадают")
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
    ankets = db_sess.query(Ankets).filter(Ankets.author == user_id).all()
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
        if (len(form.theme.data) == 0) or (len(form.theme.data) > 30) or (form.theme.data[0] == ' '):
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
        if (len(form.theme.data) == 0) or (len(form.theme.data) > 30) or (form.theme.data[0] == ' '):
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
    """ДОДЕЛАТЬ ПРОВЕРКУ ГРУППЫ НА ПРАВИЛЬНОСТЬ"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    form = ChangeGroupForm()
    if form.validate_on_submit():
        if user.check_password(form.password.data):
            user.group = form.group.data
            db_sess.commit()
            return redirect('/profile/{}/{}'.format(chat_id, user_id))
        return render_template("change_group.html", photo=user.id, chat_id=chat_id, title="Смена группы обучения",
                               form=form, message="Неверный пароль")
    return render_template("change_group.html", photo=user.id, chat_id=chat_id, title="Смена группы обучения",
                           form=form)


if __name__ == '__main__':
    db_session.global_init("db/students_chat.db")
    app.run(port=8080, host='127.0.0.1')
