from flask import render_template, flash, redirect, url_for, request
from sqlalchemy.sql import exists

from app import app, db
# 导入各个表单处理方法(form.py文件)
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SendPostForm, EditPostForm, EditUserForm, \
    SendLiuYanForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Liuyan, Comments
from werkzeug.urls import url_parse
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter


# 首页
@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    # 获取页码，若失败则取默认值1
    page = request.args.get(get_page_parameter(), type=int, default=1)
    posts = Post.query.order_by(Post.post_time.desc()).all()
    # 每页显示多少文章
    per_page = 12
    total = len(posts)
    start = (page - 1) * per_page
    end = start + per_page
    pagination = Pagination(page=page, total=total)
    # 对文章进行切片(每12篇切一次)
    articles = posts[slice(start, end)]
    posts = []
    # 将切片后的数据进行json化处理
    for postdata in articles:
        # 使用类中的to_json函数进行处理
        posts.append(postdata.to_json())
    return render_template('index.html', pagination=pagination, posts=posts)


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

        # 记录登录时间
        current_user.last_seen = datetime.now()
        db.session.commit()

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
    return render_template('user.html', title='个人中心', user=user)


# # 中户中心显示最后登录时间
# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         # 系统世界标准时间
#         # current_user.last_seen = datetime.utcnow()
#         # 系统本地时间
#         current_user.last_seen = datetime.now()
#         db.session.commit()


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
    posts = Post.query.filter_by(user_id=userId).order_by(Post.post_time.desc()).all()
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
    # 使用Pagination函数进行分页，使用bootstrap3模板
    pagination = Pagination(bs_version=3, page=page, total=total)
    # 对文章进行切片(每12篇切一次)
    articles = posts[slice(start, end)]
    # print(articles)
    context = {
        'pagination': pagination,
        'articles': articles
    }
    return render_template('post_manager.html', title='我的文章', **context)


# 用户文章管理(管理员)
@app.route('/all_post_manager')
@login_required
def all_post_manager():
    # 获取当前已登录用户id
    userId = current_user.id
    if userId == 1:
        # 查询除了管理员以外的所有文章
        posts = Post.query.filter(Post.user_id != 1).order_by(Post.post_time.desc()).all()
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
        # 使用Pagination函数进行分页，使用bootstrap3模板
        pagination = Pagination(bs_version=3, page=page, total=total)
        # 对文章进行切片(每12篇切一次)
        articles = posts[slice(start, end)]
        # print(articles)
        context = {
            'pagination': pagination,
            'articles': articles
        }
        return render_template('all_post_manager.html', title='用户文章管理', **context)
    else:
        return redirect(url_for('post_manager'))


