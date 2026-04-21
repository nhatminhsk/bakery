# 📊 ĐỀ XUẤT: Từ Single-Store → Multi-Store Architecture

**Ngày**: 19/04/2026 | **Scope**: Database, Business Logic, Authorization

---

## I. TÌNH TRẠNG HIỆN TẠI (Single-Store)

```
Hiện tại:
└─ 1 BubbleBakery Store
   ├─ 1 danh sách sản phẩm chung
   ├─ N nhân viên (không gắn cửa hàng)
   ├─ N đơn hàng (không biết từ cửa hàng nào)
   └─ Thống kê doanh số = toàn bộ hệ thống
```

**Vấn đề:**
- ❌ Không thể phân biệt doanh số cửa hàng A vs B
- ❌ Nhân viên cửa hàng B thấy sản phẩm/đơn của cửa hàng A
- ❌ Tồn kho không tách biệt theo cửa hàng
- ❌ Admin không thể quản lý từng cửa hàng độc lập

---

## II. KIẾN TRÚC DB ĐỀ XUẤT (Multi-Store)

### A. Bảng Mới: `stores`

```python
class Store(db.Model):
    __tablename__ = 'stores'
    
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False)  # "Chi nhánh Quận 1"
    code            = db.Column(db.String(20), unique=True)      # "STORE_001"
    address         = db.Column(db.String(255))
    phone           = db.Column(db.String(30))
    email           = db.Column(db.String(120))
    manager_id      = db.Column(db.Integer, db.ForeignKey('users.id'))  # Store manager
    
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products        = db.relationship('Product', backref='store', lazy=True)
    staff           = db.relationship('StoreStaff', backref='store', lazy=True, cascade='all, delete-orphan')
    orders          = db.relationship('Order', backref='store', lazy=True)
    settings        = db.relationship('StoreSetting', backref='store', lazy=True, cascade='all, delete-orphan')
```

### B. Bảng Mới: `store_staff` (Staff Assignment)

```python
class StoreStaff(db.Model):
    __tablename__ = 'store_staff'
    
    id              = db.Column(db.Integer, primary_key=True)
    store_id        = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role            = db.Column(db.String(30))  # 'manager' | 'staff'
    position        = db.Column(db.String(50))  # "Kho trưởng", "Thu ngân", v.v.
    
    assigned_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_active       = db.Column(db.Boolean, default=True)
    
    __table_args__ = (
        db.UniqueConstraint('store_id', 'user_id', name='uq_store_staff'),
    )

    user = db.relationship('User', backref='store_assignments')
```

### C. Bảng Mới: `store_settings`

```python
class StoreSetting(db.Model):
    __tablename__ = 'store_settings'
    
    id              = db.Column(db.Integer, primary_key=True)
    store_id        = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    
    # Cấu hình độc lập theo cửa hàng
    delivery_base_fee    = db.Column(db.Integer, default=20000)
    free_shipping_min    = db.Column(db.Integer, default=50000)
    delivery_eta         = db.Column(db.String(50), default='24 giờ')
    same_day_delivery    = db.Column(db.Boolean, default=False)
    
    # Chính sách thanh toán
    payment_cod          = db.Column(db.Boolean, default=True)
    payment_bank         = db.Column(db.Boolean, default=False)
    
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### D. Thay Đổi: Bảng `products`

```python
class Product(db.Model):
    __tablename__ = 'products'
    
    id              = db.Column(db.Integer, primary_key=True)
    store_id        = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)  # ← THÊM
    
    name            = db.Column(db.String(120), nullable=False)
    price           = db.Column(db.Integer)
    category        = db.Column(db.String(80))
    in_stock        = db.Column(db.Integer, default=0)
    cost_price      = db.Column(db.Integer, default=0)
    # ... rest
    
    # Index để tăng tốc độ query
    __table_args__ = (
        db.Index('idx_store_product', 'store_id', 'is_active'),
    )
```

### E. Thay Đổi: Bảng `orders`

```python
class Order(db.Model):
    __tablename__ = 'orders'
    
    id              = db.Column(db.Integer, primary_key=True)
    store_id        = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)  # ← THÊM
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    status          = db.Column(db.String(30), default='pending')
    total           = db.Column(db.Integer, default=0)
    shipping_fee    = db.Column(db.Integer, default=0)
    
    # Index
    __table_args__ = (
        db.Index('idx_store_order', 'store_id', 'created_at'),
        db.Index('idx_user_order', 'user_id', 'created_at'),
    )
