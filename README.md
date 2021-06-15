
## 機能要件
- ログイン機能
- ユーザ情報編集機能
- ユーザ検索機能
- 友達申請、表示、削除機能
- メッセージ送信機能
- OAuthによるSSO機能
- クレジット支払機能
- 単体テスト機能

## ファイル要件

### setup.py
- create_app()を用いたappの作成
- Flask appのrun

### __init__.py
- flask_sqlalchemyからdbの作成
- flask_migrateからmigrateの作成
- flask_loginからlogin_managerの作成
- flaskからappの作成、設定までをcreate_app()として関数化

### models.py
- login_managerからuser_loaderの実装
- Userクラス作成
    - id
    - username
    - email
    - password
    - picture_path
    - is_active
    - create_at
    - update_at
- PasswordResetTokenクラス作成
    - id
    - token
    - user_id: ForeignKey
    - expire_at
    - create_at
    - update_at

### forms.py
- LoginForm
    - email
    - password
    - confirm_password
- RegisterForm
    - email
    - username
    - validate_email()
- ResetPasswordForm
    - password
    - confirm_password
    - validate_password()
- ForgotPasswordForm
    - email
    - validate_email()
- UserForm
    - email
    - username
    - picture_path

### views.py
- / -> def home
- /logout
- /login
- /register
- /reset_password/<uuid:token>
- /forgot_password
- /user

### templates
- _formhelpers.html
- base.html
- home.html
- login.html
- register.html
- set_password.html
- user.html
- change_password.html
- forgot_password.html
- http500.html


