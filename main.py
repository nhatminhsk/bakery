from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__, static_folder='static', template_folder='Templates')
app.secret_key = 'nhatminhsk' # Khóa bí mật để sử dụng session và flash 



# Dữ liệu mẫu dạng JSON
products_list = [
    {
        "id": 1,
        "name": "Bánh Kem Dâu Tây",
        "category": "Bánh Kem",
        "price": 25000,
        "image": "static/images/products/bagel.png",
        "rating": 4.8,
        "date": "2023-10-01",
        "inStock": 15
    },
    {
        "id": 2,
        "name": "Croissant Bơ Pháp",
        "category": "Bánh Mì",
        "price": 45000,
        "image": "static/images/products/croissant.jpg",
        "rating": 4.5,
        "date": "2023-09-15",
        "inStock": 12
    },
    {
        "id": 3,
        "name": "Cupcake Socola",
        "category": "Bánh Ngọt",
        "price": 35000,
        "image": "static/images/products/cupcake.jpg",
        "rating": 4.2,
        "date": "2023-10-05",
        "inStock": 0
    },
    {
        "id": 4,
        "name": "Bánh Mì Bơ Tỏi",
        "category": "Bánh Mì",
        "price": 30000,
        "image": "static/images/products/garlic_bread.jpg",
        "rating": 4.6,
        "date": "2023-09-20",
        "inStock": 18
    },
    {
        "id": 5,
        "name": "Bánh Tart Trái Cây",
        "category": "Bánh Ngọt",
        "price": 40000,
        "image": "static/images/products/fruit_tart.jpg",
        "rating": 4.7,
        "date": "2023-10-03",
        "inStock": 19
    },
    {
        "id": 6,
        "name": "Bánh Mì Gà Nướng",
        "category": "Bánh Mì",
        "price": 50000,
        "image": "static/images/products/grilled_chicken_bread.jpg",
        "rating": 4.3,
        "date": "2023-09-25",
        "inStock": 16
    }
]
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
                'SELECT *OM produ FRcts WHERE name LIKE ? OR description LIKE ? ORDER BY name',
                (f'%{query}%', f'%{query}%')
            ).fetchall()
            conn.close()
        except sqlite3.OperationalError:
            # Nếu bảng chưa tồn tại, truyền danh sách rỗng
            results = []
    
    return render_template('search.html', query=query, results=results)
@app.route('/products')
def products():
    category = request.args.get('category', '').strip()
    # Sửa từ PRODUCTS thành products_list
    if category:
        filtered_products = [p for p in products_list if p['category'] == category]
    else:
        filtered_products = products_list
        
    categories = [{"name": c} for c in set(p['category'] for p in products_list)]
    return render_template('index.html', 
                           products=filtered_products, 
                           categories=categories, 
                           selected_category=category)
@app.route('/')
def index():
    """Trang chủ hiển thị sản phẩm từ danh sách JSON."""
    selected_category = request.args.get('category')
    
    # Lọc sản phẩm theo danh mục nếu có
    if selected_category:
        display_products = [p for p in products_list if p['category'] == selected_category]
    else:
        display_products = products_list
        
    # Tạo danh sách category để hiển thị các nút lọc
    categories = [{"name": c} for c in set(p['category'] for p in products_list)]
    
    return render_template('index.html', 
                           products=display_products, 
                           categories=categories,
                           selected_category=selected_category)

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
    """Trang giỏ hàng"""
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)
def get_cart_totals(cart):
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    shipping_fee = 0 if subtotal >= 50000 else 20000
    if subtotal == 0: shipping_fee = 0 # Nếu giỏ hàng trống thì không tính ship
    total = subtotal + shipping_fee
    cart_count = sum(item['quantity'] for item in cart)
    return subtotal, shipping_fee, total, cart_count
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart_api():
    data = request.get_json()
    product_id = int(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    # Tìm sản phẩm trong products_list
    product = next((p for p in products_list if p['id'] == product_id), None)
    
    if product:
        for item in cart:
            if item['id'] == product_id:
                item['quantity'] += quantity
                break
        else:
            cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': quantity
            })
        
        session['cart'] = cart # Lưu lại vào session
        session.modified = True 
        return {"success": True, "cart_count": sum(item['quantity'] for item in cart)}
    
    return {"success": False}, 400

@app.route('/api/cart/update', methods=['POST'])
def update_cart_api():
    data = request.get_json()
    product_id = int(data.get('product_id'))
    delta = int(data.get('delta'))

    if 'cart' not in session:
        return {"success": False}, 400

    cart = session['cart']
    item_new_qty = 0
    item_price = 0
    
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += delta
            # Không cho giảm xuống dưới 1
            if item['quantity'] < 1: 
                item['quantity'] = 1
            item_new_qty = item['quantity']
            item_price = item['price']
            break

    session['cart'] = cart
    session.modified = True
    
    subtotal, shipping, total, cart_count = get_cart_totals(cart)
    
    return {
        "success": True, 
        "item_qty": item_new_qty,
        "item_price": item_price,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "cart_count": cart_count
    }

@app.route('/api/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart_api(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True
        
    cart = session.get('cart', [])
    subtotal, shipping, total, cart_count = get_cart_totals(cart)
    
    return {
        "success": True,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "cart_count": cart_count
    }

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Chi tiết sản phẩm"""
   
    product = next((p for p in products_list if p['id'] == product_id), None)
    if not product:
        return render_template('404.html'), 404
    
    related_products = [p for p in products_list if p['category'] == product['category'] and p['id'] != product_id][:4]
    return render_template('product_detail.html', product=product, related_products=related_products)
@app.context_processor
def inject_cart_count():
    cart = session.get('cart', [])
    # Cộng dồn số lượng của tất cả các món trong giỏ
    cart_count = sum(item.get('quantity', 1) for item in cart)
    return dict(cart_count=cart_count)
if __name__ == '__main__':
    app.run(debug=True)