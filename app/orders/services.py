from app.extensions import db
from app.models.order import Order, OrderItem
from app.models.payment import Payment


def _normalize_payment_method(raw_method):
    method_map = {
        'cod': 'cash',
        'cash': 'cash',
        'bank': 'transfer',
        'transfer': 'transfer',
        'wallet': 'ewallet',
        'ewallet': 'ewallet',
        'card': 'card',
    }
    return method_map.get((raw_method or '').strip().lower(), 'cash')


def _build_order_note(checkout_data):
    first_name = (checkout_data.get('first_name') or '').strip()
    last_name = (checkout_data.get('last_name') or '').strip()
    full_name = f"{last_name} {first_name}".strip()

    email = (checkout_data.get('email') or '').strip()
    phone = (checkout_data.get('phone') or '').strip()
    address = (checkout_data.get('address') or '').strip()
    district = (checkout_data.get('district') or '').strip()
    city = (checkout_data.get('city') or '').strip()
    zipcode = (checkout_data.get('zipcode') or '').strip()
    customer_note = (checkout_data.get('note') or '').strip()

    address_parts = [part for part in [address, district, city, zipcode] if part]
    full_address = ', '.join(address_parts)

    lines = []
    if full_name or phone or email:
        lines.append(f"Recipient: {full_name} | {phone} | {email}")
    if full_address:
        lines.append(f"Address: {full_address}")
    if customer_note:
        lines.append(f"Customer note: {customer_note}")

    return '\n'.join(lines)


def create_order(user_id, cart_items, checkout_data=None):
    if checkout_data is None:
        checkout_data = {}
    elif isinstance(checkout_data, str):
        checkout_data = {'note': checkout_data}

    subtotal     = sum(i['price'] * i['quantity'] for i in cart_items)
    shipping_fee = 0 if subtotal >= 50000 else 20000
    grand_total  = subtotal + shipping_fee
    payment_method = _normalize_payment_method(checkout_data.get('payment'))
    order_note = _build_order_note(checkout_data)

    order = Order(
        user_id      = user_id,
        total        = subtotal,
        shipping_fee = shipping_fee,
        payment_method = payment_method,
        note         = order_note,
        status       = 'pending',
    )
    db.session.add(order)
    db.session.flush()  # lấy order.id trước khi commit

    for item in cart_items:
        order_item = OrderItem(
            order_id   = order.id,
            product_id = item['id'],
            name       = item['name'],
            price      = item['price'],
            quantity   = item['quantity'],
            image_url  = item.get('image'),
        )
        db.session.add(order_item)

    payment = Payment(
        order_id = order.id,
        method = payment_method,
        amount = grand_total,
        status = 'pending',
    )
    db.session.add(payment)

    db.session.commit()
    return order


def get_user_orders(user_id):
    return Order.query.filter_by(user_id=user_id)\
                      .order_by(Order.created_at.desc()).all()


def get_order_by_id(order_id):
    return Order.query.get(order_id)


def update_order_status(order_id, status):
    order = Order.query.get(order_id)
    if order:
        order.status = status
        db.session.commit()
    return order
