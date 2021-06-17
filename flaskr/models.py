
""" tableの設計とログイン機能の設定 """

from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, desc

from datetime import datetime, timedelta
from uuid import uuid4  # passwordを発行する時に便利


@login_manager.user_loader
def load_user(user_id):
    """ user_idに対して、Userインスタンスを返す """
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    """ ユーザログイン機能を付加 """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)  # 検索性があるものはindex付けとく
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(
                        db.String(128),
                        default=generate_password_hash('something'),
                        )  # passwordに初期値を設ける
    picture_path = db.Column(db.Text, nullable=True)
    # 有効か無効かのフラグ
    is_active = db.Column(db.Boolean, unique=False, default=False)
    # システム管理用につけるタイムスタンプ
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email):
        """ コンストラクタの値は2つ。あとは無入力であればdefaultの値が採択される """
        self.username = username
        self.email = email

    def validate_password(self, password):
        return check_password_hash(self.password, password)

    def create_new_user(self):
        db.session.add(self)

    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True

    @classmethod
    def select_user_by_email(cls, email):
        """ 同じ処理に別名を付けているだけなのであまり意味はない """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def search_by_name(cls, username, page=1):
        """ ユーザをusernameで検索して、UserConnectとouter joinで紐づけた後に
        ユーザ情報と友達関係を取得する """
        # from_user_id = 検索相手のID, to_user_id = ログインユーザのID, UserConnectに紐づけ
        user_connect1 = aliased(UserConnect)
        # from_user_id = ログインユーザのID, to_user_id = 検索相手のID, UserConnectに紐づけ
        user_connect2 = aliased(UserConnect)
        return cls.query.filter(
            cls.username.like(f'%{username}%'), # クエリ = username
            cls.id != int(current_user.get_id()), # 自分は対象外とする条件
            cls.is_active == True # 存在している条件
            ).outerjoin(
                user_connect1, 
                and_(user_connect1.from_user_id == cls.id, # 検索相手
                user_connect1.to_user_id == current_user.get_id()) # ログインユーザ
            ).outerjoin(
                user_connect2,
                and_(user_connect2.from_user_id == current_user.get_id(),
                user_connect2.to_user_id == cls.id)
            ).with_entities(
                # クエリを送るカラムを絞る
                cls.id, cls.username, cls.picture_path,
                user_connect1.status.label('joined_status_to_from'), # 相手→自分
                user_connect2.status.label('joined_status_from_to'), # 自分→相手
            ).order_by(cls.username).paginate(page, 10, False)

    @classmethod
    def select_friends(cls):
        """ UserConnectと結合させてからtoとfromの和集合を取る """
        return cls.query.join(
            UserConnect,
            or_(
                and_(
                    UserConnect.to_user_id == cls.id,
                    UserConnect.from_user_id == current_user.get_id(),
                    UserConnect.status == 2
                ),
                and_(
                    UserConnect.from_user_id == cls.id,
                    UserConnect.to_user_id == current_user.get_id(),
                    UserConnect.status == 2
                )
            )
        ).with_entities(
            cls.id, cls.username, cls.picture_path
        ).all()

    @classmethod
    def select_requested_friends(cls):
        return cls.query.join(
            UserConnect,
            and_(
                UserConnect.from_user_id == cls.id,
                UserConnect.to_user_id == current_user.get_id(),
                UserConnect.status == 1
            )
        ).with_entities(
            cls.id, cls.username, cls.picture_path
        ).all()

    @classmethod
    def select_requesting_friends(cls):
        return cls.query.join(
            UserConnect,
            and_(
                UserConnect.from_user_id == current_user.get_id(),
                UserConnect.to_user_id == cls.id,
                UserConnect.status == 1
            )
        ).with_entities(
            cls.id, cls.username, cls.picture_path
        ).all()

    # @classmethod
    # def find_friends_id(cls, user_id):
    #     """ ログインユーザと友達関係になってるUserインスタンスを取得
    #     二回外部結合しちゃうと組み合わせが二乗になるため一回ずつに制限 """
    #     friends_connect1 = aliased(UserConnect)
    #     friends_connect2 = aliased(UserConnect)
    #     # toとfromで2回クエリを投げるせいで遅い
    #     return cls.query.filter_by( # filter=WHERE句でないと結合できないので注意
    #         id=user_id
    #         ).outerjoin(
    #             friends_connect1,
    #             and_(friends_connect1.from_user_id == cls.id,
    #             friends_connect1.status == 2)
    #         ).with_entities(
    #             # クエリを送るカラムを絞る
    #             cls.id, cls.username, cls.picture_path,
    #             friends_connect1.to_user_id.label('friends_to_from'), # 自分→相手
    #         ).all(), cls.query.filter_by( # filter=WHERE句でないと結合できないので注意
    #         id=user_id
    #         ).outerjoin(
    #             friends_connect2,
    #             and_(friends_connect2.to_user_id == cls.id,
    #             friends_connect2.status == 2)
    #         ).with_entities(
    #             # クエリを送るカラムを絞る
    #             cls.id, cls.username, cls.picture_path,
    #             friends_connect2.from_user_id.label('friends_from_to'), # 相手→自分
    #         ).all()


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, index=True, server_default=str(uuid4))
    # 結合用の外部キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # なんか知らんけどnowの後に()いらん
    expire_at = db.Column(db.DateTime, default=datetime.now)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at

    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record.user_id
        else:
            return None

    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()

    @classmethod
    def publish_token(cls, user):
        """ パスワード設定用のURLを生成 """
        token = str(uuid4())
        new_token = cls(
            token, user.id, datetime.now() + timedelta(days=1)
        )
        db.session.add(new_token)
        return token


