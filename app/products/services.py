from sqlalchemy import func

from app.extensions import db
from app.models.product import Product, Category, ProductReview
from app.models.user import User


def _attach_review_stats(products):
    if not products:
        return products

    product_ids = [product.id for product in products if getattr(product, 'id', None)]
    if not product_ids:
        return products

    review_rows = (
        db.session.query(
            ProductReview.product_id,
            func.count(ProductReview.id).label('review_count'),
            func.avg(ProductReview.rating).label('avg_rating'),
        )
        .filter(ProductReview.product_id.in_(product_ids))
        .group_by(ProductReview.product_id)
        .all()
    )

    stats_map = {
        row.product_id: {
            'count': int(row.review_count or 0),
            'avg': float(row.avg_rating or 0),
        }
        for row in review_rows
    }

    for product in products:
        stats = stats_map.get(product.id)
        if stats:
            product.reviewCount = stats['count']
            product.rating = round(stats['avg'], 1)
        else:
            product.reviewCount = 0
            product.rating = 0

    return products


def get_all_products(category=None, exclude_id=None, limit=None):
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if exclude_id:
        query = query.filter(Product.id != exclude_id)
    if limit:
        query = query.limit(limit)
    products = query.all()
    return _attach_review_stats(products)


def get_products_paginated(category=None, page=1, per_page=16):
    query = Product.query
    if category:
        query = query.filter_by(category=category)

    query = query.order_by(Product.created_at.desc(), Product.id.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_product_by_id(product_id):
    product = Product.query.get(product_id)
    if not product:
        return None
    _attach_review_stats([product])
    return product


def get_product_reviews(product_id, limit=100):
    rows = (
        db.session.query(
            ProductReview.id,
            ProductReview.rating,
            ProductReview.comment,
            ProductReview.created_at,
            ProductReview.admin_reply,
            ProductReview.admin_reply_at,
            User.username,
        )
        .join(User, User.id == ProductReview.user_id)
        .filter(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc(), ProductReview.id.desc())
        .limit(limit)
        .all()
    )

    output = []
    for row in rows:
        output.append(
            {
                'id': int(row.id),
                'username': row.username,
                'rating': int(row.rating or 0),
                'comment': (row.comment or '').strip(),
                'created_at': row.created_at.strftime('%d/%m/%Y %H:%M') if row.created_at else '',
                'admin_reply': (row.admin_reply or '').strip(),
                'admin_reply_at': row.admin_reply_at.strftime('%d/%m/%Y %H:%M') if row.admin_reply_at else '',
            }
        )

    return output


def search_products(keyword):
    all_products = Product.query.order_by(Product.name).all()

    keyword = (keyword or '').strip()
    if not keyword:
        return _attach_review_stats(all_products)

    pattern = f'%{keyword}%'
    matched_products = Product.query.filter(
        Product.name.ilike(pattern) | Product.description.ilike(pattern)
    ).order_by(Product.name).all()

    matched_ids = {product.id for product in matched_products}
    other_products = [product for product in all_products if product.id not in matched_ids]

    return _attach_review_stats(matched_products + other_products)


def get_categories():
    return Category.query.order_by(Category.name).all()
