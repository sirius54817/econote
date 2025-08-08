from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.product import Product
from app.models.order import Order
from app import db
import json

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/')
def products():
    products = Product.query.all()
    return render_template('shop/products.html', products=products)

@shop_bp.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to add items to cart', 'warning')
        return redirect(url_for('auth.login'))
    
    product = Product.query.get_or_404(product_id)
    
    # Use session to manage cart
    cart = session.get('cart', [])
    cart.append({
        'id': product.id,
        'title': product.title,
        'price': product.price
    })
    session['cart'] = cart
    
    flash(f'{product.title} added to cart', 'success')
    return redirect(url_for('shop.products'))

@shop_bp.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please log in to view cart', 'warning')
        return redirect(url_for('auth.login'))
    
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    
    return render_template('shop/cart.html', cart=cart, total=total)

@shop_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please log in to checkout', 'warning')
        return redirect(url_for('auth.login'))
    
    cart = session.get('cart', [])
    
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop.products'))
    
    if request.method == 'POST':
        total_price = sum(item['price'] for item in cart)
        
        try:
            # Create order
            order = Order(
                user_id=session['user_id'],
                items=json.dumps(cart),
                total_price=total_price,
                status='Completed'
            )
            db.session.add(order)
            db.session.commit()
            
            # Clear cart after successful order
            session.pop('cart', None)
            
            flash('Order placed successfully!', 'success')
            return redirect(url_for('main.home'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Order failed: {str(e)}', 'danger')
    
    total = sum(item['price'] for item in cart)
    return render_template('shop/checkout.html', cart=cart, total=total)