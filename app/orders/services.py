from app.extensions import db
from app.models.order import Order, OrderItem


def create_order(user_id, cart_items, note=''):
    subtotal     = sum(i['price'] * i['quantity'] for i in cart_items)
    shipping_fee = 0 if subtotal >= 50000 else 20000

    order = Order(
        user_id      = user_id,
        total        = subtotal,
        shipping_fee = shipping_fee,
        note         = note,
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
