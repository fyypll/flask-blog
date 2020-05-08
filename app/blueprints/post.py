import os
from datetime import datetime

from PIL import Image
from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user
from sqlalchemy.sql import exists
from werkzeug.utils import secure_filename

from app import db
from app.forms import PostForm, LiuYanForm
from app.models import Post, User, Comments
from app.publlic_fun.publlic_fun import getuser, fenye

post_bp = Blueprint('post', __name__)

# 获取上一级目录
UPLOAD_PATH = os.path.join(os.path.dirname(__file__), os.path.pardir, 'static/upload/pic')


# 发表文章
@post_bp.route('/send_post', methods=['GET', 'POST'])
@login_required
def send_post():
    form = PostForm()
    users = getuser()
    # 如果是post请求且数据格式正确
    if form.validate_on_submit():
        # 如果传的文件不为空
        if form.post_pic.data is not None:
            # 上传的图片
            post_pic = form.post_pic.data
            # 验证上传文件类型
            filename = secure_filename(post_pic.filename)
            # 获取图片上传时间
            ftime = datetime.now().strftime('%Y%m%d%H%M%S%f')
            # 获取图片后缀
            pic_suffix = os.path.splitext(filename)[1]
            # 文件重命名
            rename_pic = ftime + pic_suffix
            # 拼接文件路径（包括文件名）
            pic_path = os.path.join(UPLOAD_PATH, rename_pic)
            # 保存文件
            post_pic.save(pic_path)

            # 压缩图片
            im = Image.open(pic_path)
            im.thumbnail((256, 192))
            # print(im.format, im.size, im.mode)
            im.save(pic_path)
        else:
            # 没有传封面图片就用默认封面
            rename_pic = '01.jpg'
        # 获取当前已登录用户id
        userId = current_user.id
        # 获取提交文章时间
        sendTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 将数据放到post
        post = Post(title=form.post_title.data, body=form.post_body.data, user_id=userId, post_time=sendTime,
                    pic_url=rename_pic)
        # 将post提交到数据库
        db.session.add(post)
        db.session.commit()
        flash('文章已发布，快去看看吧!')
        return redirect(url_for('post.post_manager'))
    return render_template('admin/send_post.html', title='发文章', form=form, users=users)


# 文章管理
@post_bp.route('/post_manager')
@login_required
def post_manager():
    users = getuser()
    # 获取当前已登录用户id
    userId = current_user.id
    # 查询属于当前已登录用户的所有文章
    posts = Post.query.filter_by(user_id=userId).order_by(Post.post_time.desc()).all()
    # 分页
    (pagination, postdata) = fenye(12, posts, 'json')
    return render_template('admin/post_manager.html', title='我的文章', articles=postdata, pagination=pagination,
                           users=users)


# 用户文章管理(管理员)
@post_bp.route('/all_post_manager')
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
        return redirect(url_for('post.post_manager'))


# 编辑文章
@post_bp.route('/edit_post', methods=['GET', 'POST'])
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
            if form.post_pic.data is not None:
                # 如果封面不是默认封面
                if post_info.pic_url != '01.jpg':
                    # 如果原封面文件存在，那么删除
                    if os.path.exists(post_info.pic_url):
                        # 删除原文章封面文件
                        os.remove(os.path.join(os.path.dirname(__file__), '../static/upload/pic', post_info.pic_url))
                else:
                    pass
                # 上传的图片
                post_pic = form.post_pic.data
                # 验证上传文件类型
                filename = secure_filename(post_pic.filename)
                # 获取图片上传时间
                ftime = datetime.now().strftime('%Y%m%d%H%M%S%f')
                # 获取图片后缀
                pic_suffix = os.path.splitext(filename)[1]
                # 文件重命名
                rename_pic = ftime + pic_suffix
                # 拼接文件路径（包括文件名）
                pic_path = os.path.join(UPLOAD_PATH, rename_pic)
                # 保存文件
                post_pic.save(pic_path)

                # 压缩图片
                im = Image.open(pic_path)
                im.thumbnail((256, 192))
                # print(im.format, im.size, im.mode)
                im.save(pic_path)
            else:
                # 没有传封面图片就用默认封面
                rename_pic = '01.jpg'
                # 且删除原封面(如果不是默认封面的话)，避免删掉默认封面图
                if post_info.pic_url == '01.jpg':
                    pass
                else:
                    # 如果原封面文件存在，那么删除
                    if os.path.exists(post_info.pic_url):
                        os.remove(os.path.join(os.path.dirname(__file__), '../static/upload/pic', post_info.pic_url))
            post_info.pic_url = rename_pic
            post_info.title = form.post_title.data
            post_info.body = form.post_body.data
            db.session.commit()
            flash('文章更新成功!')
            return redirect(url_for('post.post_manager'))
        elif request.method == 'GET':
            # 在表单中显示当前要编辑文章的标题与内容
            form.post_title.data = post_info.title
            form.post_body.data = post_info.body
    # 如果文章不属于登录用户则返回管理界面
    else:
        flash('这篇文章不是你写的哦!')
        return redirect(url_for('post.post_manager'))
    return render_template('admin/edit_post.html', title='文章编辑', form=form, users=users)


# 删除文章
# 另一种接收get参数的方式
@post_bp.route('/dele_post/<post_id>', methods=['GET'])
@login_required
def dele_post(post_id):
    # 根据文章id查询到文章数据
    post_info = Post.query.filter_by(id=post_id).first_or_404()
    db.session.delete(post_info)
    db.session.commit()
    flash('文章已成功删除!')
    # 删除后返回文章管理页面
    return redirect(url_for('post.post_manager'))


# 文章详情页
@post_bp.route('/post_info', methods=['GET', 'POST'])
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
            return redirect(url_for('post.post_info', post_id=post_id))
        elif len(form.body.data) > 1000:
            flash('评论字数最多1000字哦!')
            return redirect(url_for('post.post_info', post_id=post_id))
        # 如果发的评论在数据库表中已经存在
        if db.session.query(exists().where(Comments.body == body)).scalar():
            flash('不可发布重复评论')
            return redirect(url_for('post.post_info', post_id=post_id))
        else:
            db.session.add(comments)
            db.session.commit()
            return redirect(url_for('post.post_info', post_id=post_id))
    return render_template('front/post.html', post_info=post_info, username=username, form=form, pagination=pagination,
                           liuyandata=liuyandata)
