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
    image_url   = db.Column(db.String(500))                    # Cloudinary URL
    image_id    = db.Column(db.String(200))                    # Cloudinary public_id
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

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
