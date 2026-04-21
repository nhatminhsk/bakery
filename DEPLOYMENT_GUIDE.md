# Multi-Store System - Deployment & Operations Guide

**Version:** 1.0  
**Date:** April 2026  
**System:** BubbleBakery Multi-Store Management System

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Deployment Checklist](#deployment-checklist)
4. [Configuration](#configuration)
5. [User Management](#user-management)
6. [Operations Guide](#operations-guide)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

The Multi-Store System enables BubbleBakery to manage multiple bakery locations with:
- **Centralized Admin Dashboard** - View and manage all stores from one place
- **Store-Specific Staff Access** - Each store has dedicated staff who see only their store's data
- **Role-Based Authorization** - Admin, Staff, and Customer roles with store context
- **Unified Analytics** - Per-store and company-wide reporting

### Key Features

✅ **Store Management**
- Create and manage multiple store locations
- Store-specific settings (delivery fees, payment methods, etc.)
- Active/inactive store toggling

✅ **Staff Assignment**
- One staff member per store (1:1 relationship)
- Automatic store-level data filtering
- Cross-store access prevention

✅ **Admin Controls**
- View all stores' data
- Filter dashboard by specific store
- Store-level order and product management

✅ **Data Isolation**
- Products belong to specific stores
- Orders tagged by store_id
- Tasks can be store-specific or company-wide

---

## Architecture

### Database Schema

```
Stores Table
├── id (Primary Key)
├── name (Store name)
├── code (Unique code: STORE_001, STORE_002, etc.)
├── address (Physical location)
├── phone, email
├── is_active (Boolean)
└── created_at

StoreStaff Table (1:1 Relationship)
├── id
├── store_id (UNIQUE Foreign Key)
├── user_id (UNIQUE Foreign Key)
├── assigned_at
└── is_active

StoreSettings Table
├── id
├── store_id (Foreign Key)
├── delivery_base_fee
├── free_shipping_min
├── delivery_eta
├── same_day_delivery
├── payment_methods
└── updated_at

Products Table
├── id
├── name
├── store_id (FK) - Products belong to stores
├── price
├── category_id
└── ... (other product fields)

Orders Table
├── id
├── store_id (FK) - Orders belong to stores
├── user_id
├── total
├── status
├── created_at
└── ... (other order fields)

AdminTodos Table
├── id
├── store_id (FK) - NULL = company-wide, specific ID = store task
├── title
├── status
└── ... (other task fields)
```

### Authorization Model

```
ADMIN Role
└─ Can access: ALL STORES
   └─ Dashboard: Global view or filter by store_id parameter
   └─ Products: All stores or ?store_id=N
   └─ Orders: All stores or ?store_id=N
   └─ Reports: Company-wide or per-store

STAFF Role
└─ Can access: THEIR ASSIGNED STORE ONLY
   └─ Dashboard: Only their store's data
   └─ Products: Only their store's products
   └─ Orders: Only their store's orders
   └─ Tasks: Their store + company-wide tasks (store_id=NULL)
   └─ Prevents: Cross-store access (validated at service layer)

CUSTOMER Role
└─ Can access: THEIR OWN DATA ONLY
   └─ Orders: Their orders
   └─ Account: Their profile
   └─ Products: Public product listing
```

### Service Layer Pattern

All service functions accept optional `store_id` parameter:

```python
# Admin services (app/admin/services.py)
get_dashboard_stats(store_id=None)  # None=all stores, 1=store 1 only
get_all_products_admin(store_id=None)
get_orders_management_data(store_id=None)
get_revenue_by_month(store_id=None)

# Staff services (app/staff/services.py)
get_staff_dashboard_data(user_id=current_user.id)  # Extracts user's store
get_staff_orders_data(user_id=current_user.id)      # Automatic filtering
get_staff_inventory_products(user_id=current_user.id)
```

---

## Deployment Checklist

### Pre-Deployment (Phase 1-4 Verification)

- [ ] **Database Migration Applied**
  ```bash
  cd d:\QLDA\bakery
  flask db upgrade
  ```
  - Verify revision: f1627b613e04 or later
  - Check stores table exists
  - Verify all products/orders have store_id

- [ ] **Default Store Created**
  ```bash
  # After migration, default store should exist
  # ID: 1, Name: BubbleBakery, Code: STORE_001
  python -c "from app.models.store import Store; from app.extensions import db; from app import create_app; app = create_app('development'); db.init_app(app); print('Default store:', Store.query.get(1))"
  ```

- [ ] **Python Environment**
  ```bash
  pip list | grep -E "Flask|SQLAlchemy|flask-migrate"
  ```

- [ ] **Configuration Files**
  - Check config/development.py, production.py
  - Ensure SQLALCHEMY_DATABASE_URI is correct

### Deployment

1. **Backup Production Database**
   ```bash
   cp instance/bakery_prod.db instance/bakery_prod.db.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. **Stop Current Application**
   ```bash
   # Kill running Flask process
   ```

3. **Deploy Code**
   ```bash
   cd d:\QLDA\bakery
   git pull origin main  # or your deployment method
   ```

4. **Apply Migrations**
   ```bash
   flask db upgrade --sql  # Review changes
   flask db upgrade        # Apply
   ```

5. **Verify Schema**
   ```bash
   python test_phase5_integration.py
   ```

6. **Start Application**
   ```bash
   python wsgi.py
   # OR with Gunicorn
   gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
   ```

7. **Test Access**
   - Admin: Visit `/admin/` - should see store selector
   - Staff: Visit `/staff/` - should see assigned store badge

---

## Configuration

### Store Settings

Each store has customizable settings in StoreSettings table:

```python
store_settings = {
    'store_id': 1,
    'delivery_base_fee': 30000,          # ₫30,000
    'free_shipping_min': 200000,         # ₫200,000
    'delivery_eta': '30-45 min',
    'same_day_delivery': True,
    'payment_cod': True,
    'payment_bank': True,
    'payment_card': True,
    'payment_ewallet': False,
}
```

Update via admin panel or direct database:

```sql
UPDATE store_settings 
SET delivery_base_fee = 25000, free_shipping_min = 150000 
WHERE store_id = 2;
```

### Feature Flags

Enable multi-store filtering:

```python
# In templates
{% if stores and stores|length > 1 %}
    <!-- Show store selector -->
{% endif %}
```

---

## User Management

### Creating a New Store

1. **Via Admin Panel** (if implemented)
   - Navigate to Settings
   - Click "Add Store"
   - Fill: Name, Code (STORE_003), Address, Phone, Email
   - Click Create

2. **Via CLI**
   ```python
   from app import create_app
   from app.models.store import Store
   from app.extensions import db

   app = create_app('production')
   with app.app_context():
       new_store = Store(
           name='BubbleBakery Ha Noi',
           code='STORE_002',
           address='123 Tran Hung Dao, Ha Noi',
           phone='024-1234-5678',
           email='hanoi@bubble.vn',
           is_active=True
       )
       db.session.add(new_store)
       db.session.commit()
       print(f"Store created: {new_store.id}")
   ```

### Assigning Staff to Store

1. **Via Admin Panel**
   - Navigate to Accounts / Staff Management
   - Search for user
   - Click "Assign to Store"
   - Select store from dropdown
   - Confirm

2. **Via CLI**
   ```python
   from app.models.store import StoreStaff
   from app.models.user import User
   from app.extensions import db

   staff_user = User.query.filter_by(username='john_staff').first()
   store_id = 2

   assignment = StoreStaff(user_id=staff_user.id, store_id=store_id)
   db.session.add(assignment)
   db.session.commit()
   ```

   **Note:** Due to UNIQUE constraints, a staff member can only be assigned to one store.

### Removing Staff from Store

```python
assignment = StoreStaff.query.filter_by(user_id=user_id).delete()
db.session.commit()
```

---

## Operations Guide

### Admin Dashboard

**Access:** `http://localhost:5000/admin/`

**Features:**
- **Store Selector (Header)** - Dropdown to filter by store
  - "Tất Cả Cửa Hàng" = Company-wide view
  - Select specific store = Store-specific view
  
- **Dashboard View**
  - Total Products, Orders, Revenue
  - Pending Orders count
  - Recent orders list
  
- **Products Page** (`/admin/products?store_id=1`)
  - Add/Edit/Delete products for store
  - Inventory management
  - Stock alerts
  
- **Orders Page** (`/admin/orders?store_id=1`)
  - Filter orders by store
  - Update order status
  - View order details
  
- **Reports** (`/admin/overview?store_id=1`)
  - Revenue by store
  - Top products per store
  - Order trends

### Staff Dashboard

**Access:** `http://localhost:5000/staff/`

**Features:**
- **Store Badge (Header)** - Displays assigned store name
  - Example: 🏪 BubbleBakery HCM
  - Non-removable (confirms isolation)
  
- **Dashboard View**
  - Their store's statistics only
  - Recent orders for their store
  - Tasks (store-specific + company-wide)
  
- **Orders** (`/staff/orders`)
  - Only their store's orders
  - Cannot see other stores' orders
  - Cannot update status for other stores' orders
  
- **Inventory** (`/staff/inventory`)
  - Products in their store
  - Stock management
  - Expiry alerts
  
- **Tasks** (`/staff/todos`)
  - Store-specific tasks
  - Company-wide tasks (store_id=NULL)

### Monitoring & Alerts

**Key Metrics to Monitor:**

1. **Store Activity**
   ```sql
   -- Orders per store (today)
   SELECT store_id, COUNT(*) as order_count
   FROM orders
   WHERE DATE(created_at) = DATE('now')
   GROUP BY store_id;
   ```

2. **Staff Access**
   ```sql
   -- Check staff assignments
   SELECT u.username, s.name as store_name
   FROM store_staff ss
   JOIN users u ON ss.user_id = u.id
   JOIN stores s ON ss.store_id = s.id
   WHERE ss.is_active = TRUE;
   ```

3. **Revenue by Store (Monthly)**
   ```sql
   -- Revenue by store and month
   SELECT 
       s.name,
       strftime('%Y-%m', o.created_at) as month,
       SUM(o.total) as revenue
   FROM orders o
   JOIN stores s ON o.store_id = s.id
   WHERE o.status = 'delivered'
   GROUP BY s.id, month;
   ```

---

## Testing

### Automated Tests

Run comprehensive test suite:

```bash
# Phase 3 - Route & Authorization
python test_phase3.py

# Phase 4 - UI & Dashboard
python test_phase4.py

# Phase 5 - Integration Tests (E2E)
python test_phase5_integration.py
```

### Manual Testing

**Test 1: Admin Store Filtering**
1. Login as admin
2. Visit `/admin/`
3. See store selector in header
4. Select specific store → verify dashboard shows only that store's data
5. Select "Tất Cả Cửa Hàng" → verify company-wide data

**Test 2: Staff Store Access**
1. Login as staff user
2. Visit `/staff/`
3. Verify store badge shows in header
4. Verify all data is from assigned store only
5. Try accessing `/admin/` → should be denied (401)

**Test 3: Cross-Store Prevention**
1. As admin, go to Staff → Orders
2. Get order_id from Store 1
3. Login as staff from Store 2
4. Try `/staff/orders/{order_id}/status` → should get error "You cannot access this order"

**Test 4: Order Workflow**
1. Create order in Store 1 (admin)
2. Staff from Store 1 sees it in `/staff/orders`
3. Staff from Store 2 cannot see it
4. Admin can see it in both views (filtered and all)

**Test 5: Revenue Reports**
1. Admin → Dashboard → `/admin/?store_id=1` shows Store 1 revenue
2. Admin → Dashboard → `/admin/?store_id=2` shows Store 2 revenue
3. Admin → Dashboard → `/admin/` shows total revenue all stores

---

## Troubleshooting

### Issue: Staff not seeing their data

**Symptoms:**
- Staff visits `/staff/` but sees empty dashboard
- Orders page shows 0 orders
- Store badge shows "None"

**Diagnosis:**
1. Check StoreStaff assignment exists
   ```sql
   SELECT * FROM store_staff WHERE user_id = ?;
   ```
2. Verify store_id is valid
   ```sql
   SELECT * FROM stores WHERE id = ?;
   ```

**Solution:**
1. Assign staff to store via CLI or admin panel
2. If migration failed, re-run: `flask db upgrade`

### Issue: Admin store selector not showing

**Symptoms:**
- Store selector dropdown not visible in header
- All stores data visible but no filtering option

**Diagnosis:**
1. Check `get_all_stores()` function in admin/routes.py
2. Verify stores list passed to template
3. Check template has `{% if stores and stores|length > 1 %}`

**Solution:**
1. Verify admin base template updated: `Templates/admin/base.html`
2. Check route passes `stores=stores` to template
3. Ensure multiple stores exist in database

### Issue: Orders appearing in wrong store

**Symptoms:**
- Order shows in multiple stores
- Staff sees orders from other stores

**Diagnosis:**
```sql
-- Check all orders have correct store_id
SELECT id, store_id FROM orders WHERE store_id IS NULL;
```

**Solution:**
1. Backfill missing store_id:
   ```sql
   UPDATE orders SET store_id = 1 WHERE store_id IS NULL;
   ```
2. Add NOT NULL constraint if needed
3. Re-run migration if database reset required

### Issue: Cross-store access not prevented

**Symptoms:**
- Staff can access other stores' data
- Authorization check not working

**Diagnosis:**
1. Check `update_staff_order_status()` in staff/services.py
2. Verify `check_store_access()` called before update
3. Check current_user is staff role

**Solution:**
1. Verify staff/routes.py passes `user_id=current_user.id`
2. Check staff/services.py has store access validation
3. Restart Flask to reload code

### Issue: "You cannot access this order" error

**Symptoms:**
- Legitimate staff access denied
- Error: "You cannot access this order"

**Diagnosis:**
1. Check staff's store assignment:
   ```sql
   SELECT ss.store_id FROM store_staff ss WHERE ss.user_id = ?;
   ```
2. Check order's store_id:
   ```sql
   SELECT store_id FROM orders WHERE id = ?;
   ```

**Solution:**
- If staff store ID ≠ order store ID: Error is correct, move order or reassign staff
- If they match: Check code has recent changes, restart Flask

---

## Performance Considerations

### Indexing

Ensure these columns are indexed:

```sql
-- Already present in schema
CREATE INDEX idx_products_store_id ON products(store_id);
CREATE INDEX idx_orders_store_id ON orders(store_id);
CREATE INDEX idx_store_staff_user_id ON store_staff(user_id);
CREATE INDEX idx_store_staff_store_id ON store_staff(store_id);
CREATE INDEX idx_admin_todos_store_id ON admin_todos(store_id);
```

### Query Optimization

Services use filtering at query level (efficient):
```python
# Good: Filter in SQL query
Order.query.filter_by(store_id=store_id).all()

# Less efficient: Filter in Python
[o for o in Order.query.all() if o.store_id == store_id]
```

### Caching Strategies

For frequently accessed data:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300, key_prefix='store_1_stats')
def get_dashboard_stats(store_id=1):
    # Cached for 5 minutes
    return ...
```

---

## Support & Maintenance

### Backup Strategy

```bash
# Daily backup
*/0 3 * * * cp /path/bakery_prod.db /backups/bakery_prod.db.$(date +\%Y\%m\%d)

# Cleanup old backups (keep 30 days)
find /backups -name "bakery_prod.db.*" -mtime +30 -delete
```

### Log Monitoring

```bash
# Flask logs
tail -f logs/app.log | grep -E "ERROR|WARNING"

# Database logs (SQLite)
# Check app logs for VACUUM operations
```

### Security Checklist

- [ ] All staff users have unique assignments (1:1 per store)
- [ ] Admin-only routes use `@admin_required` decorator
- [ ] Staff routes use `@staff_required` decorator
- [ ] Cross-store access checks in place (services layer)
- [ ] `current_user` context verified in all routes
- [ ] Session timeout configured appropriately
- [ ] Database credentials not in code
- [ ] HTTPS enabled in production

---

## Rollback Procedure

If multi-store deployment fails:

1. **Stop Application**
   ```bash
   # Kill Flask process
   ```

2. **Restore Database**
   ```bash
   cp instance/bakery_prod.db.backup instance/bakery_prod.db
   ```

3. **Revert Code**
   ```bash
   git checkout <previous-stable-commit>
   ```

4. **Clear Cache**
   ```bash
   rm -rf __pycache__ app/__pycache__ instance/bakery.db
   ```

5. **Restart**
   ```bash
   python wsgi.py
   ```

---

## Contact & Support

- **Admin Issues:** Check admin dashboard logs, run `test_phase4.py`
- **Staff Access:** Verify StoreStaff assignments, check store badge
- **Data Issues:** Run `test_phase5_integration.py` for diagnosis
- **Database Issues:** Check migration version with `flask db current`

---

**End of Documentation**

Version 1.0 | April 2026 | Multi-Store System Deployment Guide
