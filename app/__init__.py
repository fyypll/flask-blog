from flask import Flask
# 导入配置文件
from config import Config

# 创建app应用,__name__是python预定义变量，被设置为使用本模块.
app = Flask(__name__)

# 添加配置信息
app.config.from_object(Config)

from app import routes
