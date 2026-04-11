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