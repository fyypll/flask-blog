from app import app
from app.blueprints.LogOrReg import LogOrReg_bp
from app.blueprints.comments import comments_bp
from app.blueprints.home import home_bp
from app.blueprints.liuyanban import liuyanban_bp
from app.blueprints.post import post_bp
from app.blueprints.user import user_bp


app.register_blueprint(home_bp)
app.register_blueprint(LogOrReg_bp)
app.register_blueprint(liuyanban_bp)
app.register_blueprint(user_bp)
app.register_blueprint(post_bp)
app.register_blueprint(comments_bp)