class Config(object):
    # 设置密匙，当然是越复杂越好啦
    SECRET_KEY = 'my%name%is%maple,this%is%my%blog'
    # 格式为mysql+pymysql://数据库用户名:密码@数据库地址:端口号/数据库名?数据库编码
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/flaskblog?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
