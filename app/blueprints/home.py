from flask import Blueprint, render_template

from app.models import Post, User
from app.publlic_fun.publlic_fun import fenye

home_bp = Blueprint('home', __name__)


# 首页
@home_bp.route('/')
@home_bp.route('/index', methods=['GET'])
def index():
    # 获取页码，若失败则取默认值1
    # page = request.args.get(get_page_parameter(), type=int, default=1)
    posts = Post.query.order_by(Post.post_time.desc()).all()
    # 分页
    (pagination, postdata) = fenye(12, posts, 'json')
    return render_template('front/index.html', pagination=pagination, posts=postdata)


# 用户个人博客首页
@home_bp.route('/<username>')
def user_index(username):
    user = User.query.filter(User.username == username).first_or_404()
    userId = user.id
    posts = Post.query.filter(Post.user_id == userId).order_by(Post.post_time.desc()).all()
    # 分页
    (pagination, postdata) = fenye(12, posts, 'json')
    return render_template('front/user_index.html', pagination=pagination, postdata=postdata)