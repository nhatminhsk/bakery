from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user, login_required


def roles_required(*roles, redirect_endpoint='products.index'):
    allowed_roles = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in allowed_roles:
                flash('Bạn không có quyền truy cập trang này.', 'error')
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def staff_required(redirect_endpoint='products.index'):
    """Decorator to require staff or admin role."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in {'staff', 'admin'}:
                flash('Bạn không có quyền truy cập trang này.', 'error')
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(redirect_endpoint='products.index'):
    """Decorator to require admin role."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role != 'admin':
                flash('Bạn không có quyền truy cập trang này.', 'error')
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def check_store_access(store_id):
    """Check if current user can access a specific store.
    
    Returns True if:
    - User is admin (can access all stores)
    - User is staff assigned to this store
    - Otherwise False
    """
    if current_user.is_admin():
        return True
    
    if current_user.is_staff():
        from app.utils.store_helper import get_user_store
        user_store = get_user_store(current_user.id)
        if user_store and user_store.id == store_id:
            return True
    
    return False
