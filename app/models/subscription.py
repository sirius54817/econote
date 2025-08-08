from app import db
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float(precision=2), nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    
    # Relationships
    subscriptions = relationship('Subscription', back_populates='plan_details')

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    status = db.Column(db.String(20), default='Active')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='subscriptions')
    plan_details = relationship('SubscriptionPlan', back_populates='subscriptions')
    
    @classmethod
    def create_subscription(cls, user, plan):
        """
        Create a new subscription
        
        :param user: User subscribing
        :param plan: SubscriptionPlan
        :return: New Subscription instance
        """
        # Cancel any existing active subscriptions
        active_subs = cls.query.filter_by(
            user_id=user.id, 
            status='Active'
        ).all()
        
        for sub in active_subs:
            sub.status = 'Cancelled'
        
        # Create new subscription
        end_date = datetime.utcnow() + timedelta(days=plan.duration_months * 30)
        
        return cls(
            user_id=user.id,
            plan_id=plan.id,
            status='Active',
            end_date=end_date
        )
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return (
            self.status == 'Active' and 
            (self.end_date is None or self.end_date > datetime.utcnow())
        )
    
    def __repr__(self):
        return f'<Subscription {self.plan_details.name} for User {self.user_id}>'