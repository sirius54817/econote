from app.extensions import db
from app.models.admin import Admin
from app.config import Config

def init_admin():
    """Initialize admin user with default credentials"""
    try:
        # Drop existing admin table to ensure clean slate
        Admin.__table__.drop(db.engine, checkfirst=True)
        db.session.commit()
        
        # Create tables
        db.create_all()
        
        admin = Admin(
            name=Config.ADMIN_NAME,
            email=Config.ADMIN_EMAIL
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
        
    except Exception as e:
        db.session.rollback()
        print(f'Error creating admin user: {str(e)}') 