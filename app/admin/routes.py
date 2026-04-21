from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.admin.services import (
    get_dashboard_stats, get_all_products_admin,
    create_product, update_product, delete_product, update_order_status,
    get_overview_orders,
    get_orders_management_data,
    get_admin_todos, create_admin_todo, toggle_admin_todo, delete_admin_todo,
    add_users_to_staff,
    get_assignable_staff_users,
    get_staff_candidate_users,
    assign_staff_to_todo,
    add_staff_to_todo,
    remove_staff_from_todo,
    get_todo_assigned_staff,
    get_feedback_reviews,
    get_accounts_management_data,
    update_user_role,
    toggle_user_active,
    get_admin_settings, update_admin_settings,
)
from app.utils.review_store import add_admin_reply, get_review_by_id
from app.utils.permissions import roles_required
from app.models.store import Store

admin_bp = Blueprint('admin', __name__)


admin_required = roles_required('admin')


def get_all_stores():
    """Get all active stores for dropdown."""
    return Store.query.filter_by(is_active=True).order_by(Store.id).all()


@admin_bp.route('/')
@admin_required
def dashboard():
    store_id = request.args.get('store_id', type=int)
    stats = get_dashboard_stats(store_id=store_id)
    stores = get_all_stores()
    selected_store = None
    if store_id:
        selected_store = Store.query.filter_by(id=store_id, is_active=True).first()
    return render_template('admin/dashboard.html', stats=stats, selected_store_id=store_id, 
                         stores=stores, selected_store=selected_store)


@admin_bp.route('/dashboard')
@admin_required
def dashboard_alias():
    store_id = request.args.get('store_id', type=int)
    return redirect(url_for('admin.dashboard', store_id=store_id) if store_id else url_for('admin.dashboard'))


@admin_bp.route('/overview')
@admin_required
def overview():
    store_id = request.args.get('store_id', type=int)
    stats = get_dashboard_stats(store_id=store_id)
    period = request.args.get('period', 'today')
    overview_data = get_overview_orders(period=period, limit=200, store_id=store_id)
    stores = get_all_stores()
    selected_store = None
    if store_id:
        selected_store = Store.query.filter_by(id=store_id, is_active=True).first()
    return render_template('admin/overview.html', stats=stats, overview=overview_data, selected_store_id=store_id,
                         stores=stores, selected_store=selected_store)


@admin_bp.route('/products')
@admin_required
def products():
    store_id = request.args.get('store_id', type=int)
    items = get_all_products_admin(store_id=store_id)
    stores = get_all_stores()
    selected_store = None
    if store_id:
        selected_store = Store.query.filter_by(id=store_id, is_active=True).first()
    return render_template('admin/products.html', products=items, selected_store_id=store_id,
                         stores=stores, selected_store=selected_store)


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
    filter_mode = request.args.get('filter', 'latest')
    selected_date = request.args.get('date', '')
    store_id = request.args.get('store_id', type=int)
    orders_data = get_orders_management_data(filter_mode=filter_mode, date_value=selected_date, store_id=store_id)
    stores = get_all_stores()
    selected_store = None
    if store_id:
        selected_store = Store.query.filter_by(id=store_id, is_active=True).first()
    return render_template('admin/new_orders.html', orders_data=orders_data, selected_store_id=store_id,
                         stores=stores, selected_store=selected_store)


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
    staff_users = get_assignable_staff_users()
    staff_candidates = get_staff_candidate_users()
    return render_template(
        'admin/todo_lists.html',
        todo=todo_data,
        staff_users=staff_users,
        staff_candidates=staff_candidates,
    )


@admin_bp.route('/todo-lists/create', methods=['POST'])
@admin_required
def todo_create():
    title = request.form.get('title', '')
    priority = request.form.get('priority', 'medium')
    assigned_user_id = request.form.get('assigned_user_id')

    success, error = create_admin_todo(title=title, priority=priority, assigned_user_id=assigned_user_id)
    if success:
        flash('Đã thêm công việc mới.', 'success')
    else:
        flash(error or 'Không thể thêm công việc.', 'error')
    return redirect(url_for('admin.todo_lists'))


