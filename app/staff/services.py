from app.admin.services import (
    get_all_products_admin,
    get_dashboard_stats,
    get_feedback_reviews,
    get_orders_management_data,
    update_order_status,
)
from app.models.admin import AdminTodo
from app.models.user import User
from app.utils.store_helper import get_current_user_store, get_user_store
from sqlalchemy.orm import joinedload
from sqlalchemy import case, or_, and_


def get_staff_todos(user_id, status='all', priority='all'):
    """Lấy các công việc được gán cho nhân viên từ many-to-many relationship (assigned_staff).
    
    Hỗ trợ cả cách giao việc cũ (assigned_user_id) và cách mới (assigned_staff many-to-many).
    Lọc theo store của nhân viên (company-wide tasks có store_id=NULL).
    """
    # Get staff's assigned store
    user_store = get_current_user_store()
    store_id = user_store.id if user_store else None
    
    # Điều kiện 1: Từ assigned_user_id (cách cũ)
    old_way_condition = AdminTodo.assigned_user_id == user_id
    
    # Điều kiện 2: Từ many-to-many relationship (cách mới)
    # Phải join trước rồi mới filter
    query = AdminTodo.query.outerjoin(AdminTodo.assigned_staff).filter(
        or_(
            old_way_condition,
            User.id == user_id
        )
    )
    
    # Filter by store: either assigned to this store or company-wide (store_id=NULL)
    if store_id:
        query = query.filter(or_(
            AdminTodo.store_id == store_id,
            AdminTodo.store_id == None  # Company-wide tasks
        ))
    else:
        # If user not assigned to store, only show company-wide tasks
        query = query.filter(AdminTodo.store_id == None)
    
    normalized_status = (status or 'all').strip().lower()
    normalized_priority = (priority or 'all').strip().lower()

    if normalized_status == 'open':
        query = query.filter(AdminTodo.is_done == False)
    elif normalized_status == 'done':
        query = query.filter(AdminTodo.is_done == True)
    else:
        normalized_status = 'all'

    if normalized_priority in {'high', 'medium', 'low'}:
        query = query.filter(AdminTodo.priority == normalized_priority)
    else:
        normalized_priority = 'all'

    # Sắp xếp theo trạng thái, ưu tiên, và ngày tạo - dùng distinct để tránh duplicate từ join
    priority_order = case(
        (AdminTodo.priority == 'high', 3),
        (AdminTodo.priority == 'medium', 2),
        (AdminTodo.priority == 'low', 1),
        else_=0,
    )
    
    todos = query.distinct(AdminTodo.id).order_by(
        AdminTodo.is_done.asc(),
        priority_order.desc(),
        AdminTodo.created_at.desc(),
    ).all()
    
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


def get_staff_dashboard_data(user_id=None):
    """Get dashboard data for staff, filtered by their assigned store.
    
    Args:
        user_id: The staff user ID (defaults to current_user.id)
    """
    # Get the user's assigned store
    user_store = get_user_store(user_id) if user_id else get_current_user_store()
    store_id = user_store.id if user_store else None
    
    stats = get_dashboard_stats(store_id=store_id)
    products = get_all_products_admin(store_id=store_id)
    low_stock_products = sorted(
        [product for product in products if int(getattr(product, 'display_in_stock', product.in_stock or 0)) < 10],
        key=lambda item: int(getattr(item, 'display_in_stock', item.in_stock or 0)),
    )
    expiring_products = [
        product
        for product in products
        if getattr(product, 'expiry_alert', None) in {'soon', 'expired'}
    ]
    recent_orders = get_orders_management_data(filter_mode='latest', store_id=store_id)['items']
    pending_feedback = get_feedback_reviews(reply_status='unreplied', store_id=store_id)
    pending_reviews = pending_feedback['items'][:5]

    return {
        'stats': stats,
        'low_stock_products': low_stock_products,
        'expiring_products': expiring_products,
        'recent_orders': recent_orders,
        'pending_reviews': pending_reviews,
        'pending_review_count': pending_feedback.get('total', 0),
        'store_id': store_id,
    }


def get_staff_orders_data(filter_mode='latest', date_value=None, user_id=None):
    """Get orders for staff, filtered by their assigned store.
    
    Args:
        filter_mode: Filter mode (latest, today, week, month)
        date_value: Date value for filtering
        user_id: The staff user ID (defaults to current_user.id)
    """
    user_store = get_user_store(user_id) if user_id else get_current_user_store()
    store_id = user_store.id if user_store else None
    return get_orders_management_data(filter_mode=filter_mode, date_value=date_value, store_id=store_id)


def get_staff_inventory_products(user_id=None):
    """Get inventory products for staff, filtered by their assigned store.
    
    Args:
        user_id: The staff user ID (defaults to current_user.id)
    """
    user_store = get_user_store(user_id) if user_id else get_current_user_store()
    store_id = user_store.id if user_store else None
    return get_all_products_admin(store_id=store_id)


def get_staff_feedback_data(search='', rating='all', reply_status='all', user_id=None):
    """Get feedback for staff, filtered by their assigned store.
    
    Args:
        search: Search query
        rating: Filter by rating
        reply_status: Filter by reply status
        user_id: The staff user ID (defaults to current_user.id)
    """
    user_store = get_user_store(user_id) if user_id else get_current_user_store()
    store_id = user_store.id if user_store else None
    return get_feedback_reviews(search=search, rating=rating, reply_status=reply_status, store_id=store_id)


def update_staff_order_status(order_id, status, user_id=None):
    """Update order status with store access check.
    
    Args:
        order_id: The order ID
        status: New status
        user_id: The staff user ID (for access check)
    """
    # Check store access if user_id is provided
    if user_id:
        from app.models.order import Order
        order = Order.query.get(order_id)
        if not order:
            return False, 'Đơn hàng không tồn tại'
        
        user_store = get_user_store(user_id)
        if user_store and order.store_id != user_store.id:
            return False, 'Bạn không có quyền cập nhật đơn hàng này'
    
    return update_order_status(order_id, status)
