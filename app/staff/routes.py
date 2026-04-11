from flask import Blueprint, jsonify, redirect, render_template, request, url_for, flash
from flask_login import current_user

from app.staff.services import (
    get_staff_dashboard_data,
    get_staff_feedback_data,
    get_staff_inventory_products,
    get_staff_orders_data,
    get_staff_todos,
    update_staff_order_status,
)
from app.utils.permissions import roles_required
from app.utils.review_store import add_admin_reply, get_review_by_id

staff_bp = Blueprint('staff', __name__)
staff_required = roles_required('staff', 'admin')


@staff_bp.route('/')
@staff_required
def dashboard():
    data = get_staff_dashboard_data()
    return render_template('staff/dashboard.html', data=data)


@staff_bp.route('/dashboard')
@staff_required
def dashboard_alias():
    return redirect(url_for('staff.dashboard'))


@staff_bp.route('/orders')
@staff_required
def orders():
    filter_mode = request.args.get('filter', 'latest')
    selected_date = request.args.get('date', '')
    orders_data = get_staff_orders_data(filter_mode=filter_mode, date_value=selected_date)
    return render_template('staff/orders.html', orders_data=orders_data)


@staff_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@staff_required
def order_status(order_id):
    status = request.form.get('status')
    success, error = update_staff_order_status(order_id, status)
    if success:
        flash('Đã cập nhật trạng thái đơn hàng.', 'success')
    else:
        flash(error or 'Không thể cập nhật trạng thái đơn hàng.', 'error')
    return redirect(url_for('staff.orders'))


@staff_bp.route('/inventory')
@staff_required
def inventory():
    products = get_staff_inventory_products()
    return render_template('staff/inventory.html', products=products)


@staff_bp.route('/feedbacks')
@staff_required
def feedbacks():
    search = request.args.get('q', '')
    rating = request.args.get('rating', 'all')
    reply_status = request.args.get('reply_status', 'all')
    feedback_data = get_staff_feedback_data(search=search, rating=rating, reply_status=reply_status)
    return render_template('staff/feedbacks.html', feedback=feedback_data)


@staff_bp.route('/todos')
@staff_required
def todos():
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    todo_data = get_staff_todos(current_user.id, status=status, priority=priority)
    return render_template('staff/todos.html', todo=todo_data)


@staff_bp.route('/reviews/<int:review_id>/reply', methods=['GET'])
@staff_required
def review_reply_form(review_id):
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


@staff_bp.route('/reviews/<int:review_id>/reply', methods=['POST'])
@staff_required
def review_reply_submit(review_id):
    reply_text = request.form.get('reply', '').strip()
    success, error = add_admin_reply(review_id, reply_text)

    if success:
        return jsonify({'success': True, 'message': 'Đã phản hồi thành công'})
    return jsonify({'success': False, 'error': error or 'Lỗi khi phản hồi'}), 400
