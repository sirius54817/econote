from app import db
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    image = db.Column(db.String(200), nullable=True)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    order_items = relationship('OrderItem', back_populates='product')
    
    @hybrid_property
    def is_in_stock(self):
        """Check if product is available"""
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        """Reduce product stock by the given quantity if available"""
        if quantity > self.stock:
            raise ValueError("Insufficient stock")
        self.stock -= quantity

    def update(self, title=None, description=None, price=None, image=None, stock=None, is_active=None):
        """Update product details with provided values"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if price is not None:
            self.price = price
        if image is not None:
            self.image = image
        if stock is not None:
            self.stock = stock
        if is_active is not None:
            self.is_active = is_active
    
    def __repr__(self):
        return f'<Product {self.title}>'
