from app.extensions import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status      = db.Column(db.String(30), default='pending')
    # pending | confirmed | processing | delivered | cancelled
    total       = db.Column(db.Integer, default=0)
    shipping_fee= db.Column(db.Integer, default=0)
    note        = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def grand_total(self):
        return self.total + self.shipping_fee

    def __repr__(self):
        return f'<Order #{self.id} - {self.status}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    name       = db.Column(db.String(120))   # snapshot tên lúc mua
    price      = db.Column(db.Integer)       # snapshot giá lúc mua
    quantity   = db.Column(db.Integer, default=1)
    image_url  = db.Column(db.String(500))

    product = db.relationship('Product')

    def subtotal(self):
        return self.price * self.quantity
