from app.extensions import db
from app.models.product import Product, Category
from app.models.order import Order
from app.models.user import User
from app.utils.cloudinary_helper import upload_image, delete_image
from sqlalchemy import func


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
        image_url, image_id = None, None
        if image_file and image_file.filename:
            image_url, image_id = upload_image(image_file, folder='bakery/products')

        product = Product(
            name        = data.get('name'),
            description = data.get('description'),
            price       = int(data.get('price', 0)),
            category    = data.get('category'),
            in_stock    = int(data.get('in_stock', 0)),
            image_url   = image_url,
            image_id    = image_id,
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
            if product.image_id:
                delete_image(product.image_id)
            product.image_url, product.image_id = upload_image(
                image_file, folder='bakery/products'
            )

        product.name        = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price       = int(data.get('price', product.price))
        product.category    = data.get('category', product.category)
        product.in_stock    = int(data.get('in_stock', product.in_stock))
        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        if product.image_id:
            delete_image(product.image_id)
        db.session.delete(product)
        db.session.commit()


def update_order_status(order_id, status):
    order = Order.query.get(order_id)
    if order:
        order.status = status
        db.session.commit()
