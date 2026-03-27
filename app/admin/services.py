from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
import json

from app.extensions import db
from app.models.product import Product, Category
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.models.admin import AdminTodo
from app.utils.cloudinary_helper import delete_image
from app.utils.review_store import list_reviews
from sqlalchemy import func
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


def get_dashboard_stats():
    weekly_series = get_revenue_by_week(limit_weeks=8)
    monthly_series = get_revenue_by_month(limit_months=12)

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


def get_all_orders():
    return Order.query.order_by(Order.created_at.desc()).all()


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
    return Product.query.order_by(Product.created_at.desc()).all()


def _seed_default_admin_todos():
    """Seed default todos if the table is empty."""
    if AdminTodo.query.first() is not None:
        return  # Table already has data

    defaults = [
        AdminTodo(
            title='Kiểm tra tồn kho nguyên liệu đầu ca',
            priority='high',
            is_done=False,
        ),
        AdminTodo(
            title='Xác nhận lịch giao hàng đơn quan trọng',
            priority='medium',
            is_done=False,
        ),
        AdminTodo(
            title='Tổng vệ sinh khu vực đóng gói',
            priority='low',
            is_done=True,
            completed_at=datetime.utcnow(),
        ),
    ]
    db.session.add_all(defaults)
    db.session.commit()


def _todo_priority_weight(priority):
    mapping = {'high': 3, 'medium': 2, 'low': 1}
    return mapping.get(priority, 0)


def get_admin_todos(status='all', priority='all'):
    # Seed default todos if table is empty
    _seed_default_admin_todos()

    query = AdminTodo.query

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

    todos = query.all()

    # Sort: incomplete first, then by priority, then by creation date
    todos.sort(
        key=lambda item: (
            item.is_done,
            -_todo_priority_weight(item.priority),
            item.created_at or '',
        )
    )

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


def create_admin_todo(title, priority='medium'):
    title = (title or '').strip()
    if not title:
        return False, 'Nội dung công việc không được để trống.'

    priority = (priority or 'medium').strip().lower()
    if priority not in {'high', 'medium', 'low'}:
        priority = 'medium'

    todo = AdminTodo(title=title, priority=priority, is_done=False)
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


def get_feedback_reviews(search='', rating='all'):
    reviews = list_reviews(search=search, rating_filter=rating)

    return {
        'items': reviews,
        'search': (search or '').strip(),
        'rating_filter': (rating or 'all').strip().lower(),
        'total': len(reviews),
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

        image_url, image_error = _save_image_to_static(image_file)
        if image_error:
            return None, image_error

        product = Product(
            name        = name,
            description = (data.get('description') or '').strip() or None,
            price       = price,
            category    = category,
            in_stock    = in_stock,
            image_url   = image_url,
            image_id    = None,
        )
        db.session.add(product)
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
