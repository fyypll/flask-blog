from flask import Flask
# 导入配置文件
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# 登录模块
from flask_login import LoginManager

# 创建app应用,__name__是python预定义变量，被设置为使用本模块.
app = Flask(__name__)

# 添加配置信息
app.config.from_object(Config)

# 连接数据库
db = SQLAlchemy(app)
# 绑定app和数据库，方便后面的操作
migrate = Migrate(app, db)

# 初始化登录模块
login = LoginManager(app)
# 加在login = LoginManager(app)后面，位置不能错
# 不让未登录的用户进入除了login之外的界面
login.login_view = 'login'
login.login_message = u"这个页面需要你登录才能访问哦"

# 这里放后面，位置也不能错
from app import routes, models