class UserConnect(db.Model):
    __tablename__ = 'user_connects'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    # 1 = 申請中, 2 = 承認済
    status = db.Column(db.Integer, unique=False, default=1)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, from_user_id, to_user_id):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id

    def create_new_connect(self):
        db.session.add(self)

    def update_status(self):
        self.status = 2
        self.update_at = datetime.now()

    @classmethod
    def select_by_from_user_id(cls, from_user_id):
        return cls.query.filter_by(
            from_user_id = from_user_id, 
            to_user_id = current_user.get_id()
        ).first()

    @classmethod
    def select_by_to_user_id(cls, to_user_id):
        return cls.query.filter_by(
            from_user_id = current_user.get_id(), 
            to_user_id = to_user_id
        ).first()

    @classmethod
    def find_friends_requested(cls, to_user_id):
        """ 非承認待ちのUserConnectインスタンス群を返す """
        return cls.query.filter(
            cls.to_user_id == to_user_id,
            cls.status == 1,
        ).all()

    @classmethod
    def is_friend(cls, to_user_id):
        user = cls.query.filter(
            or_(
                and_(
                    UserConnect.from_user_id == current_user.get_id(),
                    UserConnect.to_user_id == to_user_id,
                    UserConnect.status == 2
                ),
                and_(
                    UserConnect.from_user_id == to_user_id,
                    UserConnect.to_user_id == current_user.get_id(),
                    UserConnect.status == 2
                ),
            )
        ).first()
        return True if user else False


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    is_read = db.Column(db.Boolean, default=False)
    is_checked = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.now())
    update_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, from_user_id, to_user_id, message):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.message = message

    def create_message(self):
        db.session.add(self)
    
    @classmethod
    def get_friend_messages(cls, id1, id2, offset_value=0, limit_value=5):
        """ 降順に0件飛ばして5件メッセージデータを取得する """
        return cls.query.filter(
            or_(
                and_(
                    cls.from_user_id == id1,
                    cls.to_user_id == id2,
                ),
                and_(
                    cls.from_user_id == id2,
                    cls.to_user_id == id1,
                )
            )
        # idを降順でソート
        ).order_by(desc(cls.id)).offset(offset_value).limit(limit_value).all()  # 新着順に並び替える

    @classmethod
    def update_is_read_by_ids(cls, ids):
        cls.query.filter(cls.id.in_(ids)).update(  # inと同じ構文
            {'is_read': 1},
            synchronize_session='fetch'
        )

    @classmethod
    def update_is_checked_by_ids(cls, ids):
        cls.query.filter(cls.id.in_(ids)).update(  # inと同じ構文
            {'is_checked': 1},
            synchronize_session='fetch'
        )

    @classmethod
    def select_not_read_messages(cls, from_user_id, to_user_id):
        return cls.query.filter(
            and_(
                cls.from_user_id == from_user_id,
                cls.to_user_id == to_user_id,
                cls.is_read == 0
            )
        ).order_by(cls.id).all()

    @classmethod
    def select_not_checked_messages(cls, from_user_id, to_user_id):
        return cls.query.filter(
            and_(
                cls.from_user_id == from_user_id,
                cls.to_user_id == to_user_id,
                cls.is_read == 1,
                cls.is_checked == 0
            )
        ).order_by(cls.id).all()
