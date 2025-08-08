from flask import Flask
from .config import get_config
import logging
from .extensions import db, migrate, bcrypt, login_manager

def create_app(config_name='development'):
    """
    Application factory function for creating Flask app
    
    :param config_name: Configuration environment (development/testing/production)
    :return: Configured Flask application
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOGGING_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import models to ensure they're registered with SQLAlchemy
    from .models.user import User
    from .models.admin import Admin
    
    @login_manager.user_loader
    def load_user(user_id):
        # Try loading admin first
        if user_id.startswith('admin_'):
            admin_id = int(user_id.split('_')[1])
            return Admin.query.get(admin_id)
        # Then try regular user
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.shop import shop_bp
    from .routes.subscription import subscription_bp
    from .routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(shop_bp, url_prefix='/shop')
    app.register_blueprint(subscription_bp, url_prefix='/subscription')
    app.register_blueprint(admin_bp)
    
    # Create application context
    with app.app_context():
        # Import here to avoid circular imports
        from .utils.admin import init_admin
        
        # Create database tables
        db.create_all()
        init_admin()  # Initialize admin user
    
    return app