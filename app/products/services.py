from sqlalchemy import func
from flask_login import current_user
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.product import Product, Category, ProductReview, ProductBatch
from app.models.user import User
from app.utils.store_helper import get_current_user_store, filter_query_by_user_store


# Constants
LOCAL_TIMEZONE = timezone(timedelta(hours=7))
EXPIRY_WARNING_HOURS = 8
DISCOUNT_PERCENT = 30


def _attach_review_stats(products):
    """Attach review statistics to products.
    
    For each product, aggregates reviews from all products with the same name
    across all stores (to show combined ratings regardless of store).
    """
    if not products:
        return products

    # Build map of product_name -> list of product_ids across all stores
    product_ids_by_name = {}
    for product in products:
        product_name = product.name
        if product_name not in product_ids_by_name:
            # Find all products with this name across all stores
            all_same_name = Product.query.filter_by(name=product_name).all()
            product_ids_by_name[product_name] = [p.id for p in all_same_name]
    
    # Get review stats for each unique name
    review_rows = (
        db.session.query(
            ProductReview.product_id,
            func.count(ProductReview.id).label('review_count'),
            func.avg(ProductReview.rating).label('avg_rating'),
        )
        .filter(ProductReview.product_id.in_(
            [pid for pids in product_ids_by_name.values() for pid in pids]
        ))
        .group_by(ProductReview.product_id)
        .all()
    )

    # Aggregate stats by product name
    stats_by_name = {}
    for row in review_rows:
        product_obj = Product.query.get(row.product_id)
        if product_obj:
            product_name = product_obj.name
            if product_name not in stats_by_name:
                stats_by_name[product_name] = {'count': 0, 'total_rating': 0}
            stats_by_name[product_name]['count'] += int(row.review_count or 0)
            stats_by_name[product_name]['total_rating'] += float(row.avg_rating or 0) * int(row.review_count or 0)
    
    # Apply stats to products
    for product in products:
        stats = stats_by_name.get(product.name)
        if stats and stats['count'] > 0:
            product.reviewCount = stats['count']
            product.rating = round(stats['total_rating'] / stats['count'], 1)
        else:
            product.reviewCount = 0
            product.rating = 0

    return products


def get_all_products(category=None, exclude_id=None, limit=None, store_id=None):
    """Get all products for front-end display.
    
    Shows only store_id=1 products (canonical version) to avoid duplicates.
    Ratings are aggregated from ALL stores.
    
    Args:
        category: Filter by product category
        exclude_id: Exclude a specific product ID
        limit: Maximum number of products to return
        store_id: Ignored for front-end (always uses store_id=1)
    """
    query = Product.query.filter_by(store_id=1)  # Always use store 1 for public display
    
    if category:
        query = query.filter_by(category=category)
    if exclude_id:
        query = query.filter(Product.id != exclude_id)
    if limit:
        query = query.limit(limit)
    products = query.all()
    return _attach_review_stats(products)


def get_products_paginated(category=None, page=1, per_page=16, store_id=None):
    """Get paginated products for front-end display.
    
    Shows only store_id=1 products (canonical version) to avoid duplicates.
    
    Args:
        category: Filter by category
        page: Page number
        per_page: Items per page
        store_id: Ignored (always uses store_id=1)
    """
    query = Product.query.filter_by(store_id=1)
    
    if category:
        query = query.filter_by(category=category)

    query = query.order_by(Product.created_at.desc(), Product.id.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_product_by_id(product_id, store_id=None):
    """Get product by ID with aggregated reviews from all stores.
    
    Shows the product from store_id=1, but aggregates reviews from all products
    with the same name across all stores.
    
    Args:
        product_id: The product ID
        store_id: Ignored (always returns store_id=1 version)
    """
    product = Product.query.get(product_id)
    if not product:
        return None
    
    # Always show the store_id=1 version (canonical)
    # Find the product with same name in store 1
    canonical_product = Product.query.filter_by(name=product.name, store_id=1).first()
    if not canonical_product:
        canonical_product = product
    
    _attach_review_stats([canonical_product])
    return canonical_product


def get_product_reviews(product_id, limit=100):
    """Get reviews for a product, aggregated from all stores.
    
    Finds the product by ID, gets all products with the same name across all stores,
    and returns reviews for all of them (to show combined reviews regardless of store).
    """
    # Get the base product to find the name
    base_product = Product.query.get(product_id)
    if not base_product:
        return []
    
    # Find all products with the same name across all stores
    same_name_products = Product.query.filter_by(name=base_product.name).all()
    same_product_ids = [p.id for p in same_name_products]
    
    # Get reviews for all these products
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
        .filter(ProductReview.product_id.in_(same_product_ids))
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
    """Search products by name or description.
    
    Only searches in store_id=1 products (canonical version).
    Results are sorted by relevance.
    """
    # Get all store_id=1 products
    all_products = Product.query.filter_by(store_id=1).order_by(Product.name).all()

    keyword = (keyword or '').strip()
    if not keyword:
        return _attach_review_stats(all_products)

    pattern = f'%{keyword}%'
    matched_products = Product.query.filter_by(store_id=1).filter(
        Product.name.ilike(pattern) | Product.description.ilike(pattern)
    ).order_by(Product.name).all()

    matched_ids = {product.id for product in matched_products}
    other_products = [product for product in all_products if product.id not in matched_ids]

    return _attach_review_stats(matched_products + other_products)


def get_discounted_products():
    """Get products expiring soon with 30% discount.
    
    Returns products from store_id=1 that have batches expiring within 8 hours.
    Adds discount price and label info to each product.
    """
    # Get all store 1 products with their batches
    products = Product.query.filter_by(store_id=1).options(
        db.joinedload(Product.batches)
    ).all()
    
    now_local = datetime.now(LOCAL_TIMEZONE)
    now_vn_naive = now_local.replace(tzinfo=None)
    
    discounted_products = []
    
    for product in products:
        # Check if product has batches expiring soon
        active_batches = [
            batch for batch in (product.batches or [])
            if int(batch.quantity or 0) > 0 and batch.expiry_date
        ]
        
        if not active_batches:
            continue
        
        # Calculate hours_left for all batches and find the one expiring soonest
        batch_hours = []
        for batch in active_batches:
            if batch.imported_at:
                imported_at_naive = batch.imported_at.replace(tzinfo=None) if batch.imported_at.tzinfo else batch.imported_at
                batch_expiry_datetime = imported_at_naive + timedelta(hours=24)
                hours_left = (batch_expiry_datetime - now_vn_naive).total_seconds() / 3600
            else:
                expiry_datetime = datetime.combine(batch.expiry_date, datetime.max.time())
                hours_left = (expiry_datetime - now_vn_naive).total_seconds() / 3600
            batch_hours.append((batch, hours_left))
        
        # Find batch expiring soonest (minimum hours_left)
        nearest_batch, hours_left = min(batch_hours, key=lambda x: x[1])
        
        # Only include if expiring soon (within EXPIRY_WARNING_HOURS)
        if hours_left > EXPIRY_WARNING_HOURS:
            continue
        
        # Add discount info
        product.is_discounted = True
        product.discount_percent = DISCOUNT_PERCENT
        product.original_price = product.price
        product.discount_price = int(product.price * (100 - DISCOUNT_PERCENT) / 100)
        product.expiry_hours_left = int(hours_left)
        
        discounted_products.append(product)
    
    # Attach review stats
    return _attach_review_stats(discounted_products)


def get_categories():
    return Category.query.order_by(Category.name).all()
