
# from wtforms.form import FlaskForm
from wtforms.fields import (
    IntegerField, StringField, TextField, PasswordField,
    SubmitField, HiddenField, FileField, TextAreaField, 
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flaskr.models import User, UserConnect
from flask_login import current_user
from flask import flash
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    email = StringField('メール：', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード：', validators=[DataRequired(),
                            EqualTo('confirm_password')])
    confirm_password = PasswordField('パスワード再入力：', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class RegisterForm(FlaskForm):
    email = StringField('メール：', validators=[DataRequired(), Email('メールアドレスではありません')])
    username = StringField('名前：', validators=[DataRequired()])
    submit = SubmitField('登録')

    def validate_email(self, field):
        """ フォーム入力時に勝手に判定してくれる """
        if User.select_user_by_email(field.data):
            raise ValidationError('すでに存在するメールアドレスじゃ')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('パスワード：', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('確認用：', validators=[DataRequired()])
    submit = SubmitField('再登録')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('8文字以上で頼みますわ～')

class ForgotPasswordForm(FlaskForm):
    email = StringField('メール：', validators=[DataRequired(), Email()])
    submit = SubmitField('パスワードを再設定する')

    def validate_email(self, field):
        if not User.select_user_by_email(field.data):
            raise ValidationError('そのメールアドレスは存在しません')

class UserForm(FlaskForm):
    email = StringField('メール：', validators=[DataRequired(), Email('メルアドが間違ってるよ')])
    username = StringField('名前：', validators=[DataRequired()])
    picture_path = FileField('ファイルアップロード')
    submit = SubmitField('ユーザ情報の更新')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.id != int(current_user.get_id()):
                flash('そのメールアドレスはすでに登録されているぽよ')
                return False
        return True

class ChangePasswordForm(FlaskForm):
    password = PasswordField('パスワード：', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('確認用：', validators=[DataRequired()])
    submit = SubmitField('パスワードの更新')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('8文字以上で頼みますわ～')

class UserSearchForm(FlaskForm):
    username = StringField('名前：', validators=[DataRequired()])
    submit = SubmitField('ユーザ検索')

class ConnectForm(FlaskForm):
    connect_condition = HiddenField()
    to_user_id = HiddenField()
    submit = SubmitField()

class MessageForm(FlaskForm):
    to_user_id = HiddenField()
    message = TextAreaField()
    submit = SubmitField('メッセージ送信')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        is_friend = UserConnect.is_friend(self.to_user_id.data)
        if not is_friend:
            return False
        return True

