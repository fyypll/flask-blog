from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
# 导入各个表单处理方法(form.py文件)
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SendPostForm, EditPostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter


# 首页
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='我的', user=user)


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
        # 如果next_page记录的地址不存在那么就返回首页
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # 登录后要么重定向至跳转前的页面，要么跳转至首页
        return redirect(next_page)
    # 一定要有返回体，否则用户未登录时候会报错
    return render_template('login.html', title='登录', form=form)


# 注销登录
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# 用户注册
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
        flash('恭喜您成为我们网站的新用户啦!')
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
    return render_template('user.html', title='用户中心', user=user)


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
        flash('个人资料变更成功!')
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
        flash('文章已发布，快去看看吧!')
    return render_template('send_post.html', title='发文章', form=form)


# 文章管理
@app.route('/post_manager')
@login_required
def post_manager():
    # 获取当前已登录用户id
    userId = current_user.id
    # 查询属于当前已登录用户的所有文章
    posts = Post.query.filter_by(user_id=userId).all()
    # 每页显示多少文章
    per_page = 12
    # 总的有多少篇文章，使用len函数进行统计
    total = len(posts)
    # 获取页码，默认为第一页(刚开始取不到页码数据，默认为1)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # 每一页开始的位置
    start = (page - 1) * per_page
    # 每一页结束的位置
    end = start + per_page
    # 使用Pagination函数进行分页，使用bootstrap3模板，
    pagination = Pagination(bs_version=3, page=page, total=total)
    # 对文章进行切片(每12篇切一次)
    articles = posts[slice(start, end)]
    # print(articles)
    context = {
        'pagination': pagination,
        'articles': articles
    }
    return render_template('post_manager.html', title='文章管理', **context)


# 编辑文章
@app.route('/edit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    form = EditPostForm()
    # 获取编辑按钮传过来的文章id
    post_id = request.args.get('post_id')
    # 根据文章id查询文章数据
    post_info = Post.query.filter_by(id=post_id).first_or_404()
    # 如果当前登录用户id是文章作者id，则允许对文章进行修改
    if current_user.id == post_info.user_id:
        # 是否是post请求且数据是是否有效
        if form.validate_on_submit():
            post_info.title = form.post_title.data
            post_info.body = form.post_body.data
            db.session.commit()
            flash('文章更新成功!')
            return redirect(url_for('post_manager'))
        elif request.method == 'GET':
            # 在表单中显示当前要编辑文章的标题与内容
            form.post_title.data = post_info.title
            form.post_body.data = post_info.body
    # 如果文章不属于登录用户则返回管理界面
    else:
        flash('这篇文章不是你写的哦!')
        return redirect(url_for('post_manager'))
    return render_template('edit_post.html', title='文章编辑', form=form, )


# 删除文章
# 另一种接收get参数的方式
@app.route('/dele_post/<post_id>', methods=['GET'])
@login_required
def dele_post(post_id):
    # 根据文章id查询到文章数据
    post_info = Post.query.filter_by(id=post_id).first_or_404()
    db.session.delete(post_info)
    db.session.commit()
    flash('文章已成功删除!')
    # 删除后返回文章管理页面
    return redirect(url_for('post_manager'))


# 文章相关api
# 获取所有用户文章数据
@app.route('/api/post', methods=['GET'])
def post():
    data = Post.query.all()
    posts = []
    for postdata in data:
        # 使用类中的to_json函数进行处理
        posts.append(postdata.to_json())
    # print(jsonify(posts))
    return jsonify(posts)


# 获取指定页数文章数据
@app.route('/api/post_info', methods=['GET'])
def post_info():
    # 获取前端传过来的页数
    page = int(request.args.get('page'))
    # 查询所有文章
    posts = Post.query.all()
    # 每页显示多少文章
    per_page = 12
    # 总的有多少篇文章，使用len函数进行统计
    total = len(posts)
    # 每一页开始的位置
    start = (page - 1) * per_page
    # 每一页结束的位置
    end = start + per_page
    # 使用Pagination函数进行分页，使用bootstrap3模板，
    pagination = Pagination(page=page, total=total)
    # 对文章进行切片(每12篇切一次)
    articles = posts[slice(start, end)]
    # 定义数组posts用于接收切片且json化后的数据
    posts = []
    # 将切片后的数据进行json化处理
    for postdata in articles:
        # 使用类中的to_json函数进行处理
        posts.append(postdata.to_json())
    # print(posts)
    return jsonify(posts)
