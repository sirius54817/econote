# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.shop import shop_bp
    from app.routes.subscription import subscription_bp
    from app.routes.admin import admin_bp  
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp, url_prefix='/shop')
    app.register_blueprint(subscription_bp, url_prefix='/subscription')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app
