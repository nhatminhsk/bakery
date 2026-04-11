from app.admin.services import (
    get_all_products_admin,
    get_dashboard_stats,
    get_feedback_reviews,
    get_orders_management_data,
    update_order_status,
)
from app.models.admin import AdminTodo


def get_staff_todos(user_id, status='all', priority='all'):
    query = AdminTodo.query.filter(AdminTodo.assigned_user_id == user_id)

    normalized_status = (status or 'all').strip().lower()
    normalized_priority = (priority or 'all').strip().lower()

    if normalized_status == 'open':
        query = query.filter_by(is_done=False)
    elif normalized_status == 'done':
        query = query.filter_by(is_done=True)
    else:
        normalized_status = 'all'

    if normalized_priority in {'high', 'medium', 'low'}:
        query = query.filter_by(priority=normalized_priority)
    else:
        normalized_priority = 'all'

    todos = query.order_by(AdminTodo.is_done.asc(), AdminTodo.created_at.desc()).all()
    todos_dicts = [todo.to_dict() for todo in todos]
    done_count = sum(1 for todo in todos_dicts if todo.get('is_done'))

    return {
        'items': todos_dicts,
        'status_filter': normalized_status,
        'priority_filter': normalized_priority,
        'total': len(todos_dicts),
        'done': done_count,
        'open': len(todos_dicts) - done_count,
    }


def get_staff_dashboard_data():
    stats = get_dashboard_stats()
    products = get_all_products_admin()
    low_stock_products = sorted(
        [product for product in products if int(getattr(product, 'display_in_stock', product.in_stock or 0)) < 10],
        key=lambda item: int(getattr(item, 'display_in_stock', item.in_stock or 0)),
    )
    expiring_products = [
        product
        for product in products
        if getattr(product, 'expiry_alert', None) in {'soon', 'expired'}
    ]
    recent_orders = get_orders_management_data(filter_mode='latest')['items']
    pending_feedback = get_feedback_reviews(reply_status='unreplied')
    pending_reviews = pending_feedback['items'][:5]

    return {
        'stats': stats,
        'low_stock_products': low_stock_products,
        'expiring_products': expiring_products,
        'recent_orders': recent_orders,
        'pending_reviews': pending_reviews,
        'pending_review_count': pending_feedback.get('total', 0),
    }


def get_staff_orders_data(filter_mode='latest', date_value=None):
    return get_orders_management_data(filter_mode=filter_mode, date_value=date_value)


def get_staff_inventory_products():
    return get_all_products_admin()


def get_staff_feedback_data(search='', rating='all', reply_status='all'):
    return get_feedback_reviews(search=search, rating=rating, reply_status=reply_status)


def update_staff_order_status(order_id, status):
    return update_order_status(order_id, status)
