from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
# 导入各个表单处理方法(form.py文件)
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SendPostForm, EditPostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='我的', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    # 对表格数据进行验证
    if form.validate_on_submit():
        # 根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
        user = User.query.filter_by(username=form.username.data).first()
        # print("user", user)
        # 如果用户不存在或者密码不正确
        if user is None or not user.check_password(form.password.data):
            # 如果用户不存在或者密码不正确则进行提示
            flash('无效的用户名或密码')
            # 然后跳到登录页面
            return redirect(url_for('login'))
        # 当用户名和密码都正确时是否记住登录状态
        login_user(user, remember=form.remember_me.data)
        # 此时的next_page记录的是跳转至登录页面是的地址
        next_page = request.args.get('next')
        # 如果next_page记录的地址不存在那么就返回首页
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # 综上，登录后要么重定向至跳转前的页面，要么跳转至首页
        return redirect(next_page)
    # 一定要有返回体，否则用户未登陆时候会报错
    return render_template('login.html', title='登录', form=form)


# 注销登录
@app.route('/logout')
def logout():
    # 将用户信息保存在session中
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    # 是否是post请求且数据是是否有效
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜你成为我们网站的新用户!')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)


# 用户中心
@app.route('/user/<username>')
# 添加装饰器@login_required，必须登录之后才能访问该route
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # result = Post.query.all()
    # for a in result:
    #     print('title:%s' % a.title)
    posts = [
        {'author': user, 'body': '测试Post #1号'},
        {'author': user, 'body': '测试Post #2号'}
    ]
    return render_template('user.html', user=user, posts=posts)


# 中户中心显示最后登录时间
@app.before_request
def before_request():
    if current_user.is_authenticated:
        # 系统世界标准时间
        # current_user.last_seen = datetime.utcnow()
        # 系统本地时间
        current_user.last_seen = datetime.now()
        db.session.commit()


# 编辑个人资料
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    # 是否是post请求且数据是是否有效
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('用户名或签名变更成功')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='个人资料编辑', form=form)


# 发表文章
@app.route('/send_post', methods=['GET', 'POST'])
@login_required
def send_post():
    form = SendPostForm()
    # 如果是post请求且数据格式正确
    if form.validate_on_submit():
        # 获取当前已登录用户id
        userId = current_user.id
        # 获取提交文章时间
        sendTime = datetime.now().strftime("%Y-%m-%d %H:%M")
        # 将数据放到post
        post = Post(title=form.post_title.data, body=form.post_body.data, user_id=userId, post_time=sendTime)
        # 将post提交到数据库
        db.session.add(post)
        db.session.commit()
        flash('文章发布成功!')
    return render_template('send_post.html', title='发文章', form=form)


# 文章管理
@app.route('/post_manager')
@login_required
def post_manager():
    # 获取当前已登录用户id
    userId = current_user.id
    # 查询属于当前已登录用户的所有文章
    posts = Post.query.filter_by(user_id=userId).all()
    return render_template('post_manager.html', posts=posts)


# 编辑文章
@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = EditPostForm()
    post_info = Post.query.filter_by(id=post_id).first_or_404()
    # 是否是post请求且数据是是否有效
    if form.validate_on_submit():
        post_info.title = form.post_title.data
        post_info.body = form.post_body.data
        db.session.commit()
        flash('文章修改成功')
        return redirect(url_for('post_manager'))
    elif request.method == 'GET':
        # 在表单中显示当前要编辑文章的标题与内容
        form.post_title.data = post_info.title
        form.post_body.data = post_info.body
    return render_template('edit_post.html', form=form)


# 删除文章
@app.route('/dele_post/<post_id>', methods=['GET'])
@login_required
def dele_post(post_id):
    # 根据文章id查询到文章数据
    post_info = Post.query.filter_by(id=post_id).first_or_404()
    db.session.delete(post_info)
    db.session.commit()
    # 删除后返回文章管理页面
    return redirect(url_for('post_manager'))