```

### F. Thay Đổi: Bảng `product_batches`

```python
class ProductBatch(db.Model):
    __tablename__ = 'product_batches'
    
    id              = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey('products.id'))
    store_id        = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)  # ← THÊM
    
    quantity        = db.Column(db.Integer)
    expiry_date     = db.Column(db.Date)
```

### G. Thay Đổi: Bảng `admin_todos`

```python
class AdminTodo(db.Model):
    __tablename__ = 'admin_todos'
    
    id              = db.Column(db.Integer, primary_key=True)
    store_id        = db.Column(db.Integer, db.ForeignKey('stores.id'))  # NULL = cho toàn công ty
    
    title           = db.Column(db.String(255))
    priority        = db.Column(db.String(20))
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Nếu store_id NULL = admin task (toàn công ty)
    # Nếu store_id = X = task cho store X
```

---

## III. THAY ĐỔI NHÂN SỰ & PHÂN QUYỀN

### A. User Role → Mở Rộng

**Hiện tại:**
```python
role = 'customer' | 'staff' | 'admin'
```

**Mới - Multi-level Permission:**
```python
# Level 1: Global Role
user.role = 'customer' | 'staff' | 'manager' | 'admin'

# Level 2: Store Assignment (StoreStaff)
store_staff.role = 'store_manager' | 'staff'
store_staff.store_id = 1  # Gắn vào Store nào

# Ví dụ:
User(id=5, role='staff')
  ├─ StoreStaff(store_id=1, role='store_manager')    # Quản lý Store 1
  └─ StoreStaff(store_id=2, role='staff')             # Nhân viên Store 2
```

### B. Authorization Logic (Permission Middleware)

```python
@require_store_access('store_id_param')
def get_store_orders(store_id):
    """Chỉ staff/manager của store này mới được truy cập"""
    # Middleware sẽ check:
    # 1. current_user.role == 'admin' → Được (toàn bộ)
    # 2. current_user có StoreStaff(store_id=X) → Được
    # 3. Không thỏa → 403 Forbidden
```

### C. Dashboard Theo Cửa Hàng

**Hiện tại (Global):**
```python
stats = {
    'total_orders': 1500,
    'revenue': 50000000,  # Tất cả cửa hàng
}
```

**Mới (Per-Store):**
```python
# Nếu user = manager của Store 1
stats = {
    'store_id': 1,
    'store_name': 'Chi nhánh Quận 1',
    'total_orders': 150,    # Chỉ Store 1
    'revenue': 5000000,     # Chỉ Store 1
}

# Nếu user = admin
stats = [
    {'store_id': 1, 'revenue': 5000000},
    {'store_id': 2, 'revenue': 3000000},
    {'store_id': 3, 'revenue': 2000000},
    {'total': 10000000}
]
```

---

## IV. THAY ĐỔI SẢN PHẨM & TỒN KHO

### A. Catalog Policy

**Tùy chọn 1: Central Catalog (Khuyến cáo)**
```
1 danh sách sản phẩm chung nhưng tồn kho tách biệt

Product (id=1, name='Bánh Kem')
├─ ProductBatch (store_id=1, quantity=50)  # Store 1 có 50 cái
├─ ProductBatch (store_id=2, quantity=30)  # Store 2 có 30 cái
└─ ProductBatch (store_id=3, quantity=0)   # Store 3 hết hàng

Lợi: Quản lý dễ, thống kê chung dễ
Hại: Sự khác biệt về giá khó kiểm soát
```

**Tùy chọn 2: Store-Specific Catalog (Phức tạp)**
```
Mỗi store có danh sách sản phẩm riêng

Product (id=1, store_id=1, name='Bánh Kem Cửa Hàng 1')
Product (id=2, store_id=2, name='Bánh Kem Cửa Hàng 2', price=15000)

Lợi: Tự do giá, sản phẩm
Hại: Khó thống kê, dữ liệu duplicate
```

**→ Khuyến cáo: Tùy chọn 1 (Central Catalog)**

### B. Inventory Management

```python
def get_product_stock(product_id, store_id):
    """Lấy tồn kho sản phẩm tại cửa hàng cụ thể"""
    batch = ProductBatch.query.filter_by(
        product_id=product_id,
        store_id=store_id
    ).first()
    return batch.quantity if batch else 0

