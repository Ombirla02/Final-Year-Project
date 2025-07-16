import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from config.dbconnect import DatabaseConnection

db = DatabaseConnection().connection  

load_dotenv()
login_manager = LoginManager()

secret_key = os.getenv("SECRET_KEY")

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = secret_key

    # Blueprints
    from app.home import home_bp
    from app.auth import auth
    from app.learner import learner_bp
    from app.supervisor import supervisor_bp
    from app.industry import industry_bp
    from app.errors import error_bp


    app.register_blueprint(home_bp)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(learner_bp, url_prefix='/learner')
    app.register_blueprint(supervisor_bp, url_prefix='/supervisor')
    app.register_blueprint(industry_bp, url_prefix='/industry')
    app.register_blueprint(error_bp)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(email):
        from app.models import User
        user_data = db.users.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None
        
    return app