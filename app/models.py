from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login
from hashlib import md5


# 用户
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # back是反向引用,User和Post是一对多的关系，backref是表示在Post中新建一个属性author，关联的是Post中的user_id外键关联的User对象。
    # lazy属性常用的值的含义，select就是访问到属性的时候，就会全部加载该属性的数据;joined则是在对关联的两个表进行join操作
    # 从而获取到所有相关的对象;dynamic则不一样，在访问属性的时候，并没有在内存中加载数据，而是返回一个query对象, 需要执行相应方法才可以获取对象，比如.all()
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<用户名:{}>'.format(self.username)

    # 对用户密码进行加密
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 检测密码是否正确
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 用户avatar头像
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


# 文章
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    post_time = db.Column(db.DateTime, default=datetime.now)
    comms = db.relationship('Comments', backref='comments', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return '<body:{}>'.format(self.body)
        # return '{}>'.format(self)

    # 定义一个to_json的方法，使用dict方法来返回类中的属性字典
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 留言
class Liuyan(db.Model):
    __tablename__ = 'liuyan'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    body = db.Column(db.Text)
    email = db.Column(db.String(120))
    send_time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<body:{}>'.format(self.body)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 评论
class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    body = db.Column(db.Text)
    email = db.Column(db.String(120))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    send_time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<body:{}>'.format(self.body)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 用户加载
@login.user_loader
def load_user(id):
    # 读取session中的id然后将其转换为int类型
    return User.query.get(int(id))
