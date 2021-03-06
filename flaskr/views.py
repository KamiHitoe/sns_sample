
from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, session, jsonify, 
)
from flask_login import login_user, logout_user, login_required, current_user
from flaskr.models import User, PasswordResetToken, UserConnect, Message
from flaskr import db
from flaskr.forms import (
    LoginForm, RegisterForm, ResetPasswordForm, ForgotPasswordForm,
    UserForm, ChangePasswordForm, UserSearchForm, ConnectForm, MessageForm,

)
from flaskr.utils.message_format import make_message_format, make_old_message_format
from os import path

# メソッドの前にappを付ける必要がでてくる
bp = Blueprint('app', __name__, url_prefix='')

# @bp.route('/')
# def home():
#     """ 友達一覧表示 """
#     user_id = current_user.get_id()
#     user_friends_id_to_from, user_friends_id_from_to = User.find_friends_id(user_id)
#     # ログインユーザ空間から検索ユーザ空間に写像するためにlistの変換が必要
#     friends_id_list = []
#     for user_friend_id in user_friends_id_to_from:
#         if user_friend_id.friends_to_from:
#             friends_id_list.append(user_friend_id.friends_to_from)
#     for user_friend_id in user_friends_id_from_to:
#         if user_friend_id.friends_from_to:
#             friends_id_list.append(user_friend_id.friends_from_to)
#     friends = []
#     for friends_id in friends_id_list:
#         friends.append(User.select_user_by_id(friends_id))

#     """ 友達非承認待ち """
#     requested_friends_records = UserConnect.find_friends_requested(user_id)
#     requested_friends_records_list = []
#     for requested_friend_record in requested_friends_records:
#         requested_friends_records_list.append(requested_friend_record.from_user_id)
#     requested_friends = []
#     for requested_friend_id in requested_friends_records_list:
#         requested_friends.append(User.select_user_by_id(requested_friend_id))

#     connect_form = ConnectForm()
#     session['url'] = 'app.home'
#     return render_template('home.html', friends=friends, requested_friends=requested_friends, connect_form=connect_form)


@bp.route('/')
def home():
    friends = requested_friends = requesting_friends = None
    connect_form = ConnectForm()
    session['url'] = 'app.home'
    if current_user.is_authenticated:
        friends = User.select_friends()
        requested_friends = User.select_requested_friends()
        requesting_friends = User.select_requesting_friends()
    return render_template(
        'home.html',
        friends=friends, requested_friends=requested_friends, requesting_friends=requesting_friends,
        connect_form=connect_form
    )