def transfer_stock(from_store, to_store, product_id, quantity):
    """Chuyển hàng giữa 2 cửa hàng"""
    from_batch = ProductBatch.query.filter_by(
        store_id=from_store,
        product_id=product_id
    ).first()
    
    if from_batch.quantity >= quantity:
        from_batch.quantity -= quantity
        
        to_batch = ProductBatch.query.filter_by(
            store_id=to_store,
            product_id=product_id
        ).first_or_404()
        to_batch.quantity += quantity
        
        # Log: StockTransferLog(from_store, to_store, quantity, reason)
        db.session.commit()
```

---

## V. THAY ĐỔI NGHIỆP VỤ ĐƠN HÀNG

### A. Order Processing

```python
def create_order(user_id, store_id, cart_items):
    """
    - Cart phải chỉ chứa items từ 1 store
    - Không thể mix sản phẩm từ store khác
    """
    
    # Validate: Tất cả items phải từ cùng 1 store
    products = Product.query.filter_by(store_id=store_id).all()
    for item in cart_items:
        if item['product_id'] not in [p.id for p in products]:
            raise ValueError(f"Sản phẩm {item['product_id']} không thuộc store {store_id}")
    
    order = Order(
        user_id=user_id,
        store_id=store_id,  # ← Gắn order vào store
        total=...,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
```

### B. Order Fulfillment (Multi-Store)

```
Hiện tại:
  Order → [Staff xử lý] → Delivered

Mới:
  Order → [Store1 Staff xử lý] → [Delivery] → Delivered
  
  Nếu order từ Store 2:
  Order → [Store2 Staff xử lý] → [Delivery] → Delivered
  
  ⚠️ Nếu order từ Store 1 nhưng Staff Store 2 đang online:
     → Không thấy được order này (Permission denied)
```

### C. Thống Kê & Reporting

```python
# ❌ CŨNG (Global - không còn dùng)
def get_revenue():
    total = Order.query.filter_by(status='delivered').all()
    return sum(o.total for o in total)

# ✅ MỚI (Per-Store)
def get_store_revenue(store_id, start_date=None, end_date=None):
    """Doanh thu cụ thể 1 cửa hàng"""
    query = Order.query.filter_by(
        store_id=store_id,
        status='delivered'
    )
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    return sum(o.total for o in query.all())

def get_all_stores_revenue():
    """Dashboard CEO: so sánh revenue từng store"""
    stores = Store.query.all()
    return [
        {
            'store_name': s.name,
            'revenue': get_store_revenue(s.id),
            'orders': Order.query.filter_by(store_id=s.id).count(),
            'avg_order': get_store_revenue(s.id) / Order.query.filter_by(store_id=s.id).count(),
        }
        for s in stores
    ]
```

---

## VI. CẬP NHẬT NGÀNH HÀNG/TỔ CHỨC CẤU TRÚC

### A. User Types & Access Levels

| User Type | Truy Cập | Quyền |
|-----------|----------|-------|
| **Customer** | Tất cả cửa hàng | Xem sản phẩm, tạo đơn hàng |
| **Store Staff** | Store gán | Xử lý đơn, quản lý tồn kho của store |
| **Store Manager** | 1 store | Quản lý toàn bộ store: staff, sản phẩm, doanh số |
| **Regional Manager** | Multi-store | Quản lý N store (cấu hình, staff) |
| **Admin (CEO)** | Toàn công ty | Toàn bộ quyền, xem all reports |

### B. New Models

```
Company
├─ Store 1 (Manager A)
│  ├─ Staff B (nhân viên)
│  ├─ Staff C (nhân viên)
│  └─ Products (tồn kho riêng)
├─ Store 2 (Manager D)
│  ├─ Staff E
│  └─ Products (tồn kho riêng)
└─ Store 3 (Manager F)
```

### C. New Admin Pages

```
/admin
├─ Dashboard (Tổng hợp tất cả store)
├─ Stores
│  ├─ List Stores (tạo, chỉnh sửa store)
│  ├─ Store Detail
│  │  ├─ Settings (phí ship, thanh toán)
│  │  ├─ Staff Management
│  │  ├─ Products & Inventory
│  │  └─ Revenue Reports
│  └─ Transfer Stock (chuyển hàng)
├─ Users
│  ├─ User Management
│  └─ Store Assignment (gán user → store)
└─ Reports
   ├─ Revenue by Store
   ├─ Orders by Store
   ├─ Staff Performance
   └─ Inventory Status
```

---

## VII. MIGRATION STRATEGY (5 Phase)

### Phase 1: Database (Week 1)
- ✅ Tạo bảng `stores`, `store_staff`, `store_settings`
- ✅ Thêm column `store_id` vào `products`, `orders`, `product_batches`, `admin_todos`
- ✅ Data migration: Gán tất cả record hiện tại → `store_id=1` (Default Store)
- ✅ Test queries, migrations

### Phase 2: Backend (Week 1-2)
- ✅ Tạo Store CRUD service
- ✅ Tạo StoreStaff assignment service
- ✅ Cập nhật authorization middleware
- ✅ Cập nhật product/order/inventory services
- ✅ Unit tests

### Phase 3: Frontend Admin (Week 2-3)
- ✅ Admin Store Management UI
- ✅ Staff Assignment UI
- ✅ Per-Store Settings UI
- ✅ Per-Store Dashboard

### Phase 4: Frontend Staff/Customer (Week 3)
- ✅ Staff Panel → Hiển thị chỉ đơn từ store của họ
- ✅ Customer → Có thể chọn mua từ store nào
- ✅ Order history → Hiển thị store info

### Phase 5: Testing & Rollout (Week 4)
- ✅ Integration tests
- ✅ UAT
- ✅ Soft launch (1 store test)
- ✅ Full rollout

---

## VIII. RỦI RO & MITIGATION

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Data loss / wrong migration | 🔴 CRITICAL | Backup DB trước, test migration script |
| Permission bug (staff thấy đơn khác store) | 🔴 CRITICAL | Strict unit test, code review |
| Existing order không có store_id | 🔴 HIGH | Batch update + verify |
| Performance (thêm JOIN → chậm) | 🟠 MEDIUM | Thêm index, caching, load test |
| Customer confusion (UI change) | 🟠 MEDIUM | In-app tutorial, notification |
| Support load (staff đơn hàng missing) | 🟡 LOW | Phần cứng doc, training |

---

## IX. IMPLEMENTATION ESTIMATE

| Component | Effort | Notes |
|-----------|--------|-------|
| DB Design & Migration | 1w | Không phức tạp, có plan rõ |
| Backend Services | 2w | Cập nhật logic, authorization |
| Admin UI | 1.5w | Store CRUD, dashboards |
| Staff/Customer UI | 1w | Đơn, tồn kho, order history |
| Testing & QA | 1w | Integration tests, UAT |
| **TOTAL** | **6.5w** | ~1.5 months |

---

## X. SQL SCHEMA MIGRATION EXAMPLES

```sql
-- 1. Tạo bảng stores
CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(20) UNIQUE,
    address VARCHAR(255),
    manager_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(id)
);

