from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models.admin import Admin
from app.models.product import Product
from app.config import Config
from app.extensions import db
from functools import wraps
from flask_login import current_user, login_required, login_user, logout_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If admin is already logged in, redirect to dashboard
    if current_user.is_authenticated and isinstance(current_user, Admin):
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email != Config.ADMIN_EMAIL:
            flash('Invalid admin credentials', 'danger')
            return redirect(url_for('admin.login'))
        
        admin = Admin.get_admin()
        
        if admin and admin.check_password(password):
            login_user(admin, remember=True)
            admin.update_last_login()
            flash('Welcome Admin!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/admin'):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid password', 'danger')
            
    return render_template('admin/login.html', admin_email=Config.ADMIN_EMAIL)

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

@admin_bp.route('/logout')
@login_required
@admin_required
def logout():
    logout_user()
    flash('Admin logged out successfully', 'success')
    return redirect(url_for('admin.login')) 