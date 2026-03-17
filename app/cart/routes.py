from flask import Blueprint, render_template, request, session
from flask_login import login_required

from app.cart.services import (
    get_cart, add_to_cart, update_cart, remove_from_cart, get_cart_totals
)

cart_bp = Blueprint('cart', __name__)
@login_required
@cart_bp.route('/cart')
def cart():
    cart_items = get_cart()
    subtotal, shipping_fee, total, cart_count = get_cart_totals(cart_items)
    return render_template('cart.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           shipping_fee=shipping_fee,
                           total=total)

@login_required
@cart_bp.route('/api/cart/add', methods=['POST'])
def add_to_cart_api():
    data       = request.get_json()
    product_id = int(data.get('product_id'))
    quantity   = int(data.get('quantity', 1))

    result = add_to_cart(product_id, quantity)
    if result:
        cart_count = sum(i['quantity'] for i in get_cart())
        return {'success': True, 'cart_count': cart_count}
    return {'success': False}, 400

@login_required
@cart_bp.route('/api/cart/update', methods=['POST'])
def update_cart_api():
    data       = request.get_json()
    product_id = int(data.get('product_id'))
    delta      = int(data.get('delta'))

    cart = update_cart(product_id, delta)
    subtotal, shipping, total, cart_count = get_cart_totals(cart)

    item = next((i for i in cart if i['id'] == product_id), None)
    return {
        'success':    True,
        'item_qty':   item['quantity'] if item else 0,
        'item_price': item['price'] if item else 0,
        'subtotal':   subtotal,
        'shipping':   shipping,
        'total':      total,
        'cart_count': cart_count,
    }

@login_required
@cart_bp.route('/api/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart_api(product_id):
    cart = remove_from_cart(product_id)
    subtotal, shipping, total, cart_count = get_cart_totals(cart)
    return {
        'success':    True,
        'subtotal':   subtotal,
        'shipping':   shipping,
        'total':      total,
        'cart_count': cart_count,
    }
