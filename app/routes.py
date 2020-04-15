from flask import render_template, flash, redirect, url_for, request, jsonify, json
import requests
from sqlalchemy.sql import exists

from app import app, db
# 导入各个表单处理方法(form.py文件)
from app.blueprints.LogOrReg import LogOrReg_bp
from app.blueprints.home import home_bp
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, EditUserForm, \
    LiuYanForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Liuyan, Comments
from werkzeug.urls import url_parse
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter
from app.publlic_fun.publlic_fun import getuser, fenye


app.register_blueprint(home_bp)
app.register_blueprint(LogOrReg_bp)

# 用户中心
@app.route('/user/<username>')
# 添加装饰器@login_required，必须登录之后才能访问该route
@login_required
def user(username):
    users = getuser()
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('admin/user.html', title='个人中心', user=user, users=users)


# 编辑个人资料
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    users = getuser()
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
    return render_template('admin/edit_profile.html', title='个人资料编辑', form=form, users=users)


# 发表文章
@app.route('/send_post', methods=['GET', 'POST'])
@login_required
def send_post():
    form = PostForm()
    users = getuser()
    # 如果是post请求且数据格式正确
    if form.validate_on_submit():
        # 获取当前已登录用户id
        userId = current_user.id
        # 获取提交文章时间
        sendTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 将数据放到post
        post = Post(title=form.post_title.data, body=form.post_body.data, user_id=userId, post_time=sendTime)
        # 将post提交到数据库
        db.session.add(post)
        db.session.commit()
        flash('文章已发布，快去看看吧!')
        return redirect(url_for('post_manager'))
    return render_template('admin/send_post.html', title='发文章', form=form, users=users)


# 文章管理
@app.route('/post_manager')
@login_required
def post_manager():
    users = getuser()
    # 获取当前已登录用户id
    userId = current_user.id
    # 查询属于当前已登录用户的所有文章
    posts = Post.query.filter_by(user_id=userId).order_by(Post.post_time.desc()).all()
    # 分页
    (pagination, postdata) = fenye(12, posts, 'json')
    return render_template('admin/post_manager.html', title='我的文章', articles=postdata, pagination=pagination, users=users)


# 用户文章管理(管理员)
@app.route('/all_post_manager')
@login_required
def all_post_manager():
    users = getuser()
    # 获取当前已登录用户id
    userId = current_user.id
    if userId == 1:
        # 查询除了管理员以外的所有文章
        # filter可以多表联接查询，同时查询多张表信息一次性输出
        posts = db.session.query(Post.post_time, Post.title, Post.id, User.username).filter(
            Post.user_id == User.id).filter(Post.user_id != 1).order_by(Post.post_time.desc()).all()
        # 分页
        (pagination, postdata) = fenye(12, posts, 'nojson')
        return render_template('admin/all_post_manager.html', title='用户文章管理', articles=postdata, pagination=pagination,
                               users=users)
    else:
        return redirect(url_for('admin/post_manager'))


