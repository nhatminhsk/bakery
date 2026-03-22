from app.extensions import db
from app.models.user import User


def register_user(username, email, password):
    """Tạo user mới. Trả về (user, None) nếu thành công, (None, error_msg) nếu lỗi."""
    if User.query.filter_by(username=username).first():
        return None, 'Tên đăng nhập đã tồn tại!'
    if User.query.filter_by(email=email).first():
        return None, 'Email đã được sử dụng!'

    # Tài khoản đầu tiên trong hệ thống được cấp quyền admin.
    is_first_account = User.query.first() is None
    role = 'admin' if is_first_account else 'customer'

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None


def authenticate_user(username, password):
    """Xác thực đăng nhập. Trả về (user, role) nếu hợp lệ, (None, None) nếu sai."""
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user, user.role
    return None, None
