from datetime import datetime

from app.extensions import db


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    points = db.Column(db.Integer, default=0)
    rank = db.Column(db.String(20), default='bronze')  # bronze | silver | gold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PointHistory(db.Model):
    __tablename__ = 'point_history'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    points_change = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
