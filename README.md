
# 機能要件
- ログイン機能
- ユーザ情報編集機能
- ユーザ検索機能
- 友達申請、削除機能
- メッセージ送信機能
- 非同期通信機能

- OAuthによるSSO機能
- クレジット支払機能
- 単体テスト機能


# ファイル要件

### setup.py
- create_app()を用いたappの作成
- Flask appのrun


## flaskr

### __init__.py
- flask_sqlalchemyからdbの作成
- flask_migrateからmigrateの作成
- flask_loginからlogin_managerの作成
- flaskからappの作成、設定までをcreate_app()として関数化

### models.py
- login_managerからuser_loaderの実装
- User
    - id
    - username
    - email
    - password
    - picture_path
    - is_active
    - create_at
    - update_at
- PasswordResetToken
    - id
    - token
    - user_id: ForeignKey
    - expire_at
    - create_at
    - update_at
- UserConnect
    - id
    - from_user_id
    - to_user_id
    - status
    - create_at
    - update_at
- Message
    - id
    - from_user_id
    - to_user_id
    - is_read
    - is_checked
    - message
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
- ChangePasswordForm
    - password
    - confirm_password
- UserSearchForm
    - username
- ConnectForm
    - connect_condition
    - to_user_id
- MessageForm
    - to_user_id
    - message

### views.py
- / -> def home
- /logout
- /login
- /register
- /set_password/<uuid:token>
- /forgot_password
- /user
- /change_password
- /user_search
- /connect_user
- /delete_connect
- /message
- /message_ajax
- /load_old_messages
- /page_not_found
- /server_error


## templates
- _formhelpers.html
- base.html
- home.html
- login.html
- register.html
- set_password.html
- user.html
- user_search.html
- message.html
- change_password.html
- forgot_password.html
- http500.html


## static
- css
- icon
- user_image


## utils
- template_filters.py
- message_format.py


