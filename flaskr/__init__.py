
""" 各インスタンスを生成するファイル """

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flaskr.utils.template_filters import replace_newline

basedir = os.path.abspath(__name__)

login_manager = LoginManager()
login_manager.login_view = 'app.view'
login_manager.login_message = 'ログインしてくださいね～'
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """ appの生成から設定を行う """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hogehoge'
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # bpをここで読むこむが読み込まない場合はsetup.pyで別途読み込む必要あり
    from flaskr.views import bp
    """ viewsの内容をインポートする """
    app.register_blueprint(bp)
    app.add_template_filter(replace_newline)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app

