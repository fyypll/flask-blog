from datetime import datetime

from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db, app
from app.forms import LoginForm, RegistrationForm
from app.models import User

LogOrReg_bp = Blueprint('LogOrReg', __name__)


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = LoginForm()
    # 是否是post请求且数据格式正确
    if form.validate_on_submit():
        # 根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
        user = User.query.filter_by(username=form.username.data).first()
        # print("user", user)
        # 如果用户不存在或者密码不正确
        if user is None or not user.check_password(form.password.data):
            # 如果用户不存在或者密码不正确则进行提示
            flash('用户名或密码无效,再检查一下?')
            # 然后跳到登录页面
            return redirect(url_for('login'))
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
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = RegistrationForm()
    # 是否是post请求且数据是是否有效
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜您成为我们网站的新用户啦!')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)


# 注销登录
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.index'))