@bp.route('/logout')
def logout():
    """ ユーザのセッションを切ってくれる """
    logout_user()
    return redirect(url_for('app.home'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        """ http.postかつformのvalidaterが正常な場合 """
        user = User.select_user_by_email(form.email.data)
        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next:
                next = url_for('app.home')
            return redirect(next)
        elif not user:
            flash('存在しないユーザ、ってかflashって何！？')
        elif not user.is_active:
            flash('無効になっとるユーザや！')
        elif not user.validate_password(form.password.data):
            flash('メールアドレスとパスワードのCombが誤っています')
    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username = form.username.data,
            email = form.email.data,
        )
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = ''
        with db.session.begin(subtransactions=True):
            token = PasswordResetToken.publish_token(user)
        db.session.commit()
        print(f'パスワード設定用URL：http://127.0.0.1:5000/set_password/{token}')
        flash('パスワード設定用のURLを表示しました')
        return redirect(url_for('app.login'))
    return render_template('register.html', form=form)


@bp.route('/set_password/<uuid:token>', methods=['GET', 'POST'])
def set_password(token):
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method == 'POST' and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードは無事に更新されました')
        return redirect(url_for('app.login'))
    return render_template('set_password.html', form=form)


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        user = User.select_user_by_email(email)
        if user:
            with db.session.begin(subtransactions=True):
                token = PasswordResetToken.publish_token(user)
            db.session.commit()
            reset_url = f'http://127.0.0.1:5000/set_password/{token}'
            print(reset_url)
            flash('パスワード設定用のURLを表示しました')
        else:
            flash('存在しないユーザです')
    return render_template('forgot_password.html', form=form)


@bp.route('/user', methods=['GET', 'POST'])
def user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.email = form.email.data
            # fileデータは処理が違う
            file = request.files[form.picture_path.name].read()
            if file:
                """ 上のファイル名でファイルが存在していたら """
                file_name = user_id + '_' + str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flaskr/static/user_image/' + file_name
                # picture_pathに画像ファイルのバイナリデータを記述する
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_image/' + file_name
        db.session.commit()
        flash('ユーザ情報の更新に成功しました')
    return render_template('user.html', form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_id(current_user.get_id())
        password = form.password.data
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
        db.session.commit()
        flash('パスワードの更新に成功しました')
        return redirect(url_for('app.user'))
    return render_template('change_password.html', form=form)


@bp.route('/user_search', methods=['GET'])
@login_required
def user_search():
    form = UserSearchForm(request.form)
    connect_form = ConnectForm()
    session['url'] = 'app.user_search'
    users = None
    user_name = request.args.get('username', None, type=str)
    next_url = prev_url = None
    if user_name:
        page = request.args.get('page', 1, type=int)
        # postsはflask_sqlalchemy.Paginationクラスを継承している
        posts = User.search_by_name(user_name, page)
        next_url = url_for('app.user_search', page=posts.next_num, username=user_name) if posts.has_next else None
        prev_url = url_for('app.user_search', page=posts.prev_num, username=user_name) if posts.has_prev else None
        users = posts.items
        # UserからUserConnectのStatusを取得する
    return render_template('user_search.html', form=form, users=users, connect_form=connect_form,
        next_url=next_url, prev_url=prev_url)


@bp.route('/connect_user', methods=['POST'])
@login_required
def connect_user():
    form = ConnectForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.connect_condition.data == 'connect':
            new_connect = UserConnect(current_user.get_id(), form.to_user_id.data)
            with db.session.begin(subtransactions=True):
                new_connect.create_new_connect()
            db.session.commit()
        elif form.connect_condition.data == 'accept':
            # 相手から自分へのUserConnectを取得
            connect = UserConnect.select_by_from_user_id(form.to_user_id.data)
            if connect:
                with db.session.begin(subtransactions=True):
                    connect.update_status() # status 1 -> 2
                db.session.commit()
    # user_searchから取得したsessionを利用する
    next_url = session.pop('url', 'app:home')
    return redirect(url_for(next_url))


@bp.route('/delete_connect', methods=['POST'])
@login_required
def delete_connect():
    """ UserConnectから対応レコードを削除 """
    form = ConnectForm(request.form)
    if request.method == 'POST':
        if form.connect_condition.data == 'delete':
            if UserConnect.select_by_from_user_id(form.to_user_id.data):
                delete_connect = UserConnect.select_by_from_user_id(form.to_user_id.data)
                with db.session.begin(subtransactions=True):
                    db.session.delete(delete_connect)
                db.session.commit()
            elif UserConnect.select_by_to_user_id(form.to_user_id.data):
                delete_connect = UserConnect.select_by_to_user_id(form.to_user_id.data)
                with db.session.begin(subtransactions=True):
                    db.session.delete(delete_connect)
                db.session.commit()
    # user_searchから取得したsessionを利用する
    next_url = session.pop('url', 'app:home')
    return redirect(url_for(next_url))


@bp.route('/message/<id>', methods=['GET', 'POST'])
@login_required
def message(id):
    if not UserConnect.is_friend(id):
        """ Falseであればリダイレクト """
        return redirect(url_for('app.home'))
    form = MessageForm(request.form)
    # 自分と相手のメッセージを取得
    messages = Message.get_friend_messages(current_user.get_id(), id)
    user = User.select_user_by_id(id)

    # 未読の相手のメッセージを取り出す
    read_message_ids = \
                      [message.id for message in messages \
                      if (not message.is_read) and (message.from_user_id == int(id))]
    # すでに読まれている未読メッセージを既読化する
    not_checked_message_ids = \
                              [message.id for message in messages \
                              if message.is_read and (not message.is_checked) \
                              and (message.from_user_id == int(current_user.get_id())) ]
    if not_checked_message_ids:
        """ 未読状態ですでに表示したもののis_checkedフラグを1にしてDBに格納 """
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    if read_message_ids:
        """ 相手のメッセージを表示するとis_readフラグを1にしてDBに格納 """
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(read_message_ids)
        db.session.commit()

    if request.method == 'POST' and form.validate():
        """ message.htmlから送られたメッセージをDBに格納 """
        new_message = Message(current_user.get_id(), id, form.message.data)
        with db.session.begin(subtransactions=True):
            new_message.create_message()
        db.session.commit()
        return redirect(url_for('app.message', id=id))
    return render_template('message.html', 
        form=form, messages=messages, to_user_id=id, user=user)


@bp.route('/message_ajax', methods=['GET'])
@login_required
def message_ajax():
    user_id = request.args.get('user_id', -1, type=int)
    user = User.select_user_by_id(user_id)
    not_read_messages = Message.select_not_read_messages(user_id, current_user.get_id())
    # まだ読んでいない相手のメッセージをajaxで取得
    not_read_message_ids = [message.id for message in not_read_messages]
    if not_read_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_read_by_ids(not_read_message_ids)
        db.session.commit()
    # ajaxによってすでに読まれた自分のメッセージを既読化する
    not_checked_messages = Message.select_not_checked_messages(current_user.get_id(), user_id)
    not_checked_message_ids = [not_checked_message.id for not_checked_message in not_checked_messages]
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            Message.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    return jsonify(data=make_message_format(user, not_read_messages),
        checked_message_ids=not_checked_message_ids)


@bp.route('/load_old_messages', methods=['GET'])
@login_required
def load_old_messages():
    user_id = request.args.get('user_id', -1, type=int)
    offset_value = request.args.get('offset_value', -1, type=int)
    if (user_id == -1) or (offset_value == -1):
        return
    messages = Message.get_friend_messages(current_user.get_id(), user_id, offset_value * 5)
    user = User.select_user_by_id(user_id)
    return jsonify(data=make_old_message_format(user, messages))


# エラーハンドリング
@bp.app_errorhandler(404)
def page_not_found(e):
    """ 404Not Foundの時のエラーハンドリング """
    return redirect(url_for('app.home'))


@bp.app_errorhandler(500)
def server_error(e):
    """ 500Server Errorの時のエラーハンドリング """
    return render_template('http500.html'), 500
