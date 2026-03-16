from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.services import register_user, authenticate_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user, error = register_user(username, email, password)
        if error:
            flash(error, 'error')
        else:
            flash('Đăng ký thành công! Mời bạn đăng nhập.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = authenticate_user(username, password)
        if user:
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('products.index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('products.index'))


@auth_bp.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)
