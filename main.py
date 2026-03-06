from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__, static_folder='static', template_folder='Templates')
app.secret_key = 'nhatminhsk' # Khóa bí mật để sử dụng session và flash 


# Lấy đường dẫn tuyệt đối đến thư mục chứa file main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Kết nối chính xác đến file trong thư mục database/bakery.db
sqldbname = os.path.join(BASE_DIR, 'database', 'bakery.db')

def get_db_connection():
    """Tạo kết nối tới SQLite và trả về dữ liệu dưới dạng Dictionary."""
    # Đảm bảo thư mục database tồn tại
    if not os.path.exists('database'):
        os.makedirs('database')
        
    conn = sqlite3.connect(sqldbname)
    conn.row_factory = sqlite3.Row # Cho phép truy cập cột theo tên
    return conn

@app.route('/')
def index():
    """Trang chủ của hệ thống."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Lấy tất cả sản phẩm hoặc một số sản phẩm được đề xuất
        recommended_products = cur.execute('SELECT * FROM products LIMIT 10').fetchall()
        conn.close()
        return render_template('index.html', recommended_products=recommended_products)
    except sqlite3.OperationalError:
        # Nếu bảng chưa tồn tại, truyền danh sách rỗng
        return render_template('index.html', recommended_products=[])

@app.route('/search', methods=['GET'])
def search():
    """Tìm kiếm sản phẩm theo từ khóa."""
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Tìm kiếm sản phẩm theo tên hoặc mô tả
            results = cur.execute(
                'SELECT * FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY name',
                (f'%{query}%', f'%{query}%')
            ).fetchall()
            conn.close()
        except sqlite3.OperationalError:
            # Nếu bảng chưa tồn tại, truyền danh sách rỗng
            results = []
    
    return render_template('search.html', query=query, results=results)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Xử lý đăng ký người dùng mới."""
    if request.method == 'POST':
        # Lấy dữ liệu (JS đã check định dạng, nên ở đây ta nhận luôn)
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                        (username, email, password))
            conn.commit()
            conn.close()
            
            flash("Đăng ký thành công! Mời bạn đăng nhập.", "success")
            return render_template('login.html', registration_status='success')
            
        except sqlite3.IntegrityError:
            flash("Tên đăng nhập hoặc Email đã tồn tại!", "error")
            return render_template('login.html', registration_status='error')
        except Exception as e:
            flash(f"Lỗi hệ thống: {str(e)}", "error")
            return render_template('login.html', registration_status='error')
            
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Xử lý đăng nhập người dùng."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        conn = get_db_connection()
        # Tìm kiếm người dùng có thông tin khớp trong bảng 'users'
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                         (username, password)).fetchone()
        conn.close()

        if user:
            # Lưu thông tin vào session khi đăng nhập thành công 
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Đăng xuất và xóa session."""
    session.clear() # Xóa sạch dữ liệu phiên làm việc 
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/account')
def account():
    """Trang thông tin tài khoản (Yêu cầu đăng nhập)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('account.html')

@app.route('/cart')
def cart():
    """Trang giỏ hàng."""
    return render_template('cart.html')

if __name__ == '__main__':
    # Khởi chạy ứng dụng ở chế độ Debug để dễ theo dõi lỗi 
    app.run(debug=True)