from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.orders.services import (
    create_order,
    get_order_by_id,
    get_user_orders,
    get_available_promotions,
    validate_promotion_for_user,
    validate_cart_stock,
)
from app.cart.services import get_cart, clear_cart, get_cart_totals
from app.utils.review_store import has_review_for_order, create_order_review

orders_bp = Blueprint('orders', __name__)
OUT_OF_STOCK_MESSAGE = 'hết hàng, chúng tôi sẽ cập nhật trong thời gian sớm nhất'


@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = get_cart()
    if not cart_items:
        flash('Giỏ hàng trống!', 'warning')
        return redirect(url_for('cart.cart'))

    # Validate stock immediately when user clicks "Tiến hành thanh toán".
    is_stock_valid, stock_error = validate_cart_stock(cart_items)
    if not is_stock_valid:
        flash(OUT_OF_STOCK_MESSAGE, 'error')
        return redirect(url_for('cart.cart'))

    subtotal, shipping_fee, grand_total, cart_count = get_cart_totals(cart_items)
    available_promotions = get_available_promotions(current_user.id)
    selected_voucher_code = ''
    discount_amount = 0
    discounted_subtotal = subtotal
    checkout_data = {}

    if request.method == 'POST':
        # Re-check stock right before placing order to avoid race conditions.
        is_stock_valid, stock_error = validate_cart_stock(cart_items)
        if not is_stock_valid:
            flash(OUT_OF_STOCK_MESSAGE, 'error')
            return redirect(url_for('cart.cart'))

        selected_voucher_code = request.form.get('voucher_code', '').strip().upper()
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
            'voucher_code': selected_voucher_code,
        }

        promotion, discount_amount, promo_error = validate_promotion_for_user(
            current_user.id,
            selected_voucher_code,
            subtotal,
        )
        if promo_error:
            flash(promo_error, 'error')
            discounted_subtotal = subtotal
            shipping_fee = 0 if discounted_subtotal >= 50000 else 20000
            grand_total = discounted_subtotal + shipping_fee
            return render_template(
                'checkout.html',
                cart_items=cart_items,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                discount_amount=discount_amount,
                discounted_subtotal=discounted_subtotal,
                grand_total=grand_total,
                promotions=available_promotions,
                selected_voucher_code=selected_voucher_code,
                checkout_data=checkout_data,
            )

        discounted_subtotal = subtotal - discount_amount
        shipping_fee = 0 if discounted_subtotal >= 50000 else 20000
        grand_total = discounted_subtotal + shipping_fee

        try:
            order = create_order(
                current_user.id,
                cart_items,
                checkout_data,
                promotion=promotion,
                discount_amount=discount_amount,
            )
        except ValueError as exc:
            flash(OUT_OF_STOCK_MESSAGE, 'error')
            return render_template(
                'checkout.html',
                cart_items=cart_items,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                discount_amount=discount_amount,
                discounted_subtotal=discounted_subtotal,
                grand_total=grand_total,
                promotions=available_promotions,
                selected_voucher_code=selected_voucher_code,
                checkout_data=checkout_data,
            )

        clear_cart()
        flash(f'Đặt hàng thành công! Mã đơn: #{order.id}', 'success')
        return redirect(url_for('orders.order_detail', order_id=order.id))

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        discounted_subtotal=discounted_subtotal,
        grand_total=grand_total,
        promotions=available_promotions,
        selected_voucher_code=selected_voucher_code,
        checkout_data=checkout_data,
    )


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
    has_review = has_review_for_order(current_user.id, order.id)
    return render_template('order_detail.html', order=order, has_review=has_review)


@orders_bp.route('/orders/<int:order_id>/review', methods=['GET', 'POST'])
@login_required
def review_order(order_id):
    order = get_order_by_id(order_id)
    if not order or order.user_id != current_user.id:
        flash('Không tìm thấy đơn hàng.', 'error')
        return redirect(url_for('orders.order_list'))

    if order.status != 'delivered':
        flash('Chỉ có thể đánh giá khi đơn hàng đã giao thành công.', 'warning')
        return redirect(url_for('orders.order_detail', order_id=order.id))

    if has_review_for_order(current_user.id, order.id):
        flash('Bạn đã đánh giá đơn hàng này rồi.', 'info')
        return redirect(url_for('orders.order_detail', order_id=order.id))

    if request.method == 'POST':
        rating_raw = request.form.get('rating', '5').strip()
        comment = request.form.get('comment', '').strip()

        try:
            rating = int(rating_raw)
        except ValueError:
            rating = 0

        if rating < 1 or rating > 5:
            flash('Số sao phải nằm trong khoảng từ 1 đến 5.', 'error')
            return render_template('review_order.html', order=order, rating=rating_raw, comment=comment)

        success, error = create_order_review(order, current_user, rating, comment)
        if success:
            flash('Cảm ơn bạn đã gửi đánh giá!', 'success')
            return redirect(url_for('orders.order_detail', order_id=order.id))

        flash(error or 'Không thể lưu đánh giá, vui lòng thử lại.', 'error')

    return render_template('review_order.html', order=order)