-- 2. Thêm store_id vào products
ALTER TABLE products ADD COLUMN store_id INTEGER;
ALTER TABLE products ADD CONSTRAINT fk_product_store FOREIGN KEY (store_id) REFERENCES stores(id);

-- 3. Insert default store (backward compat)
INSERT INTO stores (id, name, code) VALUES (1, 'BubbleBakery Main', 'STORE_001');

-- 4. Update tất cả product → store 1
UPDATE products SET store_id = 1 WHERE store_id IS NULL;

-- 5. Tạo bảng store_staff
CREATE TABLE store_staff (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    store_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(30),
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY (store_id, user_id)
);

-- 6. Migrate staff từ user.role='staff' → store_staff
INSERT INTO store_staff (store_id, user_id, role)
SELECT 1, id, 'staff'
FROM users
WHERE role = 'staff' AND is_active = TRUE;
```

---

## XI. BENEFITS

✅ **Scalability**: Mở rộng sang 10, 100 cửa hàng dễ dàng  
✅ **Control**: Mỗi store có settings riêng (phí ship, sản phẩm)  
✅ **Security**: Staff chỉ thấy data store của họ  
✅ **Analytics**: So sánh hiệu năng từng store  
✅ **Autonomy**: Store managers độc lập quản lý  
✅ **Scalability**: Chuẩn bị cho future POS integration, franchise

---

## XII. NEXT STEPS

1. **Approve** kiến trúc này
2. **Start** Phase 1 (DB migration)
3. **Create** detailed task breakdown
4. **Setup** dev/test environment
5. **Begin** Phase 2 (Backend)

---

**Questions?** Hỏi về chi tiết bất kỳ phần nào.
