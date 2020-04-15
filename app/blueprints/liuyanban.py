from datetime import datetime

from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from sqlalchemy.sql import exists

from app import db
from app.forms import LiuYanForm
from app.models import Liuyan
from app.publlic_fun.publlic_fun import fenye, getuser

liuyanban_bp = Blueprint('liuyanban', __name__)


# 留言板
@liuyanban_bp.route('/liuyan', methods=['GET', 'POST'])
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
            return redirect(url_for('liuyanban.liuyan'))
        elif len(form.body.data) > 1000:
            flash('评论字数最多1000字哦!')
            return redirect(url_for('liuyanban.liuyan'))
        # 如果发的评论在数据库表中已经存在
        if db.session.query(exists().where(Liuyan.body == body)).scalar():
            flash('不可发布重复评论')
            return redirect(url_for('liuyanban.liuyan'))
        else:
            db.session.add(liuyan)
            db.session.commit()
            return redirect(url_for('liuyanban.liuyan'))
    # 分页
    (pagination, liuyandata) = fenye(12, liuyandata, 'nojson')
    return render_template('front/liuyan.html', form=form, pagination=pagination, liuyandata=liuyandata)


# 留言管理(管理员)
@liuyanban_bp.route('/liuyan_manager', methods=['GET'])
@login_required
def liuyan_manager():
    users = getuser()
    # 如果不是管理员
    if current_user.id != 1:
        return redirect(url_for('comments.comm_manager'))
    else:
        liuyan_info = Liuyan.query.order_by(Liuyan.send_time.desc()).all()
        # 分页
        (pagination, liuyan_info) = fenye(12, liuyan_info, 'nojson')
    return render_template('admin/liuyan_manager.html', users=users, pagination=pagination, liuyan_info=liuyan_info)


# 删除留言(管理员)
@liuyanban_bp.route('/liuyan_del', methods=['GET'])
@login_required
def liuyan_del():
    liuyan_id = request.args.get('liuyan_id')
    liuyan_info = Liuyan.query.filter_by(id=liuyan_id).first_or_404()
    db.session.delete(liuyan_info)
    db.session.commit()
    flash('留言已成功删除!')
    # 删除后返回评论管理页面
    return redirect(url_for('liuyanban.liuyan_manager'))


# 留言编辑(管理员)
@liuyanban_bp.route('/edit_liuyan', methods=['GET', 'POST'])
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
            return redirect(url_for('liuyanban.liuyan_manager'))
        elif request.method == 'GET':
            form.username.data = liuyan_info.username
            form.email.data = liuyan_info.email
            form.body.data = liuyan_info.body
        return render_template('admin/edit_liuyan.html', users=users, form=form)
    else:
        return redirect(url_for('comments.comm_manager'))
