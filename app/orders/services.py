from app.extensions import db
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.payment import Promotion
from app.models.product import Product, ProductBatch
from datetime import datetime
from sqlalchemy import func


DEFAULT_VOUCHERS = [
    {
        'code': 'WELCOME10',
        'type': 'percent',
        'value': 10,
        'min_order': 100000,
    },
    {
        'code': 'SAVE30K',
        'type': 'fixed',
        'value': 30000,
        'min_order': 150000,
    },
    {
        'code': 'FREEDAY15',
        'type': 'percent',
        'value': 15,
        'min_order': 200000,
    },
]


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


def ensure_default_promotions():
    existing = {p.code for p in Promotion.query.with_entities(Promotion.code).all()}
    to_create = []

    for item in DEFAULT_VOUCHERS:
        if item['code'] in existing:
            continue
        to_create.append(
            Promotion(
                code=item['code'],
                type=item['type'],
                value=item['value'],
                min_order=item['min_order'],
                is_active=True,
            )
        )

    if to_create:
        db.session.add_all(to_create)
        db.session.commit()


def _promotion_discount(subtotal, promotion):
    if not promotion:
        return 0

    if promotion.type == 'percent':
        discount = int(subtotal * (promotion.value / 100))
    else:
        discount = int(promotion.value)

    return max(0, min(discount, subtotal))


def get_available_promotions(user_id):
    ensure_default_promotions()
    now = datetime.utcnow()

    used_promotion_ids = {
        row[0]
        for row in db.session.query(Order.promotion_id)
        .filter(
            Order.user_id == user_id,
            Order.promotion_id.isnot(None),
            Order.status != 'cancelled',
        )
        .all()
    }

    promotions = (
        Promotion.query
        .filter(Promotion.is_active.is_(True))
        .order_by(Promotion.created_at.desc())
        .all()
    )

    available = []
    for promotion in promotions:
        if promotion.id in used_promotion_ids:
            continue
        if promotion.start_date and promotion.start_date > now:
            continue
        if promotion.end_date and promotion.end_date < now:
            continue
        available.append(promotion)

    return available


def validate_promotion_for_user(user_id, voucher_code, subtotal):
    code = (voucher_code or '').strip().upper()
    if not code:
        return None, 0, None

    promotion = Promotion.query.filter(
        db.func.upper(Promotion.code) == code,
        Promotion.is_active.is_(True),
    ).first()
    if not promotion:
        return None, 0, 'Mã giảm giá không hợp lệ hoặc đã hết hạn.'

    available_ids = {p.id for p in get_available_promotions(user_id)}
    if promotion.id not in available_ids:
        return None, 0, 'Mã giảm giá này đã được sử dụng hoặc không khả dụng.'

    if subtotal < (promotion.min_order or 0):
        return None, 0, f'Đơn hàng cần tối thiểu {promotion.min_order:,}đ để dùng mã này.'.replace(',', '.')

    discount = _promotion_discount(subtotal, promotion)
    return promotion, discount, None


def validate_cart_stock(cart_items):
    """Validate that all cart items still have enough stock.

    Returns:
        (is_valid: bool, error_message: str | None)
    """
    required_by_product = {}
    for item in cart_items:
        product_id = item.get('id')
        quantity = int(item.get('quantity') or 0)
        if not product_id or quantity <= 0:
            continue
        required_by_product[product_id] = required_by_product.get(product_id, 0) + quantity

    if not required_by_product:
        return False, 'Giỏ hàng không có sản phẩm hợp lệ để thanh toán.'

    products = Product.query.filter(Product.id.in_(required_by_product.keys())).all()
    product_map = {p.id: p for p in products}

    for product_id, required_qty in required_by_product.items():
        product = product_map.get(product_id)
        if not product:
            return False, 'Có sản phẩm không còn tồn tại trong hệ thống.'

        if int(product.in_stock or 0) < required_qty:
            return False, (
                f'Sản phẩm "{product.name}" chỉ còn {int(product.in_stock or 0)} '
                f'nhưng bạn đang chọn {required_qty}. Vui lòng cập nhật giỏ hàng trước khi thanh toán.'
            )

    return True, None


def create_order(user_id, cart_items, checkout_data=None, promotion=None, discount_amount=0):
    if checkout_data is None:
        checkout_data = {}
    elif isinstance(checkout_data, str):
        checkout_data = {'note': checkout_data}
    try:
        subtotal = sum(i['price'] * i['quantity'] for i in cart_items)
        discount_amount = max(0, min(int(discount_amount or 0), subtotal))
        discounted_subtotal = subtotal - discount_amount
        shipping_fee = 0 if discounted_subtotal >= 50000 else 20000
        grand_total = discounted_subtotal + shipping_fee
        payment_method = _normalize_payment_method(checkout_data.get('payment'))
        order_note = _build_order_note(checkout_data)

        order = Order(
            user_id      = user_id,
            promotion_id = promotion.id if promotion else None,
            total        = discounted_subtotal,
            shipping_fee = shipping_fee,
            payment_method = payment_method,
            note         = order_note,
            status       = 'pending',
        )
        db.session.add(order)
        db.session.flush()  # lấy order.id trước khi commit

        # Deduct inventory by batch (FEFO: earliest expiry first).
        _consume_inventory_batches(cart_items)

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
    except Exception:
        db.session.rollback()
        raise


def _consume_inventory_batches(cart_items):
    required_by_product = {}
    for item in cart_items:
        product_id = item.get('id')
        quantity = int(item.get('quantity') or 0)
        if not product_id or quantity <= 0:
            continue
        required_by_product[product_id] = required_by_product.get(product_id, 0) + quantity

    if not required_by_product:
        return

    product_ids = list(required_by_product.keys())
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    for product_id, required_qty in required_by_product.items():
        product = product_map.get(product_id)
        if not product:
            raise ValueError('Có sản phẩm không còn tồn tại trong hệ thống.')
        if int(product.in_stock or 0) < required_qty:
            raise ValueError(f'Sản phẩm "{product.name}" không đủ tồn kho.')

        remaining_to_consume = required_qty
        batches = (
            ProductBatch.query
            .filter(
                ProductBatch.product_id == product_id,
                ProductBatch.quantity > 0,
            )
            .order_by(ProductBatch.expiry_date.asc(), ProductBatch.imported_at.asc(), ProductBatch.id.asc())
            .all()
        )

        if not batches:
            raise ValueError(f'Sản phẩm "{product.name}" chưa có dữ liệu lô hàng.')

        for batch in batches:
            if remaining_to_consume <= 0:
                break

            deduct_qty = min(batch.quantity, remaining_to_consume)
            batch.quantity -= deduct_qty
            remaining_to_consume -= deduct_qty

        if remaining_to_consume > 0:
            raise ValueError(f'Sản phẩm "{product.name}" không đủ số lượng theo các lô còn lại.')

        product.in_stock = int(product.in_stock or 0) - required_qty
        _sync_product_cost_price_from_batches(product_id)


def _sync_product_cost_price_from_batches(product_id):
    product = Product.query.get(product_id)
    if not product:
        return

    qty_sum, cost_sum = (
        db.session.query(
            func.coalesce(func.sum(ProductBatch.quantity), 0),
            func.coalesce(func.sum(ProductBatch.quantity * ProductBatch.cost_price), 0),
        )
        .filter(
            ProductBatch.product_id == product_id,
            ProductBatch.quantity > 0,
        )
        .first()
    )

    total_qty = int(qty_sum or 0)
    total_cost = int(cost_sum or 0)

    if total_qty <= 0:
        product.cost_price = 0
        return

    product.cost_price = int(round(total_cost / total_qty))


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
