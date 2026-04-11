from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta, date, timezone
import json

from app.extensions import db
from app.models.product import Product, Category, ProductBatch
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.user import User
from app.models.admin import AdminTodo
from app.utils.cloudinary_helper import delete_image, upload_image
from app.utils.review_store import list_reviews
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_PRODUCTS_DIR = PROJECT_ROOT / 'static' / 'images' / 'products'
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
VALID_ORDER_STATUSES = {'pending', 'confirmed', 'processing', 'delivered', 'cancelled'}
ADMIN_SETTINGS_PATH = PROJECT_ROOT / 'data' / 'admin_settings.json'

DEFAULT_ADMIN_SETTINGS = {
    'store_name': 'BubbleBakery',
    'contact_email': 'contact@bubblebakery.vn',
    'phone': '+84 (0) 123 456 789',
    'address': '123 Đường Bánh Tươi, Quận 1, TP.HCM',
    'delivery_base_fee': 20000,
    'free_shipping_min': 50000,
    'delivery_eta': '24 giờ',
    'same_day_delivery': True,
    'payment_cod': True,
    'payment_credit_card': True,
    'payment_bank_transfer': True,
    'payment_ewallet': False,
}

LOCAL_TIMEZONE = timezone(timedelta(hours=7))
LOW_STOCK_THRESHOLD = 10
EXPIRY_WARNING_DAYS = 3


def _local_day_bounds_to_utc(target_date):
    """Convert local-day boundaries (UTC+7) to naive UTC datetimes for DB filters."""
    local_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=LOCAL_TIMEZONE)
    local_end = local_start + timedelta(days=1)
    utc_start = local_start.astimezone(timezone.utc).replace(tzinfo=None)
    utc_end = local_end.astimezone(timezone.utc).replace(tzinfo=None)
    return utc_start, utc_end


def _local_week_bounds_to_utc(target_date):
    """Week starts on Monday in local time."""
    week_start_date = target_date - timedelta(days=target_date.weekday())
    local_start = datetime(week_start_date.year, week_start_date.month, week_start_date.day, tzinfo=LOCAL_TIMEZONE)
    local_end = local_start + timedelta(days=7)
    utc_start = local_start.astimezone(timezone.utc).replace(tzinfo=None)
    utc_end = local_end.astimezone(timezone.utc).replace(tzinfo=None)
    return utc_start, utc_end


def _local_month_bounds_to_utc(target_date):
    local_start = datetime(target_date.year, target_date.month, 1, tzinfo=LOCAL_TIMEZONE)
    if target_date.month == 12:
        next_month_start = datetime(target_date.year + 1, 1, 1, tzinfo=LOCAL_TIMEZONE)
    else:
        next_month_start = datetime(target_date.year, target_date.month + 1, 1, tzinfo=LOCAL_TIMEZONE)

    utc_start = local_start.astimezone(timezone.utc).replace(tzinfo=None)
    utc_end = next_month_start.astimezone(timezone.utc).replace(tzinfo=None)
    return utc_start, utc_end


