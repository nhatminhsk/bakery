from app.extensions import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    role       = db.Column(db.String(20), default='customer')  # customer | staff | admin
    is_active  = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    phone      = db.Column(db.String(30))
    points     = db.Column(db.Integer, default=0)
    rank       = db.Column(db.String(20), default='bronze')  # bronze | silver | gold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='customer', lazy=True)

    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == 'admin'

    def is_staff(self):
        return self.role == 'staff'

    def has_role(self, *roles):
        return self.role in set(roles)

    def can_access_staff(self):
        return self.role in {'staff', 'admin'}

    def __repr__(self):
        return f'<User {self.username}>'
