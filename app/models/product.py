from app.extensions import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = 'categories'

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    products = db.relationship('Product', backref='category_ref', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Integer, nullable=False)        # VND
    category    = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    rating      = db.Column(db.Float, default=0.0)
    in_stock    = db.Column(db.Integer, default=0)
    cost_price  = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    unit        = db.Column(db.String(30), default='cai')
    image_url   = db.Column(db.String(500))                    # Cloudinary URL
    image_id    = db.Column(db.String(200))                    # Cloudinary public_id
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    batches = db.relationship(
        'ProductBatch',
        backref='product',
        lazy=True,
        cascade='all, delete-orphan'
    )
    reviews = db.relationship(
        'ProductReview',
        backref='product',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id':       self.id,
            'name':     self.name,
            'price':    self.price,
            'category': self.category,
            'rating':   self.rating,
            'inStock':  self.in_stock,
            'image':    self.image_url,
        }

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductBatch(db.Model):
    __tablename__ = 'product_batches'

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False, default=0)
    cost_price = db.Column(db.Integer, nullable=False, default=0)
    expiry_date = db.Column(db.Date, nullable=False)
    imported_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductBatch product={self.product_id} qty={self.quantity} exp={self.expiry_date}>'


class ProductReview(db.Model):
    __tablename__ = 'product_reviews'

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text)
    admin_reply = db.Column(db.Text)
    admin_reply_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('order_id', 'user_id', 'product_id', name='uq_review_order_user_product'),
    )

    def __repr__(self):
        return f'<ProductReview product={self.product_id} user={self.user_id} rating={self.rating}>'