@admin_bp.route('/todo-lists/add-staff', methods=['POST'])
@admin_required
def todo_add_staff():
    selected_user_ids = request.form.getlist('user_ids')
    success, updated_count, error = add_users_to_staff(selected_user_ids)
    if success:
        if updated_count > 0:
            flash(f'Đã thêm {updated_count} tài khoản vào nhóm nhân viên.', 'success')
        else:
            flash('Các tài khoản đã thuộc nhóm nhân viên từ trước.', 'info')
    else:
        flash(error or 'Không thể thêm nhân viên.', 'error')
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


@admin_bp.route('/todo-lists/assign', methods=['GET', 'POST'])
@admin_required
def todo_assign():
    """Manage staff assignments for a todo (modal form)."""
    todo_id = request.args.get('todo_id', type=int) or request.form.get('todo_id', type=int)
    
    if not todo_id:
        return jsonify({'error': 'Missing todo_id'}), 400
    
    if request.method == 'GET':
        # Return JSON with current assignments and available staff
        assigned_staff = get_todo_assigned_staff(todo_id)
        available_staff = get_assignable_staff_users()
        
        available_data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_assigned': any(s['id'] == user.id for s in (assigned_staff or [])),
            }
            for user in available_staff
        ]
        
        return jsonify({
            'todo_id': todo_id,
            'assigned_staff': assigned_staff or [],
            'available_staff': available_data,
        })
    
    # POST: Update assignments
    action = request.form.get('action', 'set')  # 'set', 'add', 'remove'
    staff_user_ids = request.form.getlist('staff_user_ids')
    staff_user_id = request.form.get('staff_user_id')  # For remove action
    
    if action == 'set':
        # Replace all assignments
        success, count, error = assign_staff_to_todo(todo_id, staff_user_ids)
        if success:
            flash(f'Đã giao công việc cho {count} nhân viên.', 'success')
        else:
            flash(error or 'Không thể cập nhật giao việc.', 'error')
    
    elif action == 'add':
        # Add additional staff
        success, count, error = add_staff_to_todo(todo_id, staff_user_ids)
        if success:
            if count > 0:
                flash(f'Đã thêm {count} nhân viên vào công việc này.', 'success')
            else:
                flash('Các nhân viên đã được giao công việc này rồi.', 'info')
        else:
            flash(error or 'Không thể thêm nhân viên.', 'error')
    
    elif action == 'remove':
        # Remove a staff member
        success, error = remove_staff_from_todo(todo_id, staff_user_id)
        if success:
            flash('Đã xóa nhân viên khỏi công việc này.', 'success')
        else:
            flash(error or 'Không thể xóa nhân viên.', 'error')
    
    return redirect(url_for('admin.todo_lists'))


@admin_bp.route('/feedbacks')
@admin_required
def feedbacks():
    search = request.args.get('q', '')
    rating = request.args.get('rating', 'all')
    reply_status = request.args.get('reply_status', 'all')
    store_id = request.args.get('store_id', type=int)
    feedback_data = get_feedback_reviews(search=search, rating=rating, reply_status=reply_status, store_id=store_id)
    stores = get_all_stores()
    selected_store = None
    if store_id:
        selected_store = Store.query.filter_by(id=store_id, is_active=True).first()
    return render_template('admin/feedbacks.html', feedback=feedback_data, selected_store_id=store_id,
                         stores=stores, selected_store=selected_store)


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


@admin_bp.route('/accounts')
@admin_required
def accounts():
    search = request.args.get('q', '')
    role = request.args.get('role', 'all')
    status = request.args.get('status', 'all')
    accounts_data = get_accounts_management_data(search=search, role=role, status=status)
    return render_template('admin/accounts.html', accounts=accounts_data)


@admin_bp.route('/accounts/<int:user_id>/role', methods=['POST'])
@admin_required
def account_update_role(user_id):
    new_role = request.form.get('role', '')
    success, error = update_user_role(user_id, new_role, current_user.id)
    if success:
        flash('Đã cập nhật vai trò tài khoản.', 'success')
    else:
        flash(error or 'Không thể cập nhật vai trò.', 'error')
    return redirect(url_for('admin.accounts'))


