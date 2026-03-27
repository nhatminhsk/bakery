from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.admin.services import (
    get_dashboard_stats, get_all_orders, get_all_products_admin,
    create_product, update_product, delete_product, update_order_status,
    get_overview_orders,
    get_admin_todos, create_admin_todo, toggle_admin_todo, delete_admin_todo,
    get_feedback_reviews,
    get_admin_settings, update_admin_settings,
)
from app.utils.review_store import add_admin_reply, get_review_by_id

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('products.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/dashboard')
@admin_required
def dashboard_alias():
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/overview')
@admin_required
def overview():
    stats = get_dashboard_stats()
    period = request.args.get('period', 'today')
    overview_data = get_overview_orders(period=period, limit=200)
    return render_template('admin/overview.html', stats=stats, overview=overview_data)


@admin_bp.route('/products')
@admin_required
def products():
    items = get_all_products_admin()
    return render_template('admin/products.html', products=items)


@admin_bp.route('/products/create', methods=['POST'])
@admin_required
def product_create():
    image_file = request.files.get('image')
    data = request.form.to_dict()
    product, error = create_product(data, image_file)
    if error:
        flash(error, 'error')
    else:
        flash(f'Đã thêm sản phẩm: {product.name}', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:product_id>/update', methods=['POST'])
@admin_required
def product_update(product_id):
    image_file = request.files.get('image')
    data = request.form.to_dict()
    product, error = update_product(product_id, data, image_file)
    if error:
        flash(error, 'error')
    else:
        flash(f'Đã cập nhật: {product.name}', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def product_delete(product_id):
    success, error = delete_product(product_id)
    if success:
        flash('Đã xóa sản phẩm.', 'success')
    else:
        flash(error or 'Không thể xóa sản phẩm.', 'error')
    return redirect(url_for('admin.products'))


@admin_bp.route('/orders')
@admin_required
def orders():
    all_orders = get_all_orders()
    return render_template('admin/new_orders.html', orders=all_orders)


@admin_bp.route('/new-orders')
@admin_required
def orders_alias():
    return redirect(url_for('admin.orders'))


@admin_bp.route('/todo-lists')
@admin_required
def todo_lists():
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    todo_data = get_admin_todos(status=status, priority=priority)
    return render_template('admin/todo_lists.html', todo=todo_data)


@admin_bp.route('/todo-lists/create', methods=['POST'])
@admin_required
def todo_create():
    title = request.form.get('title', '')
    priority = request.form.get('priority', 'medium')

    success, error = create_admin_todo(title=title, priority=priority)
    if success:
        flash('Đã thêm công việc mới.', 'success')
    else:
        flash(error or 'Không thể thêm công việc.', 'error')
    return redirect(url_for('admin.todo_lists'))


@admin_bp.route('/todo-lists/<int:todo_id>/toggle', methods=['POST'])
@admin_required
def todo_toggle(todo_id):
    success, error = toggle_admin_todo(todo_id)
    if success:
        flash('Đã cập nhật trạng thái công việc.', 'success')
    else:
        flash(error or 'Không thể cập nhật công việc.', 'error')
    return redirect(url_for('admin.todo_lists'))


@admin_bp.route('/todo-lists/<int:todo_id>/delete', methods=['POST'])
@admin_required
def todo_delete(todo_id):
    success, error = delete_admin_todo(todo_id)
    if success:
        flash('Đã xóa công việc.', 'success')
    else:
        flash(error or 'Không thể xóa công việc.', 'error')
    return redirect(url_for('admin.todo_lists'))


@admin_bp.route('/feedbacks')
@admin_required
def feedbacks():
    search = request.args.get('q', '')
    rating = request.args.get('rating', 'all')
    feedback_data = get_feedback_reviews(search=search, rating=rating)
    return render_template('admin/feedbacks.html', feedback=feedback_data)


@admin_bp.route('/reviews/<int:review_id>/reply', methods=['GET'])
@admin_required
def review_reply_form(review_id):
    """Get reply form for a review (AJAX)."""
    review = get_review_by_id(review_id)
    if not review:
        return jsonify({'error': 'Không tìm thấy đánh giá'}), 404
    
    return jsonify({
        'review_id': review_id,
        'username': review.get('username'),
        'product_name': review.get('product_name'),
        'comment': review.get('comment'),
        'admin_reply': review.get('admin_reply'),
        'admin_reply_at': review.get('admin_reply_at'),
    })


@admin_bp.route('/reviews/<int:review_id>/reply', methods=['POST'])
@admin_required
def review_reply_submit(review_id):
    """Submit admin reply to a review."""
    reply_text = request.form.get('reply', '').strip()
    
    success, error = add_admin_reply(review_id, reply_text)
    
    if success:
        return jsonify({'success': True, 'message': 'Đã phản hồi thành công'})
    else:
        return jsonify({'success': False, 'error': error or 'Lỗi khi phản hồi'}), 400


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        success, error = update_admin_settings(request.form)
        if success:
            flash('Đã lưu cài đặt thành công.', 'success')
        else:
            flash(error or 'Không thể lưu cài đặt.', 'error')
        return redirect(url_for('admin.settings'))

    settings_data = get_admin_settings()
    return render_template('admin/settings.html', settings=settings_data)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def order_status(order_id):
    status = request.form.get('status')
    success, error = update_order_status(order_id, status)
    if success:
        flash('Đã cập nhật trạng thái đơn hàng.', 'success')
    else:
        flash(error or 'Không thể cập nhật trạng thái đơn hàng.', 'error')
    return redirect(url_for('admin.orders'))
