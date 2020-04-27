from datetime import datetime

from flask import Blueprint, redirect, url_for, flash, request, render_template, make_response, session
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.publlic_fun.publlic_fun import get_verify_code
from io import BytesIO

LogOrReg_bp = Blueprint('LogOrReg', __name__)


# 登录
@LogOrReg_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = LoginForm()
    # 是否是post请求且数据格式正确
    if form.validate_on_submit():
        # 检验验证码
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('验证码错误！')
            # return redirect(url_for('LogOrReg.login'))
        else:
            # 根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
            user = User.query.filter_by(username=form.username.data).first()
            # print("user", user)
            # 如果用户不存在或者密码不正确
            if user is None or not user.check_password(form.password.data):
                # 如果用户不存在或者密码不正确则进行提示
                flash('用户名或密码无效,再检查一下?')
                # 然后跳到登录页面
                return redirect(url_for('LogOrReg.login'))
            # 当用户名和密码都正确时是否记住登录状态
            login_user(user, remember=form.remember_me.data)
            # 此时的next_page记录的是跳转至登录页面时的地址
            next_page = request.args.get('next')

            # 记录登录时间
            current_user.last_seen = datetime.now()
            db.session.commit()

            # 如果next_page记录的地址不存在那么就返回首页
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home.index')
            # 登录后要么重定向至跳转前的页面，要么跳转至首页
            return redirect(next_page)
    # 一定要有返回体，否则用户未登录时候会报错
    return render_template('login.html', title='登录', form=form)


# 注册
@LogOrReg_bp.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = RegistrationForm()
    # 是否是post请求且数据是是否有效
    if form.validate_on_submit():
        # 检验验证码,lower()大写转小写
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('验证码错误！')
            # return redirect(url_for('LogOrReg.register'))
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('恭喜您成为我们网站的新用户啦!')
            return redirect(url_for('LogOrReg.login'))
    return render_template('register.html', title='注册', form=form)


# 注销登录
@LogOrReg_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.index'))


# 验证码视图函数
@LogOrReg_bp.route('/code')
def get_code():
    image, code = get_verify_code()
    # 图片以二进制形式写入
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把buf_str作为response返回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = code
    return response
