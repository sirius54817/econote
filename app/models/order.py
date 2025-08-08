from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float(precision=2), nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float(precision=2), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    
    @classmethod
    def create_order(cls, user, cart_items):
        """
        Create an order from cart items
        
        :param user: User making the order
        :param cart_items: List of cart items
        :return: New Order instance
        """
        total_price = sum(item.price * item.quantity for item in cart_items)
        
        order = cls(
            user_id=user.id,
            total_price=total_price,
            status='Pending'
        )
        
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
            order_items.append(order_item)
        
        order.items = order_items
        return order
    
    def __repr__(self):
        return f'<Order {self.id} - User {self.user_id}>'