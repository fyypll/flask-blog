import re

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


# 登录表格
class LoginForm(FlaskForm):
    # DataRequired，当你在当前表格没有输入而直接到下一个表格时会提示你输入
    username = StringField('用户名', validators=[DataRequired(message='请输入名户名')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    verify_code = StringField('验证码', validators=[DataRequired(message='请输入验证码')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

    # # 校验用户名是否注册
    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is None:
    #         raise ValidationError('该用户尚未注册！')


# 注册表格
class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email('邮箱格式不对哦，检查一下吧!')])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('重复密码', validators=[DataRequired(), EqualTo('password', '两次输入的密码不一致!')])
    submit = SubmitField('注册')

    # 校验用户名
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        # 如果用户名在数据库已存在
        if user is not None:
            raise ValidationError('用户名已存在，再想一个?')
        # 如果用户名是纯数字
        if username.data.isdigit():
            raise ValidationError('用户名不能是纯数字哦!')
        # 用户名长度判断
        if len(username.data) < 4:
            raise ValidationError('用户名长度不能小于4位哦!')
        if len(username.data) > 15:
            raise ValidationError('用户名长度不能大于15位哦!')

    # 校验邮箱
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        # 如果邮箱在数据库中已存在
        if user is not None:
            raise ValidationError('邮箱已存在，换一个?')
        # 这里注释了是因为其实上面的表单已经实现了验证了，把默认的错误提示改成自己的就行了，这里就不需要了
        # # 如果邮箱名长度小于7且格式通过正则验证结果为None
        # if len(email.data) < 7 or re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email.data) == None:
        #     raise ValidationError('邮箱格式不对哦，检查一下吧!')

    # 验证密码长度
    def validate_password(self, password):
        if len(password.data) < 6:
            raise ValidationError('密码长度不能少于6个字符哦!')
        if len(password.data) > 15:
            raise ValidationError('密码长度不能大于15个字符哦!')


# 个人资料表格
class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='用户名不可为空哦')])
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=140)])
    submit = SubmitField('提交')

    # 校验用户名
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        current_user.username
        # 如果用户名在数据库已存在且不是修改前的用户名
        if user is not None and user.username != current_user.username:
            raise ValidationError('用户名已存在，再想一个?')
        # 如果用户名是纯数字
        if username.data.isdigit():
            raise ValidationError('用户名不能是纯数字哦!')
        # 用户名长度判断
        if len(username.data) < 4:
            raise ValidationError('用户名长度不能小于4位哦!')
        if len(username.data) > 15:
            raise ValidationError('用户名长度不能大于15位哦!')


# 发表/编辑文章的表格
class PostForm(FlaskForm):
    post_title = StringField('标题', validators=[DataRequired()])
    post_body = TextAreaField('正文', validators=[Length(min=10, max=10000)])
    submit = SubmitField('发表')


# 编辑用户的表格
class EditUserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email('邮箱格式不对哦，检查一下吧!')])
    about_me = TextAreaField('签名', validators=[Length(min=0, max=140)])
    submit = SubmitField('更新')

    # # 校验邮箱
    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     # 如果邮箱在数据库中已存在
    #     if user is not None:
    #         raise ValidationError('邮箱已存在，换一个?')


# 评论/留言板/编辑评论留言的表格
class LiuYanForm(FlaskForm):
    username = StringField('称呼', validators=[DataRequired()])
    email = StringField('电子邮件', validators=[DataRequired(), Email('邮箱格式不对哦，检查一下吧!')])
    body = TextAreaField('添加新评论', validators=[DataRequired()])
    submit = SubmitField('提交评论')

    # 评论长度判断
    def validate_body(self, body):
        if len(body.data) < 5:
            raise ValidationError('评论长度不能小于5个字哦!')
        if len(body.data) > 1000:
            raise ValidationError('评论长度不能大于1000字哦!')
