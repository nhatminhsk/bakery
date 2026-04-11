from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models.product import Product, ProductReview
from app.models.user import User


def _iso_or_none(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _recalculate_product_ratings(product_ids=None):
    query = (
        db.session.query(
            ProductReview.product_id,
            func.count(ProductReview.id).label('review_count'),
            func.avg(ProductReview.rating).label('avg_rating'),
        )
        .group_by(ProductReview.product_id)
    )

    if product_ids:
        query = query.filter(ProductReview.product_id.in_(product_ids))

    aggregates = query.all()
    aggregated_map = {
        row.product_id: round(float(row.avg_rating or 0), 1)
        for row in aggregates
    }

    target_products = Product.query
    if product_ids:
        target_products = target_products.filter(Product.id.in_(product_ids))

    for product in target_products.all():
        product.rating = aggregated_map.get(product.id, 0)

    db.session.commit()


def has_review_for_order(user_id, order_id):
    return (
        ProductReview.query
        .filter_by(user_id=user_id, order_id=order_id)
        .first()
        is not None
    )


def list_reviews(search='', rating_filter='all'):
    keyword = (search or '').strip().lower()
    rf = (rating_filter or 'all').strip().lower()

    query = (
        db.session.query(
            ProductReview,
            User.username,
            Product.name.label('product_name'),
        )
        .join(User, User.id == ProductReview.user_id)
        .join(Product, Product.id == ProductReview.product_id)
    )

    if rf.isdigit():
        query = query.filter(ProductReview.rating == int(rf))

    if keyword:
        pattern = f'%{keyword}%'
        query = query.filter(
            User.username.ilike(pattern)
            | Product.name.ilike(pattern)
            | ProductReview.comment.ilike(pattern)
        )

    rows = query.order_by(ProductReview.created_at.desc()).all()
    output = []

    for review, username, product_name in rows:
        output.append(
            {
                'id': review.id,
                'order_id': review.order_id,
                'user_id': review.user_id,
                'username': username,
                'product_id': review.product_id,
                'product_name': product_name,
                'rating': review.rating,
                'comment': review.comment or '',
                'created_at': _iso_or_none(review.created_at),
                'admin_reply': review.admin_reply,
                'admin_reply_at': _iso_or_none(review.admin_reply_at),
            }
        )

    return output


def create_order_review(order, user, rating, comment):
    if has_review_for_order(user.id, order.id):
        return False, 'Bạn đã đánh giá đơn hàng này rồi.'

    seen_product_ids = set()
    now = datetime.utcnow()
    comment_text = (comment or '').strip()

    for item in order.items:
        if not item.product_id or item.product_id in seen_product_ids:
            continue

        seen_product_ids.add(item.product_id)
        review = ProductReview(
            order_id=order.id,
            user_id=user.id,
            product_id=item.product_id,
            rating=int(rating),
            comment=comment_text,
            created_at=now,
            updated_at=now,
        )
        db.session.add(review)

    if not seen_product_ids:
        db.session.rollback()
        return False, 'Không có sản phẩm hợp lệ để đánh giá.'

    try:
        db.session.commit()
        _recalculate_product_ratings(product_ids=list(seen_product_ids))
    except Exception:
        db.session.rollback()
        return False, 'Không thể lưu đánh giá vào cơ sở dữ liệu.'

    return True, None


def get_review_by_id(review_id):
    review = ProductReview.query.get(review_id)
    if not review:
        return None

    user = User.query.get(review.user_id)
    product = Product.query.get(review.product_id)

    return {
        'id': review.id,
        'order_id': review.order_id,
        'user_id': review.user_id,
        'username': user.username if user else '',
        'product_id': review.product_id,
        'product_name': product.name if product else '',
        'rating': review.rating,
        'comment': review.comment or '',
        'created_at': _iso_or_none(review.created_at),
        'admin_reply': review.admin_reply,
        'admin_reply_at': _iso_or_none(review.admin_reply_at),
    }


def add_admin_reply(review_id, reply_text):
    reply_text = (reply_text or '').strip()
    if not reply_text:
        return False, 'Nội dung phản hồi không được để trống.'

    review = ProductReview.query.get(review_id)
    if not review:
        return False, 'Không tìm thấy đánh giá.'

    review.admin_reply = reply_text
    review.admin_reply_at = datetime.utcnow()
    db.session.commit()
    return True, None