def _write_admin_settings(settings_data):
    ADMIN_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ADMIN_SETTINGS_PATH.write_text(
        json.dumps(settings_data, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def get_admin_settings():
    if not ADMIN_SETTINGS_PATH.exists():
        _write_admin_settings(DEFAULT_ADMIN_SETTINGS)
        return dict(DEFAULT_ADMIN_SETTINGS)

    try:
        data = json.loads(ADMIN_SETTINGS_PATH.read_text(encoding='utf-8'))
    except Exception:
        data = {}

    merged = dict(DEFAULT_ADMIN_SETTINGS)
    if isinstance(data, dict):
        merged.update(data)

    # Ensure persisted data always has complete key set.
    _write_admin_settings(merged)
    return merged


def update_admin_settings(form_data):
    current = get_admin_settings()

    store_name = (form_data.get('store_name') or '').strip()
    contact_email = (form_data.get('contact_email') or '').strip()
    phone = (form_data.get('phone') or '').strip()
    address = (form_data.get('address') or '').strip()
    delivery_eta = (form_data.get('delivery_eta') or '').strip()

    if not store_name:
        return False, 'Tên cửa hàng không được để trống.'
    if not contact_email:
        return False, 'Email liên hệ không được để trống.'

    try:
        delivery_base_fee = int(form_data.get('delivery_base_fee', current['delivery_base_fee']))
        free_shipping_min = int(form_data.get('free_shipping_min', current['free_shipping_min']))
    except (TypeError, ValueError):
        return False, 'Phí giao hàng và ngưỡng miễn phí phải là số hợp lệ.'

    if delivery_base_fee < 0 or free_shipping_min < 0:
        return False, 'Phí giao hàng và ngưỡng miễn phí không được âm.'

    updated = {
        'store_name': store_name,
        'contact_email': contact_email,
        'phone': phone,
        'address': address,
        'delivery_base_fee': delivery_base_fee,
        'free_shipping_min': free_shipping_min,
        'delivery_eta': delivery_eta or current['delivery_eta'],
        'same_day_delivery': form_data.get('same_day_delivery') == 'on',
        'payment_cod': form_data.get('payment_cod') == 'on',
        'payment_credit_card': form_data.get('payment_credit_card') == 'on',
        'payment_bank_transfer': form_data.get('payment_bank_transfer') == 'on',
        'payment_ewallet': form_data.get('payment_ewallet') == 'on',
    }

    _write_admin_settings(updated)
    return True, None


def _save_image_to_static(image_file):
    if not image_file or not image_file.filename:
        return None, None

    safe_filename = secure_filename(image_file.filename)
    if not safe_filename:
        return None, 'Tên file ảnh không hợp lệ.'

    ext = Path(safe_filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None, 'Ảnh chỉ hỗ trợ định dạng: jpg, jpeg, png, webp, gif.'

    STATIC_PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f'{uuid4().hex}{ext}'
    destination = STATIC_PRODUCTS_DIR / stored_filename
    image_file.save(destination)
    return f'/static/images/products/{stored_filename}', None


def _delete_local_image(image_url):
    if not image_url or not image_url.startswith('/static/images/'):
        return

    image_path = PROJECT_ROOT.joinpath(*image_url.lstrip('/').split('/'))
    try:
        if image_path.exists() and image_path.is_file():
            image_path.unlink()
    except Exception:
        pass


def _upload_image_to_cloudinary(image_file):
    """Validate extension then upload to Cloudinary.

    Returns:
        (image_url, image_id, error_message)
        On success: (str, str, None)
        On failure: (None, None, str)
    """
    if not image_file or not image_file.filename:
        return None, None, None

    safe_filename = secure_filename(image_file.filename)
    if not safe_filename:
        return None, None, 'Tên file ảnh không hợp lệ.'

    ext = Path(safe_filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None, None, 'Ảnh chỉ hỗ trợ định dạng: jpg, jpeg, png, webp, gif.'

    try:
        image_url, image_id = upload_image(image_file)
    except Exception as e:
        return None, None, f'Tải ảnh lên Cloudinary thất bại: {e}'

    if not image_url:
        return None, None, 'Cloudinary không trả về URL ảnh hợp lệ.'

    return image_url, image_id, None


def get_dashboard_stats():
    weekly_series = get_revenue_by_week(limit_weeks=8)
    monthly_series = get_revenue_by_month(limit_months=12)
    weekly_periods = [item['period'] for item in weekly_series]
    monthly_periods = [item['period'] for item in monthly_series]

    weekly_top_products = get_top_products_by_period('%Y-W%W', weekly_periods, top_n=5)
    monthly_top_products = get_top_products_by_period('%Y-%m', monthly_periods, top_n=5)

    current_week_key = datetime.utcnow().strftime('%Y-W%W')
    current_month_key = datetime.utcnow().strftime('%Y-%m')

    this_week_revenue = next((item['revenue'] for item in weekly_series if item['period'] == current_week_key), 0)
    this_month_revenue = next((item['revenue'] for item in monthly_series if item['period'] == current_month_key), 0)

    return {
        'total_products': Product.query.count(),
        'total_orders':   Order.query.count(),
        'total_users':    User.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'revenue':        db.session.query(func.sum(Order.total + Order.shipping_fee))\
                            .filter(Order.status == 'delivered', Order.paid_at.isnot(None)).scalar() or 0,
        'weekly_revenue': this_week_revenue,
        'monthly_revenue': this_month_revenue,
        'weekly_revenue_series': weekly_series,
        'monthly_revenue_series': monthly_series,
        'weekly_top_products': weekly_top_products,
        'monthly_top_products': monthly_top_products,
    }


def _aggregate_revenue_by_period(period_expr):
    rows = (
        db.session.query(
            period_expr.label('period'),
            func.sum(Order.total + Order.shipping_fee).label('revenue'),
            func.count(Order.id).label('order_count'),
        )
        .filter(Order.status == 'delivered', Order.paid_at.isnot(None))
        .group_by(period_expr)
        .order_by(period_expr)
        .all()
    )

    return [
        {
            'period': row.period,
            'revenue': int(row.revenue or 0),
            'order_count': int(row.order_count or 0),
        }
        for row in rows
        if row.period
    ]


def get_revenue_by_week(limit_weeks=8):
    period_expr = func.strftime('%Y-W%W', Order.paid_at)
    series = _aggregate_revenue_by_period(period_expr)
    return series[-limit_weeks:] if limit_weeks else series


def get_revenue_by_month(limit_months=12):
    period_expr = func.strftime('%Y-%m', Order.paid_at)
    series = _aggregate_revenue_by_period(period_expr)
    return series[-limit_months:] if limit_months else series


def get_top_products_by_period(period_pattern, target_periods, top_n=5):
    if not target_periods:
        return []

    period_expr = func.strftime(period_pattern, Order.paid_at)
    rows = (
        db.session.query(
            period_expr.label('period'),
            OrderItem.product_id.label('product_id'),
            OrderItem.name.label('product_name'),
            func.sum(OrderItem.quantity).label('sold_qty'),
            func.sum(OrderItem.price * OrderItem.quantity).label('revenue'),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.status == 'delivered',
            Order.paid_at.isnot(None),
            OrderItem.quantity.isnot(None),
            OrderItem.quantity > 0,
            period_expr.in_(target_periods),
        )
        .group_by(period_expr, OrderItem.product_id, OrderItem.name)
        .all()
    )

    period_map = {period: [] for period in target_periods}
    for row in rows:
        period_map.setdefault(row.period, []).append(
            {
                'product_id': row.product_id,
                'product_name': row.product_name or 'Không rõ tên sản phẩm',
                'sold_qty': int(row.sold_qty or 0),
                'revenue': int(row.revenue or 0),
            }
        )

    result = []
    for period in target_periods:
        ranked = sorted(
            period_map.get(period, []),
            key=lambda item: (item['sold_qty'], item['revenue']),
            reverse=True,
        )[:top_n]

        result.append(
            {
                'period': period,
                'items': ranked,
            }
        )

    return result


def get_all_orders():
    return Order.query.order_by(Order.created_at.desc()).all()


def get_orders_management_data(filter_mode='latest', date_value=None):
    mode = (filter_mode or 'latest').strip().lower()
    query = Order.query
    local_today = datetime.now(LOCAL_TIMEZONE).date()
    selected_date = None
    period_note = ''

    if mode == 'all':
        label = 'Tất cả đơn hàng'
        period_note = 'Phạm vi: toàn thời gian'
    elif mode == 'latest':
        start, end = _local_day_bounds_to_utc(local_today)
        query = query.filter(Order.created_at >= start, Order.created_at < end)
        label = 'Đơn hàng trong ngày'
        period_note = f'Phạm vi: ngày {local_today.strftime("%d/%m/%Y")}'
    elif mode == 'yesterday':
        target_date = local_today - timedelta(days=1)
        start, end = _local_day_bounds_to_utc(target_date)
        query = query.filter(Order.created_at >= start, Order.created_at < end)
        label = 'Đơn hàng hôm qua'
        period_note = f'Phạm vi: ngày {target_date.strftime("%d/%m/%Y")}'
    elif mode == 'week':
        start, end = _local_week_bounds_to_utc(local_today)
        query = query.filter(Order.created_at >= start, Order.created_at < end)
        label = 'Đơn hàng tuần này'
        week_start = local_today - timedelta(days=local_today.weekday())
        period_note = f'Phạm vi: từ {week_start.strftime("%d/%m/%Y")} đến {local_today.strftime("%d/%m/%Y")}'
    elif mode == 'month':
        start, end = _local_month_bounds_to_utc(local_today)
        query = query.filter(Order.created_at >= start, Order.created_at < end)
        label = 'Đơn hàng tháng này'
        month_start = local_today.replace(day=1)
        period_note = f'Phạm vi: từ {month_start.strftime("%d/%m/%Y")} đến {local_today.strftime("%d/%m/%Y")}'
    elif mode == 'date':
        try:
            selected_date = datetime.strptime((date_value or '').strip(), '%Y-%m-%d').date()
        except ValueError:
            selected_date = None

        if selected_date:
            start, end = _local_day_bounds_to_utc(selected_date)
            query = query.filter(Order.created_at >= start, Order.created_at < end)
            label = f'Đơn hàng ngày {selected_date.strftime("%d/%m/%Y")}'
            period_note = f'Phạm vi: ngày {selected_date.strftime("%d/%m/%Y")}'
        else:
            mode = 'latest'
            start, end = _local_day_bounds_to_utc(local_today)
            query = query.filter(Order.created_at >= start, Order.created_at < end)
            label = 'Đơn hàng trong ngày'
            period_note = f'Phạm vi: ngày {local_today.strftime("%d/%m/%Y")}'
    else:
        mode = 'latest'
        start, end = _local_day_bounds_to_utc(local_today)
        query = query.filter(Order.created_at >= start, Order.created_at < end)
        label = 'Đơn hàng trong ngày'
        period_note = f'Phạm vi: ngày {local_today.strftime("%d/%m/%Y")}'

    query = query.order_by(Order.created_at.desc())

    orders = query.all()
    total_all_time = Order.query.count()
    return {
        'items': orders,
        'filter_mode': mode,
        'selected_date': selected_date.strftime('%Y-%m-%d') if selected_date else '',
        'label': label,
        'period_note': period_note,
        'count': len(orders),
        'total_all_time': total_all_time,
    }


def _resolve_overview_period(period):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    if period == 'all':
        start = None
        end = None
        label = 'Tất cả'
    elif period == 'yesterday':
        start = today_start - timedelta(days=1)
        end = today_start
        label = 'Hôm qua'
    elif period == 'week':
        start = today_start - timedelta(days=today_start.weekday())
        end = now
        label = 'Tuần này'
    else:
        start = today_start
        end = now
        period = 'today'
        label = 'Hôm nay'

    return period, label, start, end


def get_overview_orders(period='today', limit=100):
    period, period_label, start, end = _resolve_overview_period(period)
    query = Order.query.order_by(Order.created_at.desc())

    if start and end:
        query = query.filter(Order.created_at >= start, Order.created_at <= end)

    if limit:
        query = query.limit(limit)

    orders = query.all()
    completed_count = sum(1 for order in orders if order.status == 'delivered')
    revenue = sum((order.total or 0) + (order.shipping_fee or 0) for order in orders if order.status != 'cancelled')

    return {
        'selected_period': period,
        'period_label': period_label,
        'orders': orders,
        'order_count': len(orders),
        'completed_count': completed_count,
        'revenue': revenue,
    }


def get_all_products_admin():
    products = (
        Product.query
        .options(joinedload(Product.batches))
        .order_by(Product.created_at.desc())
        .all()
    )

    today_local = datetime.now(LOCAL_TIMEZONE).date()

    needs_stock_sync = False

    for product in products:
        available_batch_qty = sum(
            int(batch.quantity or 0)
            for batch in (product.batches or [])
            if int(batch.quantity or 0) > 0
        )

        # Keep product.in_stock synchronized with batch quantities to avoid drift.
        if int(product.in_stock or 0) != available_batch_qty:
            product.in_stock = available_batch_qty
            needs_stock_sync = True

        stock_qty = int(product.in_stock or 0)
        product.display_in_stock = stock_qty
        if stock_qty <= 0:
            product.stock_alert = 'out'
        elif stock_qty < LOW_STOCK_THRESHOLD:
            product.stock_alert = 'low'
        else:
            product.stock_alert = 'ok'

        active_batches = [
            batch for batch in (product.batches or [])
            if int(batch.quantity or 0) > 0 and batch.expiry_date
        ]

        if not active_batches:
            product.nearest_expiry_date = None
            product.expiry_days_left = None
            product.expiry_alert = 'missing'
            continue

        nearest_batch = min(active_batches, key=lambda item: item.expiry_date)
        nearest_expiry = nearest_batch.expiry_date
        days_left = (nearest_expiry - today_local).days

        product.nearest_expiry_date = nearest_expiry
        product.expiry_days_left = days_left
        if days_left < 0:
            product.expiry_alert = 'expired'
        elif days_left <= EXPIRY_WARNING_DAYS:
            product.expiry_alert = 'soon'
        else:
            product.expiry_alert = 'ok'

    if needs_stock_sync:
        db.session.commit()

    return products


def _todo_priority_weight(priority):
    mapping = {'high': 3, 'medium': 2, 'low': 1}
    return mapping.get(priority, 0)


def get_admin_todos(status='all', priority='all'):
    query = AdminTodo.query.options(joinedload(AdminTodo.assigned_user))

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

    # Database-level sorting: incomplete first, then by priority, then by creation date
    priority_order = case(
        (AdminTodo.priority == 'high', 3),
        (AdminTodo.priority == 'medium', 2),
        (AdminTodo.priority == 'low', 1),
        else_=0,
    )
    todos = query.order_by(
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


def get_assignable_staff_users():
    return (
        User.query
        .filter(User.role == 'staff')
        .order_by(User.username.asc())
        .all()
    )


def get_staff_candidate_users():
    return (
        User.query
        .filter(User.role != 'admin')
        .order_by(User.username.asc())
        .all()
    )


def add_users_to_staff(user_ids):
    raw_ids = user_ids or []
    normalized_ids = []

    for value in raw_ids:
        try:
            normalized_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    normalized_ids = sorted(set(normalized_ids))
    if not normalized_ids:
        return False, 0, 'Vui lòng chọn ít nhất 1 tài khoản để thêm vào nhân viên.'

    users = User.query.filter(User.id.in_(normalized_ids)).all()
    if not users:
        return False, 0, 'Không tìm thấy tài khoản hợp lệ.'

    updated_count = 0
    for user in users:
        if user.role == 'admin':
            continue
        if user.role != 'staff':
            user.role = 'staff'
            updated_count += 1

    db.session.commit()
    return True, updated_count, None


def get_staff_todos(user_id, status='all', priority='all'):
    query = AdminTodo.query.options(joinedload(AdminTodo.assigned_user)).filter(AdminTodo.assigned_user_id == user_id)

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

    # Database-level sorting: incomplete first, then by priority, then by creation date
    priority_order = case(
        (AdminTodo.priority == 'high', 3),
        (AdminTodo.priority == 'medium', 2),
        (AdminTodo.priority == 'low', 1),
        else_=0,
    )
    todos = query.order_by(
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


def create_admin_todo(title, priority='medium', assigned_user_id=None):
    title = (title or '').strip()
    if not title:
        return False, 'Nội dung công việc không được để trống.'

    priority = (priority or 'medium').strip().lower()
    if priority not in {'high', 'medium', 'low'}:
        priority = 'medium'

    assigned_user = None
    if assigned_user_id not in (None, ''):
        try:
            assigned_user_id = int(assigned_user_id)
        except (TypeError, ValueError):
            return False, 'Mã nhân viên không hợp lệ.'

        assigned_user = User.query.get(assigned_user_id)
        if not assigned_user or assigned_user.role != 'staff':
            return False, 'Chỉ có thể giao việc cho tài khoản nhân viên.'

    todo = AdminTodo(title=title, priority=priority, assigned_user_id=assigned_user.id if assigned_user else None, is_done=False)
    
    # Also add to many-to-many relationship for new assignment system
    if assigned_user:
        todo.assigned_staff.append(assigned_user)
    
    db.session.add(todo)
    db.session.commit()
    return True, None


def toggle_admin_todo(todo_id):
    todo = AdminTodo.query.get(todo_id)

    if not todo:
        return False, 'Không tìm thấy công việc.'

    todo.is_done = not todo.is_done
    todo.completed_at = datetime.utcnow() if todo.is_done else None
    db.session.commit()
    return True, None


def delete_admin_todo(todo_id):
    todo = AdminTodo.query.get(todo_id)

    if not todo:
        return False, 'Không tìm thấy công việc để xóa.'

    db.session.delete(todo)
    db.session.commit()
    return True, None


def assign_staff_to_todo(todo_id, staff_user_ids):
    """
    Assign multiple staff members to a todo.
    
    Args:
        todo_id: AdminTodo.id
        staff_user_ids: List of User.id to assign (replaces existing assignments)
    
    Returns:
        (success, count, error_message)
    """
    todo = AdminTodo.query.get(todo_id)
    if not todo:
        return False, 0, 'Không tìm thấy công việc.'
    
    raw_ids = staff_user_ids or []
    normalized_ids = []
    
    for value in raw_ids:
        try:
            normalized_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    
    normalized_ids = sorted(set(normalized_ids))
    
    # Get all staff users with these IDs
    staff_users = User.query.filter(
        User.id.in_(normalized_ids),
        User.role == 'staff'
    ).all()
    
    if not staff_users and normalized_ids:
        return False, 0, 'Không tìm thấy nhân viên hợp lệ để giao cho công việc.'
    
    # Clear existing assignments and set new ones
    todo.assigned_staff = staff_users
    db.session.commit()
    
    return True, len(staff_users), None


def add_staff_to_todo(todo_id, staff_user_ids):
    """
    Add additional staff members to a todo (keeps existing assignments).
    
    Args:
        todo_id: AdminTodo.id
        staff_user_ids: List of User.id to add
    
    Returns:
        (success, count_added, error_message)
    """
    todo = AdminTodo.query.get(todo_id)
    if not todo:
        return False, 0, 'Không tìm thấy công việc.'
    
    raw_ids = staff_user_ids or []
    normalized_ids = []
    
    for value in raw_ids:
        try:
            normalized_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    
    normalized_ids = sorted(set(normalized_ids))
    
    # Get existing staff IDs
    existing_ids = {user.id for user in (todo.assigned_staff or [])}
    
    # Get new staff to add
    staff_to_add = User.query.filter(
        User.id.in_(normalized_ids),
        User.role == 'staff',
        ~User.id.in_(existing_ids),  # Not already assigned
    ).all()
    
    if not staff_to_add:
        return True, 0, None  # No new staff to add is not an error
    
    # Add to existing assignments
    for user in staff_to_add:
        todo.assigned_staff.append(user)
    
    db.session.commit()
    return True, len(staff_to_add), None


def remove_staff_from_todo(todo_id, staff_user_id):
    """
    Remove a staff member from a todo.
    
    Args:
        todo_id: AdminTodo.id
        staff_user_id: User.id to remove
    
    Returns:
        (success, error_message)
    """
    todo = AdminTodo.query.get(todo_id)
    if not todo:
        return False, 'Không tìm thấy công việc.'
    
    try:
        staff_user_id = int(staff_user_id)
    except (TypeError, ValueError):
        return False, 'Mã nhân viên không hợp lệ.'
    
    staff_user = User.query.get(staff_user_id)
    if not staff_user or staff_user.role != 'staff':
        return False, 'Không tìm thấy nhân viên để xóa.'
    
    if staff_user in todo.assigned_staff:
        todo.assigned_staff.remove(staff_user)
        db.session.commit()
        return True, None
    
    return False, 'Nhân viên này không được giao công việc này.'


def get_todo_assigned_staff(todo_id):
    """Get list of staff assigned to a todo."""
    todo = AdminTodo.query.get(todo_id)
    if not todo:
        return None
    
    return [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        for user in (todo.assigned_staff or [])
    ]


def get_feedback_reviews(search='', rating='all', reply_status='all'):
    reviews = list_reviews(search=search, rating_filter=rating)
    normalized_reply_status = (reply_status or 'all').strip().lower()

    if normalized_reply_status == 'unreplied':
        reviews = [item for item in reviews if not (item.get('admin_reply') or '').strip()]
    elif normalized_reply_status == 'replied':
        reviews = [item for item in reviews if (item.get('admin_reply') or '').strip()]
    else:
        normalized_reply_status = 'all'

    replied_count = sum(1 for item in reviews if (item.get('admin_reply') or '').strip())
    unreplied_count = len(reviews) - replied_count

    return {
        'items': reviews,
        'search': (search or '').strip(),
        'rating_filter': (rating or 'all').strip().lower(),
        'reply_status_filter': normalized_reply_status,
        'total': len(reviews),
        'replied_count': replied_count,
        'unreplied_count': unreplied_count,
    }


def create_product(data, image_file=None):
    try:
        name = (data.get('name') or '').strip()
        if not name:
            return None, 'Tên sản phẩm không được để trống.'

        category = (data.get('category') or '').strip()
        if not category:
            return None, 'Danh mục không được để trống.'

        try:
            price = int(data.get('price', 0))
        except (TypeError, ValueError):
            return None, 'Giá sản phẩm phải là số nguyên hợp lệ.'
        if price < 0:
            return None, 'Giá sản phẩm không được âm.'

        try:
            in_stock = int(data.get('in_stock', 0))
        except (TypeError, ValueError):
            return None, 'Số lượng tồn kho phải là số nguyên hợp lệ.'
        if in_stock < 0:
            return None, 'Số lượng tồn kho không được âm.'

        try:
            cost_price = int(data.get('cost_price', 0))
        except (TypeError, ValueError):
            return None, 'Giá vốn phải là số nguyên hợp lệ.'
        if cost_price < 0:
            return None, 'Giá vốn không được âm.'

        expiry_date_raw = (data.get('expiry_date') or '').strip()
        expiry_date = None
        if expiry_date_raw:
            try:
                expiry_date = date.fromisoformat(expiry_date_raw)
            except ValueError:
                return None, 'Hạn sử dụng không hợp lệ. Vui lòng chọn đúng định dạng ngày.'

        if in_stock > 0 and not expiry_date:
            return None, 'Khi nhập tồn kho ban đầu, vui lòng cung cấp hạn sử dụng cho lô hàng.'

        # Upload ảnh lên Cloudinary thay vì lưu local
        image_url, image_id, image_error = _upload_image_to_cloudinary(image_file)
        if image_error:
            return None, image_error

        product = Product(
            name        = name,
            description = (data.get('description') or '').strip() or None,
            price       = price,
            category    = category,
            in_stock    = in_stock,
            cost_price  = cost_price,
            image_url   = image_url,
            image_id    = image_id,
        )
        db.session.add(product)
        db.session.flush()

        if in_stock > 0 and expiry_date:
            db.session.add(
                ProductBatch(
                    product_id=product.id,
                    quantity=in_stock,
                    cost_price=cost_price,
                    expiry_date=expiry_date,
                    imported_at=datetime.utcnow(),
                )
            )

        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def update_product(product_id, data, image_file=None):
    product = Product.query.get(product_id)
    if not product:
        return None, 'Sản phẩm không tồn tại.'

    try:
        if image_file and image_file.filename:
            new_image_url, image_error = _save_image_to_static(image_file)
            if image_error:
                return None, image_error

            if product.image_url:
                _delete_local_image(product.image_url)
            if product.image_id:
                delete_image(product.image_id)

            product.image_url = new_image_url
            product.image_id = None

        name = data.get('name')
        if name is not None:
            name = name.strip()
            if not name:
                return None, 'Tên sản phẩm không được để trống.'
            product.name = name

        product.description = data.get('description', product.description)

        price_value = data.get('price')
        if price_value is not None:
            try:
                parsed_price = int(price_value)
            except (TypeError, ValueError):
                return None, 'Giá sản phẩm phải là số nguyên hợp lệ.'

            if parsed_price < 0:
                return None, 'Giá sản phẩm không được âm.'
            product.price = parsed_price

        category = data.get('category')
        if category is not None:
            category = category.strip()
            if not category:
                return None, 'Danh mục không được để trống.'
            product.category = category

        in_stock_value = data.get('in_stock')
        if in_stock_value is not None:
            try:
                parsed_stock = int(in_stock_value)
            except (TypeError, ValueError):
                return None, 'Số lượng tồn kho phải là số nguyên hợp lệ.'

            if parsed_stock < 0:
                return None, 'Số lượng tồn kho không được âm.'
            product.in_stock = parsed_stock

        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return False, 'Sản phẩm không tồn tại hoặc đã bị xóa.'

    try:
        if product.image_url:
            _delete_local_image(product.image_url)
        if product.image_id:
            delete_image(product.image_id)
        db.session.delete(product)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def update_order_status(order_id, status):
    if status not in VALID_ORDER_STATUSES:
        return False, 'Trạng thái đơn hàng không hợp lệ.'

    order = Order.query.get(order_id)
    if not order:
        return False, 'Không tìm thấy đơn hàng.'

    try:
        order.status = status

        payment = Payment.query.filter_by(order_id=order.id).first()

        if status == 'confirmed':
            order.paid_at = order.paid_at or datetime.utcnow()

            if not payment:
                payment = Payment(
                    order_id=order.id,
                    method=order.payment_method or 'cash',
                    amount=(order.total or 0) + (order.shipping_fee or 0),
                    status='pending',
                )
                db.session.add(payment)

            payment.method = order.payment_method or payment.method or 'cash'
            payment.amount = (order.total or 0) + (order.shipping_fee or 0)
            payment.status = 'success'

        elif status == 'cancelled' and payment and payment.status != 'success':
            payment.status = 'failed'

        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)
