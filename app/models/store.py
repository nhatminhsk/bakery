from app.extensions import db
from datetime import datetime


class Store(db.Model):
    __tablename__ = 'stores'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False)
    code            = db.Column(db.String(20), unique=True, nullable=False)
    address         = db.Column(db.String(255))
    phone           = db.Column(db.String(30))
    email           = db.Column(db.String(120))
    
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff_assignment = db.relationship('StoreStaff', backref='store', lazy=True, cascade='all, delete-orphan', uselist=False)
    products        = db.relationship('Product', backref='store', lazy=True)
    orders          = db.relationship('Order', backref='store', lazy=True)
    settings        = db.relationship('StoreSetting', backref='store', lazy=True, cascade='all, delete-orphan', uselist=False)

    def __repr__(self):
        return f'<Store {self.name}>'


class StoreStaff(db.Model):
    """1 staff = 1 store"""
    __tablename__ = 'store_staff'

    id              = db.Column(db.Integer, primary_key=True)
    store_id        = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False, unique=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    assigned_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_active       = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='store_assignment')

    __table_args__ = (
        db.UniqueConstraint('store_id', name='uq_store_one_staff'),
    )

    def __repr__(self):
        return f'<StoreStaff store={self.store_id} user={self.user_id}>'


class StoreSetting(db.Model):
    __tablename__ = 'store_settings'

    id                  = db.Column(db.Integer, primary_key=True)
    store_id            = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    
    delivery_base_fee   = db.Column(db.Integer, default=20000)
    free_shipping_min   = db.Column(db.Integer, default=50000)
    delivery_eta        = db.Column(db.String(50), default='24 giờ')
    same_day_delivery   = db.Column(db.Boolean, default=False)
    
    payment_cod         = db.Column(db.Boolean, default=True)
    payment_bank        = db.Column(db.Boolean, default=False)
    payment_card        = db.Column(db.Boolean, default=False)
    payment_ewallet     = db.Column(db.Boolean, default=False)
    
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StoreSetting store={self.store_id}>'
