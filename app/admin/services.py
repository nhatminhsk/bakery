from pathlib import Path
from uuid import uuid4

from app.extensions import db
from app.models.product import Product, Category
from app.models.order import Order
from app.models.user import User
from app.utils.cloudinary_helper import delete_image
from sqlalchemy import func
from werkzeug.utils import secure_filename


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_PRODUCTS_DIR = PROJECT_ROOT / 'static' / 'images' / 'products'
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


def _save_image_to_static(image_file):
    if not image_file or not image_file.filename:
        return None, None

    safe_filename = secure_filename(image_file.filename)
    if not safe_filename:
        return None, 'Tên file ảnh không hợp lệ.'

    ext = Path(safe_filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None, 'Ảnh chỉ hỗ trợ định dạng: jpg, jpeg, png, webp, gif.'

    STATIC_PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f'{uuid4().hex}{ext}'
    destination = STATIC_PRODUCTS_DIR / stored_filename
    image_file.save(destination)
    return f'/static/images/products/{stored_filename}', None


def _delete_local_image(image_url):
    if not image_url or not image_url.startswith('/static/images/'):
        return

    image_path = PROJECT_ROOT.joinpath(*image_url.lstrip('/').split('/'))
    try:
        if image_path.exists() and image_path.is_file():
            image_path.unlink()
    except Exception:
        pass


def get_dashboard_stats():
    return {
        'total_products': Product.query.count(),
        'total_orders':   Order.query.count(),
        'total_users':    User.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'revenue':        db.session.query(func.sum(Order.total + Order.shipping_fee))\
                            .filter(Order.status == 'delivered').scalar() or 0,
    }


def get_all_orders():
    return Order.query.order_by(Order.created_at.desc()).all()


def get_all_products_admin():
    return Product.query.order_by(Product.created_at.desc()).all()


def create_product(data, image_file=None):
    try:
        name = (data.get('name') or '').strip()
        if not name:
            return None, 'Tên sản phẩm không được để trống.'

        category = (data.get('category') or '').strip()
        if not category:
            return None, 'Danh mục không được để trống.'

        try:
            price = int(data.get('price', 0))
        except (TypeError, ValueError):
            return None, 'Giá sản phẩm phải là số nguyên hợp lệ.'
        if price < 0:
            return None, 'Giá sản phẩm không được âm.'

        try:
            in_stock = int(data.get('in_stock', 0))
        except (TypeError, ValueError):
            return None, 'Số lượng tồn kho phải là số nguyên hợp lệ.'
        if in_stock < 0:
            return None, 'Số lượng tồn kho không được âm.'

        image_url, image_error = _save_image_to_static(image_file)
        if image_error:
            return None, image_error

        product = Product(
            name        = name,
            description = (data.get('description') or '').strip() or None,
            price       = price,
            category    = category,
            in_stock    = in_stock,
            image_url   = image_url,
            image_id    = None,
        )
        db.session.add(product)
        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def update_product(product_id, data, image_file=None):
    product = Product.query.get(product_id)
    if not product:
        return None, 'Sản phẩm không tồn tại.'

    try:
        if image_file and image_file.filename:
            new_image_url, image_error = _save_image_to_static(image_file)
            if image_error:
                return None, image_error

            if product.image_url:
                _delete_local_image(product.image_url)
            if product.image_id:
                delete_image(product.image_id)

            product.image_url = new_image_url
            product.image_id = None

        name = data.get('name')
        if name is not None:
            name = name.strip()
            if not name:
                return None, 'Tên sản phẩm không được để trống.'
            product.name = name

        product.description = data.get('description', product.description)

        price_value = data.get('price')
        if price_value is not None:
            try:
                parsed_price = int(price_value)
            except (TypeError, ValueError):
                return None, 'Giá sản phẩm phải là số nguyên hợp lệ.'

            if parsed_price < 0:
                return None, 'Giá sản phẩm không được âm.'
            product.price = parsed_price

        category = data.get('category')
        if category is not None:
            category = category.strip()
            if not category:
                return None, 'Danh mục không được để trống.'
            product.category = category

        in_stock_value = data.get('in_stock')
        if in_stock_value is not None:
            try:
                parsed_stock = int(in_stock_value)
            except (TypeError, ValueError):
                return None, 'Số lượng tồn kho phải là số nguyên hợp lệ.'

            if parsed_stock < 0:
                return None, 'Số lượng tồn kho không được âm.'
            product.in_stock = parsed_stock

        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return False, 'Sản phẩm không tồn tại hoặc đã bị xóa.'

    try:
        if product.image_url:
            _delete_local_image(product.image_url)
        if product.image_id:
            delete_image(product.image_id)
        db.session.delete(product)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def update_order_status(order_id, status):
    order = Order.query.get(order_id)
    if order:
        order.status = status
        db.session.commit()
