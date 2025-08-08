from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import func
from app import db
from app.models.subscription import Subscription
from app.models.user import User
from datetime import datetime, timedelta

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/plans')
def plans():
    return render_template('subscription/plans.html')

@subscription_bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if 'user_id' not in session:
        flash('Please log in to subscribe', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        plan = request.form.get('plan')
        user_id = session['user_id']
        
        if not plan:
            flash('Please select a valid subscription plan', 'danger')
            return redirect(url_for('subscription.plans'))
        
        # Deactivate existing active subscriptions
        Subscription.query.filter_by(
            user_id=user_id, 
            status='Active'
        ).update({
            'status': 'Inactive', 
            'end_date': func.current_timestamp()
        })
        
        try:
            # Create new subscription
            subscription = Subscription(
                user_id=user_id, 
                plan=plan, 
                status='Active',
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30)
            )
            db.session.add(subscription)
            db.session.commit()
            
            flash(f'Successfully subscribed to {plan} plan!', 'success')
            return redirect(url_for('subscription.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Subscription failed: {str(e)}', 'danger')
            return redirect(url_for('subscription.plans'))
    
    return render_template('subscription/plans.html')

@subscription_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to view dashboard', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Retrieve user's subscriptions
    subscriptions = Subscription.query.filter_by(
        user_id=user_id
    ).order_by(
        Subscription.start_date.desc()
    ).all()
    
    # Get active subscription
    active_subscription = Subscription.query.filter_by(
        user_id=user_id, 
        status='Active'
    ).first()
    
    return render_template(
        'subscription/dashboard.html', 
        user=user, 
        subscriptions=subscriptions,
        active_subscription=active_subscription
    )

@subscription_bp.route('/update-payment', methods=['POST'])
def update_payment():
    if 'user_id' not in session:
        flash('Please log in to update payment method', 'warning')
        return redirect(url_for('auth.login'))
    
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        # Get payment details from form
        card_number = request.form.get('card_number')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')
        
        # Basic validation
        if not all([card_number, expiry, cvv]):
            flash('Please provide complete payment information', 'danger')
            return redirect(url_for('subscription.dashboard'))
        
        # Update user's billing information
        user.billing_info = {
            'last4': card_number[-4:],
            'exp_month': expiry.split('/')[0],
            'exp_year': expiry.split('/')[1]
        }
        
        db.session.commit()
        
        flash('Payment method updated successfully', 'success')
        return redirect(url_for('subscription.dashboard'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update payment method: {str(e)}', 'danger')
        return redirect(url_for('subscription.dashboard'))

@subscription_bp.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    if 'user_id' not in session:
        flash('Please log in to cancel subscription', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        # Find and update active subscription
        active_subscription = Subscription.query.filter_by(
            user_id=user_id, 
            status='Active'
        ).first()
        
        if active_subscription:
            active_subscription.status = 'Cancelled'
            active_subscription.end_date = func.current_timestamp()
            db.session.commit()
            
            flash('Subscription cancelled successfully', 'success')
        else:
            flash('No active subscription found', 'warning')
        
        return redirect(url_for('subscription.dashboard'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to cancel subscription: {str(e)}', 'danger')
        return redirect(url_for('subscription.dashboard'))