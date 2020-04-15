from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.forms import LiuYanForm
from app.models import Post, Comments
from app.publlic_fun.publlic_fun import getuser, fenye

comments_bp = Blueprint('comments', __name__)


# 评论管理
@comments_bp.route('/comm_manager', methods=['GET'])
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
@comments_bp.route('/comm_del', methods=['GET'])
@login_required
def comm_del():
    comm_id = request.args.get('comm_id')
    comm_info = Comments.query.filter_by(id=comm_id).first_or_404()
    db.session.delete(comm_info)
    db.session.commit()
    flash('用户评论已成功删除!')
    # 删除后返回评论管理页面
    return redirect(url_for('comments.comm_manager'))


# 所有评论管理(管理员)
@comments_bp.route('/all_comm_manager', methods=['GET'])
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
        return redirect(url_for('comments.comm_manager'))


# 评论编辑
@comments_bp.route('/edit_comm', methods=['GET', 'POST'])
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
            return redirect(url_for('comments.comm_manager'))
        elif request.method == 'GET':
            form.username.data = comm_info.username
            form.email.data = comm_info.email
            form.body.data = comm_info.body
        return render_template('admin/edit_comm.html', users=users, form=form)
    else:
        flash('你无权修改这条评论哦!')
        return redirect(url_for('comments.comm_manager'))
