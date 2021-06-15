
from wtforms.form import Form
from wtforms.fields import (
    IntegerField, StringField, TextField, PasswordField,
    SubmitField, HiddenField, FileField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flaskr.models import User
from flask_login import current_user
from flask import flash

class LoginForm(Form):
    email = StringField('メール：', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード：', validators=[DataRequired(),
                            EqualTo('confirm_password')])
    confirm_password = PasswordField('パスワード再入力：', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class RegisterForm(Form):
    email = StringField('メール：', validators=[DataRequired(), Email('メールアドレスではありません')])
    username = StringField('名前：', validators=[DataRequired()])
    submit = SubmitField('登録')

    def validate_email(self, field):
        """ フォーム入力時に勝手に判定してくれる """
        if User.select_user_by_email(field.data):
            raise ValidationError('すでに存在するメールアドレスじゃ')

class ResetPasswordForm(Form):
    password = PasswordField('パスワード：', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('確認用：', validators=[DataRequired()])
    submit = SubmitField('再登録')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('8文字以上で頼みますわ～')

class ForgotPasswordForm(Form):
    email = StringField('メール：', validators=[DataRequired(), Email()])
    submit = SubmitField('パスワードを再設定する')

    def validate_email(self, field):
        if not User.select_user_by_email(field.data):
            raise ValidationError('そのメールアドレスは存在しません')

class UserForm(Form):
    email = StringField('メール：', validators=[DataRequired(), Email('メルアドが間違ってるよ')])
    username = StringField('名前：', validators=[DataRequired()])
    picture_path = FileField('ファイルアップロード')
    submit = SubmitField('ユーザ情報の更新')

    def validate(self):
        if not super(Form, self).validate():
            return False
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.id != int(current_user.get_id()):
                flash('そのメールアドレスはすでに登録されているぽよ')
                return False
        return True

class ChangePasswordForm(Form):
    password = PasswordField('パスワード：', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('確認用：', validators=[DataRequired()])
    submit = SubmitField('パスワードの更新')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('8文字以上で頼みますわ～')

class UserSearchForm(Form):
    username = StringField('名前：', validators=[DataRequired()])
    submit = SubmitField('ユーザ検索')

class ConnectForm(Form):
    connect_condition = HiddenField()
    to_user_id = HiddenField()
    submit = SubmitField()

