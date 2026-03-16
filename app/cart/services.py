from flask import session
from app.models.product import Product


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

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({
            'id':       product.id,
            'name':     product.name,
            'price':    product.price,
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