# 编辑文章
@app.route('/edit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    form = EditPostForm()
    # 获取编辑按钮传过来的文章id
    post_id = request.args.get('post_id')
    # 根据文章id查询文章数据
    post_info = Post.query.filter_by(id=post_id).first_or_404()
    # 如果当前登录用户id是文章作者id，或者是管理员，则允许对文章进行修改
    if current_user.id == post_info.user_id or current_user.id == 1:
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
    return render_template('edit_post.html', title='文章编辑', form=form)


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


# 用户管理（管理员可用）
@app.route('/user_manager')
@login_required
def user_manager():
    # 获取当前已登录用户id
    userId = current_user.id
    if userId == 1:
        # 排除管理员，也就是id为1的用户
        users = User.query.filter(User.id != 1).all()
        per_page = 12
        total = len(users)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        start = (page - 1) * per_page
        end = start + per_page
        pagination = Pagination(bs_version=3, page=page, total=total)
        usersData = users[slice(start, end)]
        context = {
            'pagination': pagination,
            'users': usersData
        }
        return render_template('user_manager.html', title='用户管理', **context)
    else:
        return redirect(url_for('post_manager'))


# 编辑用户信息（管理员可用）
@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditUserForm()
    user_id = request.args.get('user_id')
    user_info = User.query.filter(User.id == user_id).first_or_404()
    if current_user.id == 1:
        # 是否是post请求且数据是是否有效
        if form.validate_on_submit():
            user_info.username = form.username.data
            user_info.email = form.email.data
            user_info.about_me = form.about_me.data
            db.session.commit()
            flash('用户信息更新成功!')
            return redirect(url_for('user_manager'))
        elif request.method == 'GET':
            form.username.data = user_info.username
            form.email.data = user_info.email
            form.about_me.data = user_info.about_me
        return render_template('edit_user.html', title='编辑用户信息', form=form)
    else:
        return redirect(url_for('post_manager'))


# 删除用户
@app.route('/dele_user', methods=['GET'])
@login_required
def dele_user():
    user_id = request.args.get('user_id')
    user_info = User.query.filter_by(id=user_id).first_or_404()
    db.session.delete(user_info)
    db.session.commit()
    flash('用户已成功删除!')
    # 删除后返回文章管理页面
    return redirect(url_for('user_manager'))


# 留言板
@app.route('/liuyan', methods=['GET', 'POST'])
def liuyan():
    form = SendLiuYanForm()
    liuyandata = []
    if request.method == 'GET':
        # 倒序排序，依据为时间
        liuyan = Liuyan.query.order_by(Liuyan.send_time.desc()).all()
        for ly in liuyan:
            # 使用类中的to_json函数进行处理
            liuyandata.append(ly.to_json())
    else:
        send_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        username = form.username.data
        email = form.email.data
        body = form.body.data
        liuyan = Liuyan(username=username, email=email, body=body, send_time=send_time)
        # 如果发的评论在数据库表中已经存在
        if db.session.query(exists().where(Liuyan.body == body)).scalar():
            flash('不可发布重复评论')
            return redirect(url_for('liuyan'))
        else:
            db.session.add(liuyan)
            db.session.commit()
            return redirect(url_for('liuyan'))
    # 分页
    per_page = 12
    total = len(liuyandata)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    end = start + per_page
    pagination = Pagination(page=page, total=total)
    # 对文章进行切片
    liu = liuyandata[slice(start, end)]
    context = {
        'pagination': pagination,
        'liuyandata': liu
    }
    return render_template('liuyan.html', form=form, **context)


# 文章详情页
@app.route('/post_info', methods=['GET', 'POST'])
def post_info():
    form = SendLiuYanForm()
    post_id = request.args.get('post_id')
    post_data = []
    # 根据文章id查询文章数据
    post_info = Post.query.filter_by(id=post_id).first_or_404()
    post_data.append(post_info.to_json())
    # 查询文章作者
    post_user = User.query.filter_by(id=post_info.user_id).first_or_404()
    username = post_user.username

    if request.method == 'GET':
        # 文章评论
        commentsData = []
        comments_info = Comments.query.filter_by(post_id=post_id).order_by(Comments.send_time.desc()).all()
        for cm_inf in comments_info:
            # 使用类中的to_json函数进行处理
            commentsData.append(cm_inf.to_json())
        # 分页
        per_page = 12
        total = len(commentsData)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        start = (page - 1) * per_page
        end = start + per_page
        pagination = Pagination(page=page, total=total)
        # 对文章进行切片
        comments = commentsData[slice(start, end)]
        context = {
            'pagination': pagination,
            'liuyandata': comments
        }
    else:
        send_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        username = form.username.data
        email = form.email.data
        body = form.body.data
        comments = Comments(username=username, email=email, body=body, send_time=send_time, post_id=post_id)
        # 如果发的评论在数据库表中已经存在
        if db.session.query(exists().where(Comments.body == body)).scalar():
            flash('不可发布重复评论')
            return redirect(url_for('post_info', post_id=post_id))
        else:
            db.session.add(comments)
            db.session.commit()
            return redirect(url_for('post_info', post_id=post_id))
    return render_template('post.html', post_info=post_info, username=username, form=form, **context)
