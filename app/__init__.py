import os
from flask import Flask
from app.extensions import db, login_manager, bcrypt, migrate
from config import config_map

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app(config_name='development'):
    app = Flask(__name__,
                static_folder=os.path.join(BASE_DIR, 'static'),
                template_folder=os.path.join(BASE_DIR, 'Templates'))

    app.config.from_object(config_map[config_name])

    # Khởi tạo extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Nạp toàn bộ model để SQLAlchemy metadata có đủ bảng cho migrate/create_all.
    from app import models as _models  # noqa: F401

    # Cloudinary
    from app.utils.cloudinary_helper import init_cloudinary
    init_cloudinary(app)

    # Đăng ký blueprints
    from app.auth.routes import auth_bp
    from app.products.routes import products_bp
    from app.cart.routes import cart_bp
    from app.orders.routes import orders_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Inject cart_count vào mọi template
    from app.cart.services import get_cart_count
    @app.context_processor
    def inject_cart_count():
        return dict(cart_count=get_cart_count())

    return app