@admin_bp.route('/accounts/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def account_toggle_active(user_id):
    success, error = toggle_user_active(user_id, current_user.id)
    if success:
        flash('Đã cập nhật trạng thái tài khoản.', 'success')
    else:
        flash(error or 'Không thể cập nhật trạng thái tài khoản.', 'error')
    return redirect(url_for('admin.accounts'))


@admin_bp.route('/import-stock', methods=['POST'])
@admin_required
def import_product_stock():
    """Import stock for a single product with 24-hour expiry."""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int, default=0)
    
    if not product_id or quantity <= 0:
        flash('❌ Sản phẩm hoặc số lượng không hợp lệ.', 'error')
        return redirect(request.referrer or url_for('admin.products'))
    
    from app.admin.services import import_product_batch
    
    try:
        result = import_product_batch(product_id, quantity)
        if result['success']:
            flash(
                f"✓ Nhập thành công! Tạo lô hàng {quantity} cái cho '{result['product_name']}'. "
                f"Hạn sử dụng: {result['expiry_at']}",
                'success'
            )
        else:
            flash(f"❌ Lỗi: {result['message']}", 'error')
    except Exception as e:
        flash(f'❌ Lỗi khi nhập hàng: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('admin.products'))


@admin_bp.route('/clear-old-batches', methods=['POST'])
@admin_required
def clear_old_batches():
    """Clear all old batches (set quantity to 0)."""
    from app.admin.services import clear_all_batches
    
    store_id = request.args.get('store_id', type=int)
    
    try:
        result = clear_all_batches(store_id=store_id)
        flash(f"✓ {result['message']}", 'success')
    except Exception as e:
        flash(f'❌ Lỗi: {str(e)}', 'error')
    
    return redirect(url_for('admin.products', store_id=store_id) if store_id else url_for('admin.products'))


@admin_bp.route('/import-all-batches', methods=['POST'])
@admin_required
def import_all_batches():
    """Import 50 units for all products in selected store with 24-hour expiry."""
    from app.admin.services import import_all_product_batches
    
    store_id = request.args.get('store_id', type=int)
    
    if not store_id:
        flash('❌ Vui lòng chọn cơ sở trước khi nhập hàng.', 'error')
        return redirect(url_for('admin.products'))
    
    try:
        result = import_all_product_batches(store_id=store_id)
        flash(
            f"✓ Nhập hàng thành công! Tạo {result['total_batches']} lô hàng cho {result['total_products']} sản phẩm. "
            f"Hạn sử dụng: {result['expiry_at']}",
            'success'
        )
    except Exception as e:
        flash(f'❌ Lỗi: {str(e)}', 'error')
    
    return redirect(url_for('admin.products', store_id=store_id))


@admin_bp.route('/test-expiry-batches', methods=['POST'])
@admin_required
def test_expiry_batches():
    """Test: Import 1 batch of 5 random products from April 18 at 20:30."""
    from app.admin.services import import_april18_batch
    
    store_id = request.args.get('store_id', type=int)
    
    try:
        result = import_april18_batch(store_id=store_id)
        if result['status'] == 'success':
            flash(
                f"🧪 TEST: Nhập lô hàng từ 18/4 20:30 cho 5 sản phẩm ({result['total_units']} units). "
                f"Hạn hết: {result['expiry_at']}",
                'success'
            )
        else:
            flash(f'❌ {result["message"]}', 'error')
    except Exception as e:
        flash(f'❌ Lỗi: {str(e)}', 'error')
    
    return redirect(url_for('admin.products', store_id=store_id) if store_id else url_for('admin.products'))


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


@admin_bp.route('/import-stock', methods=['POST'])
@admin_required
def import_stock():
    """Import stock batches with 24-hour expiry for selected store."""
    store_id = request.form.get('store_id', type=int)
    
    # Import the function from services
    from app.admin.services import import_stock_batches
    
    try:
        result = import_stock_batches(store_id=store_id)
        flash(
            f'✓ Nhập hàng thành công! Tạo {result["total_batches"]} lô hàng cho {result["total_products"]} sản phẩm. '
            f'Hạn sử dụng: {result["expiry_at"]}',
            'success'
        )
    except Exception as e:
        flash(f'❌ Lỗi khi nhập hàng: {str(e)}', 'error')
    
    # Redirect to products page with same store filter
    return redirect(url_for('admin.products', store_id=store_id) if store_id else url_for('admin.products'))
