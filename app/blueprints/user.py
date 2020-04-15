from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from app import db
from app.forms import EditProfileForm, EditUserForm
from app.models import User
from app.publlic_fun.publlic_fun import getuser, fenye

user_bp = Blueprint('user', __name__)


# 用户中心
@user_bp.route('/user/<username>')
# 添加装饰器@login_required，必须登录之后才能访问该route
@login_required
def user(username):
    users = getuser()
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('admin/user.html', title='个人中心', user=user, users=users)


# 编辑个人资料
@user_bp.route('/edit_profile', methods=['GET', 'POST'])
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
        return redirect(url_for('user.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('admin/edit_profile.html', title='个人资料编辑', form=form, users=users)


# 编辑用户信息（管理员可用）
@user_bp.route('/edit_user', methods=['GET', 'POST'])
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
            return redirect(url_for('user.user_manager'))
        elif request.method == 'GET':
            form.username.data = user_info.username
            form.email.data = user_info.email
            form.about_me.data = user_info.about_me
        return render_template('admin/edit_user.html', title='编辑用户信息', form=form, users=users)
    else:
        return redirect(url_for('post.post_manager'))


# 用户管理（管理员可用）
@user_bp.route('/user_manager')
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
        return redirect(url_for('post.post_manager'))



# 删除用户
@user_bp.route('/dele_user', methods=['GET'])
@login_required
def dele_user():
    user_id = request.args.get('user_id')
    user_info = User.query.filter_by(id=user_id).first_or_404()
    db.session.delete(user_info)
    db.session.commit()
    flash('用户已成功删除!')
    # 删除后返回文章管理页面
    return redirect(url_for('user.user_manager'))