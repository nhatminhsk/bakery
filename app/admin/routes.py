from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.admin.services import (
    get_dashboard_stats, get_all_orders, get_all_products_admin,
    create_product, update_product, delete_product, update_order_status
)

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


@admin_bp.route('/overview')
@admin_required
def overview():
    stats = get_dashboard_stats()
    return render_template('admin/overview.html', stats=stats)


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


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def order_status(order_id):
    status = request.form.get('status')
    update_order_status(order_id, status)
    flash('Đã cập nhật trạng thái đơn hàng.', 'success')
    return redirect(url_for('admin.orders'))
