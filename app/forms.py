from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


# 登录表格
class LoginForm(FlaskForm):
    # DataRequired，当你在当前表格没有输入而直接到下一个表格时会提示你输入
    username = StringField('用户名', validators=[DataRequired(message='请输入名户名')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


# 注册表格
class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '重复密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    # 校验用户名是否重复
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名重复了，请您重新换一个呗!')

    # 校验邮箱是否重复
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('邮箱重复了，请您重新换一个呗!')


# 个人资料表格
class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名!')])
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=140)])
    submit = SubmitField('提交')


# 发文章表格
class SendPostForm(FlaskForm):
    post_title = StringField('标题', validators=[DataRequired()])
    post_body = TextAreaField('正文', validators=[Length(min=10, max=10000)])
    submit = SubmitField('发表')


# 编辑文章表格
class EditPostForm(FlaskForm):
    post_title = StringField('标题', validators=[DataRequired()])
    post_body = TextAreaField('正文', validators=[Length(min=10, max=10000)])
    submit = SubmitField('发表')
