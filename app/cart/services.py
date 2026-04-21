from flask import session
from app.models.product import Product, ProductBatch
from datetime import datetime, timedelta, timezone

# Constants
LOCAL_TIMEZONE = timezone(timedelta(hours=7))
EXPIRY_WARNING_HOURS = 8
DISCOUNT_PERCENT = 30


def _get_product_price_with_discount(product):
    """Calculate product price with discount if expiring soon.
    
    Returns the discounted price (30% off) if the product has batches
    expiring within 8 hours, otherwise returns regular price.
    """
    # Check if product has batches expiring soon
    active_batches = [
        batch for batch in product.batches
        if int(batch.quantity or 0) > 0 and batch.expiry_date
    ]
    
    if not active_batches:
        return product.price
    
    nearest_batch = min(active_batches, key=lambda item: item.expiry_date)
    
    # Calculate hours until expiry
    now_local = datetime.now(LOCAL_TIMEZONE)
    now_vn_naive = now_local.replace(tzinfo=None)
    
    if nearest_batch.imported_at:
        imported_at_naive = nearest_batch.imported_at.replace(tzinfo=None) if nearest_batch.imported_at.tzinfo else nearest_batch.imported_at
        batch_expiry_datetime = imported_at_naive + timedelta(hours=24)
        hours_left = (batch_expiry_datetime - now_vn_naive).total_seconds() / 3600
    else:
        expiry_datetime = datetime.combine(nearest_batch.expiry_date, datetime.max.time())
        hours_left = (expiry_datetime - now_vn_naive).total_seconds() / 3600
    
    # Apply discount if expiring soon
    if hours_left <= EXPIRY_WARNING_HOURS:
        return int(product.price * (100 - DISCOUNT_PERCENT) / 100)
    
    return product.price


def get_cart():
    return session.get('cart', [])


def get_cart_count():
    return sum(item.get('quantity', 1) for item in get_cart())


def get_cart_totals(cart):
    subtotal     = sum(item['price'] * item['quantity'] for item in cart)
    shipping_fee = 0 if (subtotal >= 50000 or subtotal == 0) else 20000
    total        = subtotal + shipping_fee
    cart_count   = sum(item['quantity'] for item in cart)
    return subtotal, shipping_fee, total, cart_count


def add_to_cart(product_id, quantity=1):
    product = Product.query.get(product_id)
    if not product:
        return None

    # Get price with discount applied if expiring soon
    price = _get_product_price_with_discount(product)

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({
            'id':       product.id,
            'name':     product.name,
            'price':    price,
            'image':    product.image_url,
            'quantity': quantity,
        })

    session['cart'] = cart
    session.modified = True
    return cart


def update_cart(product_id, delta):
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] = max(1, item['quantity'] + delta)
            break
    session['cart'] = cart
    session.modified = True
    return cart


def remove_from_cart(product_id):
    cart = [i for i in session.get('cart', []) if i['id'] != product_id]
    session['cart'] = cart
    session.modified = True
    return cart


def clear_cart():
    session['cart'] = []
    session.modified = True
