from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.orders.services import create_order, get_user_orders, get_order_by_id
from app.cart.services import get_cart, clear_cart, get_cart_totals

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = get_cart()
    if not cart_items:
        flash('Giỏ hàng trống!', 'warning')
        return redirect(url_for('cart.cart'))

    subtotal, shipping_fee, grand_total, cart_count = get_cart_totals(cart_items)

    if request.method == 'POST':
        checkout_data = {
            'first_name': request.form.get('firstName', '').strip(),
            'last_name': request.form.get('lastName', '').strip(),
            'email': request.form.get('email', '').strip() or getattr(current_user, 'email', ''),
            'phone': request.form.get('phone', '').strip() or getattr(current_user, 'phone', ''),
            'address': request.form.get('address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'district': request.form.get('district', '').strip(),
            'zipcode': request.form.get('zipcode', '').strip(),
            'payment': request.form.get('payment', 'cod').strip(),
            'note': request.form.get('note', '').strip(),
        }
        order = create_order(current_user.id, cart_items, checkout_data)
        clear_cart()
        flash(f'Đặt hàng thành công! Mã đơn: #{order.id}', 'success')
        return redirect(url_for('orders.order_detail', order_id=order.id))

    return render_template('checkout.html', cart_items=cart_items, total=subtotal)


@orders_bp.route('/orders')
@login_required
def order_list():
    orders = get_user_orders(current_user.id)
    return render_template('orders.html', orders=orders)


@orders_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = get_order_by_id(order_id)
    if not order or order.user_id != current_user.id:
        flash('Không tìm thấy đơn hàng.', 'error')
        return redirect(url_for('orders.order_list'))
    return render_template('order_detail.html', order=order)
