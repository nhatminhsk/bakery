import json
from datetime import datetime
from pathlib import Path

from app.extensions import db
from app.models.product import Product


REVIEW_STORAGE_PATH = Path('data/product_reviews.json')


def _load_reviews():
    if not REVIEW_STORAGE_PATH.exists():
        return []

    try:
        data = json.loads(REVIEW_STORAGE_PATH.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_reviews(reviews):
    REVIEW_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_STORAGE_PATH.write_text(
        json.dumps(reviews, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def has_review_for_order(user_id, order_id):
    reviews = _load_reviews()
    return any(r.get('user_id') == user_id and r.get('order_id') == order_id for r in reviews)


def list_reviews(search='', rating_filter='all'):
    reviews = _load_reviews()
    keyword = (search or '').strip().lower()
    rf = (rating_filter or 'all').strip().lower()

    if rf.isdigit():
        rating_value = int(rf)
        reviews = [r for r in reviews if int(r.get('rating', 0)) == rating_value]

    if keyword:
        reviews = [
            r for r in reviews
            if keyword in (r.get('username') or '').lower()
            or keyword in (r.get('product_name') or '').lower()
            or keyword in (r.get('comment') or '').lower()
        ]

    reviews.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return reviews


def _recalculate_product_ratings(reviews):
    grouped = {}
    for review in reviews:
        product_id = review.get('product_id')
        rating = review.get('rating')
        if not product_id or not isinstance(rating, (int, float)):
            continue
        grouped.setdefault(product_id, []).append(float(rating))

    for product_id, ratings in grouped.items():
        product = Product.query.get(product_id)
        if product and ratings:
            product.rating = round(sum(ratings) / len(ratings), 1)

    db.session.commit()


def create_order_review(order, user, rating, comment):
    if has_review_for_order(user.id, order.id):
        return False, 'Bạn đã đánh giá đơn hàng này rồi.'

    reviews = _load_reviews()
    next_id = max((r.get('id', 0) for r in reviews), default=0) + 1
    created_at = datetime.utcnow().isoformat()

    seen_product_ids = set()
    for item in order.items:
        if not item.product_id or item.product_id in seen_product_ids:
            continue

        seen_product_ids.add(item.product_id)
        reviews.append(
            {
                'id': next_id,
                'order_id': order.id,
                'user_id': user.id,
                'username': user.username,
                'product_id': item.product_id,
                'product_name': item.name,
                'rating': int(rating),
                'comment': (comment or '').strip(),
                'created_at': created_at,
                'admin_reply': None,
                'admin_reply_at': None,
            }
        )
        next_id += 1

    if not seen_product_ids:
        return False, 'Không có sản phẩm hợp lệ để đánh giá.'

    _save_reviews(reviews)
    _recalculate_product_ratings(reviews)
    return True, None


def get_review_by_id(review_id):
    """Get a single review by ID."""
    reviews = _load_reviews()
    return next((r for r in reviews if r.get('id') == review_id), None)


def add_admin_reply(review_id, reply_text):
    """Add or update admin reply to a review."""
    reply_text = (reply_text or '').strip()
    if not reply_text:
        return False, 'Nội dung phản hồi không được để trống.'

    reviews = _load_reviews()
    review = next((r for r in reviews if r.get('id') == review_id), None)

    if not review:
        return False, 'Không tìm thấy đánh giá.'

    review['admin_reply'] = reply_text
    review['admin_reply_at'] = datetime.utcnow().isoformat()
    _save_reviews(reviews)
    return True, None
