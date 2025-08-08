# app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models.product import Product
from app import db
from functools import wraps
from app.extensions import bcrypt
from datetime import datetime
from flask_login import UserMixin
from app.config import Config

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

# Custom decorator to restrict access to admin users
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden if not an admin
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

@admin_bp.route('/add-product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        image = request.form.get('image')
        
        try:
            price = float(price)
        except ValueError:
            flash("Please enter a valid price", "danger")
            return redirect(url_for("admin.add_product"))
        
        new_product = Product(title=title, description=description, price=price, image=image)
        try:
            db.session.add(new_product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash("Error adding product: " + str(e), "danger")
    
    return render_template('admin/add_product.html')

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Set password with bcrypt hashing"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_admin(cls):
        """Get the admin user"""
        return cls.query.filter_by(email=Config.ADMIN_EMAIL).first()
    
    def get_id(self):
        """Return the admin ID as a string"""
        return f"admin_{self.id}"
    
    def __repr__(self):
        return f'<Admin {self.email}>'