# 编辑文章
@app.route('/edit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    users = getuser()
    form = PostForm()
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
    return render_template('admin/edit_post.html', title='文章编辑', form=form, users=users)


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
    users = getuser()
    # 获取当前已登录用户id
    userId = current_user.id
    if userId == 1:
        # 排除管理员，也就是id为1的用户
        users_info = User.query.filter(User.id != 1).all()
        # 分页
        (pagination, users_info) = fenye(12, users_info, 'nojson')
        return render_template('admin/user_manager.html', title='用户管理', pagination=pagination, users_info=users_info,
                               users=users)
    else:
        return redirect(url_for('post_manager'))


# 编辑用户信息（管理员可用）
@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    users = getuser()
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
        return render_template('admin/edit_user.html', title='编辑用户信息', form=form, users=users)
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
    form = LiuYanForm()
    liuyandata = []
    if request.method == 'GET':
        # 倒序排序，依据为时间
        liuyan = Liuyan.query.order_by(Liuyan.send_time.desc()).all()
        for ly in liuyan:
            # 使用类中的to_json函数进行处理
            liuyandata.append(ly.to_json())
    else:
        send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        username = form.username.data
        email = form.email.data
        body = form.body.data
        liuyan = Liuyan(username=username, email=email, body=body, send_time=send_time)
        # 判断评论长度
        if len(form.body.data) < 5:
            flash('评论字数最低5字哦!')
            return redirect(url_for('liuyan'))
        elif len(form.body.data) > 1000:
            flash('评论字数最多1000字哦!')
            return redirect(url_for('liuyan'))
        # 如果发的评论在数据库表中已经存在
        if db.session.query(exists().where(Liuyan.body == body)).scalar():
            flash('不可发布重复评论')
            return redirect(url_for('liuyan'))
        else:
            db.session.add(liuyan)
            db.session.commit()
            return redirect(url_for('liuyan'))
    # 分页
    (pagination, liuyandata) = fenye(12, liuyandata, 'nojson')
    return render_template('front/liuyan.html', form=form, pagination=pagination, liuyandata=liuyandata)


# 文章详情页
@app.route('/post_info', methods=['GET', 'POST'])
def post_info():
    form = LiuYanForm()
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
        comments_info = Comments.query.filter_by(post_id=post_id).order_by(Comments.send_time.desc()).all()
        # 评论分页
        (pagination, liuyandata) = fenye(12, comments_info, 'json')
    else:
        send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        username = form.username.data
        email = form.email.data
        body = form.body.data
        comments = Comments(username=username, email=email, body=body, send_time=send_time, post_id=post_id)
        # 判断评论长度
        if len(form.body.data) < 5:
            flash('评论字数最低5字哦!')
            return redirect(url_for('post_info', post_id=post_id))
        elif len(form.body.data) > 1000:
            flash('评论字数最多1000字哦!')
            return redirect(url_for('post_info', post_id=post_id))
        # 如果发的评论在数据库表中已经存在
        if db.session.query(exists().where(Comments.body == body)).scalar():
            flash('不可发布重复评论')
            return redirect(url_for('post_info', post_id=post_id))
        else:
            db.session.add(comments)
            db.session.commit()
            return redirect(url_for('post_info', post_id=post_id))
    return render_template('front/post.html', post_info=post_info, username=username, form=form, pagination=pagination,
                           liuyandata=liuyandata)


# 评论管理
@app.route('/comm_manager', methods=['GET'])
@login_required
def comm_manager():
    users = getuser()
    user_id = current_user.id
    # 获取当前登录用户所属文章的所有评论,lable()设置字段别名，避免相同字段干扰
    comm_info = db.session.query(Post.title, Post.id.label('postId'), Comments.id, Comments.username, Comments.body,
                                 Comments.send_time,
                                 Comments.email).filter(
        Post.user_id == user_id).filter(
        Comments.post_id == Post.id).order_by(Comments.send_time.desc()).all()
    # 分页
    (pagination, comm_info) = fenye(12, comm_info, 'nojson')
    return render_template('admin/comm_manager.html', users=users, pagination=pagination, comm_info=comm_info)


# 删除评论
@app.route('/comm_del', methods=['GET'])
@login_required
def comm_del():
    comm_id = request.args.get('comm_id')
    comm_info = Comments.query.filter_by(id=comm_id).first_or_404()
    db.session.delete(comm_info)
    db.session.commit()
    flash('用户评论已成功删除!')
    # 删除后返回评论管理页面
    return redirect(url_for('comm_manager'))


# 留言管理(管理员)
@app.route('/liuyan_manager', methods=['GET'])
@login_required
def liuyan_manager():
    users = getuser()
    # 如果不是管理员
    if current_user.id != 1:
        return redirect(url_for('comm_manager'))
    else:
        liuyan_info = Liuyan.query.order_by(Liuyan.send_time.desc()).all()
        # 分页
        (pagination, liuyan_info) = fenye(12, liuyan_info, 'nojson')
    return render_template('admin/liuyan_manager.html', users=users, pagination=pagination, liuyan_info=liuyan_info)


# 删除留言(管理员)
@app.route('/liuyan_del', methods=['GET'])
@login_required
def liuyan_del():
    liuyan_id = request.args.get('liuyan_id')
    liuyan_info = Liuyan.query.filter_by(id=liuyan_id).first_or_404()
    db.session.delete(liuyan_info)
    db.session.commit()
    flash('留言已成功删除!')
    # 删除后返回评论管理页面
    return redirect(url_for('liuyan_manager'))


# 留言编辑(管理员)
@app.route('/edit_liuyan', methods=['GET', 'POST'])
@login_required
def edit_liuyan():
    users = getuser()
    form = LiuYanForm()
    liuyan_id = request.args.get('liuyan_id')
    liuyan_info = Liuyan.query.filter_by(id=liuyan_id).first_or_404()
    if current_user.id == 1:
        if form.validate_on_submit():
            liuyan_info.username = form.username.data
            liuyan_info.email = form.email.data
            liuyan_info.body = form.body.data
            db.session.commit()
            flash('留言已成功更新!')
            return redirect(url_for('liuyan_manager'))
        elif request.method == 'GET':
            form.username.data = liuyan_info.username
            form.email.data = liuyan_info.email
            form.body.data = liuyan_info.body
        return render_template('admin/edit_liuyan.html', users=users, form=form)
    else:
        return redirect(url_for('comm_manager'))


# 所有评论管理(管理员)
@app.route('/all_comm_manager', methods=['GET'])
@login_required
def all_comm_manager():
    users = getuser()
    if current_user.id == 1:
        comm_info = db.session.query(Post.title, Post.id.label('postId'), Comments.id, Comments.username,
                                     Comments.email,
                                     Comments.send_time, Comments.body).filter(Comments.post_id == Post.id).order_by(
            Comments.send_time.desc()).all()
        # 分页
        (pagination, comm_info) = fenye(12, comm_info, 'nojson')
        return render_template('admin/all_comm_manager.html', users=users, pagination=pagination, comm_info=comm_info)
    else:
        return redirect(url_for('comm_manager'))


# 评论编辑
@app.route('/edit_comm', methods=['GET', 'POST'])
@login_required
def edit_comm():
    users = getuser()
    form = LiuYanForm()
    comm_id = request.args.get('comm_id')
    comm_info = Comments.query.filter_by(id=comm_id).first_or_404()
    # 获取当前编辑的评论是不是这个作者的文章里面的评论
    userId = db.session.query(Post.user_id).filter(Comments.id == comm_id).filter(
        Comments.post_id == Post.id).first_or_404()
    # 如果用户编辑的这条评论是该用户所属文章中的评论
    if current_user.id == userId.user_id:
        if form.validate_on_submit():
            comm_info.username = form.username.data
            comm_info.email = form.email.data
            comm_info.body = form.body.data
            db.session.commit()
            flash('评论已成功更新!')
            return redirect(url_for('comm_manager'))
        elif request.method == 'GET':
            form.username.data = comm_info.username
            form.email.data = comm_info.email
            form.body.data = comm_info.body
        return render_template('admin/edit_comm.html', users=users, form=form)
    else:
        flash('你无权修改这条评论哦!')
        return redirect(url_for('comm_manager'))


# 用户个人博客首页
@app.route('/<username>')
def user_index(username):
    user = User.query.filter(User.username == username).first_or_404()
    userId = user.id
    posts = Post.query.filter(Post.user_id == userId).order_by(Post.post_time.desc()).all()
    # 分页
    (pagination, postdata) = fenye(12, posts, 'json')
    return render_template('front/user_index.html', pagination=pagination, postdata=postdata)
