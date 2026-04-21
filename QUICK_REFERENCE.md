# Multi-Store System - Quick Reference

## Admin Quick Guide

### Store Management
| Task | Steps |
|------|-------|
| **View all stores** | Dashboard > Store selector shows list |
| **Focus on one store** | Dashboard > Store selector > Select store |
| **View company-wide** | Store selector > "Tất Cả Cửa Hàng" |
| **Add store** | Settings > Stores > Add New (if available) |

### Product Management
| Task | Steps |
|------|-------|
| **View products** | Sản Phẩm > Select store from dropdown |
| **Add product** | Sản Phẩm > Add > Fill form > Save |
| **Edit product** | Sản Phẩm > Find product > Edit |
| **Delete product** | Sản Phẩm > Find product > Delete |
| **Bulk update prices** | Sản Phẩm > Select multiple > Update price |

### Order Management
| Task | Steps |
|------|-------|
| **View orders** | Quản Lý Đơn Hàng > Select store |
| **Update order status** | Click order > Change Status > Select new > Save |
| **View order details** | Click order in list |
| **Print invoice** | Click order > Print Invoice |

### Staff Management
| Task | Steps |
|------|-------|
| **Assign staff to store** | Quản Lý Tài Khoản > Find staff > Assign to Store |
| **View all staff** | Quản Lý Tài Khoản > List shows all |
| **Change staff role** | Quản Lý Tài Khoản > Find staff > Change Role |

### Task Management
| Task | Steps |
|------|-------|
| **Create company task** | Công Việc > Add > Leave store field BLANK |
| **Create store task** | Công Việc > Add > Select store |
| **View all tasks** | Công Việc > List shows all |
| **Assign task to staff** | Công Việc > Find task > Assign staff |

### Reports
| Task | Steps |
|------|-------|
| **Daily revenue** | Tổng Quan > Select date (Today) > Select store |
| **Monthly revenue** | Tổng Quan > Select date (Month) > Select store |
| **Top products** | Tổng Quan > Shows top 5 for selected store |
| **Compare stores** | Dashboard > Store selector > Compare each store |

---

## Staff Quick Guide

### Dashboard
| Task | Steps |
|------|-------|
| **View my data** | Click Dashboard (automatic store filter) |
| **My store name** | Check green badge at top left 🏪 |
| **View my orders today** | Dashboard shows recent orders |
| **View my tasks** | Dashboard shows assigned tasks |

### Order Management
| Task | Steps |
|------|-------|
| **View my orders** | Đơn Hàng > All orders shown |
| **Update order status** | Click order > Change Status > Select new |
| **Print receipt** | Click order > Print Invoice |
| **Contact customer** | Click order > Show contact info |

### Inventory
| Task | Steps |
|------|-------|
| **Check stock** | Kho Hàng > See all products with quantities |
| **Low stock alerts** | Products highlighted if stock < threshold |
| **Update quantity** | Click product > Update Stock > Add/Remove |

### Feedback
| Task | Steps |
|------|-------|
| **View customer reviews** | Phản Hồi > All reviews for your store |
| **Filter by rating** | Phản Hồi > Click ⭐⭐⭐⭐⭐ to filter |
| **Reply to review** | Click review > Phản Hồi > Type reply > Send |

### Tasks
| Task | Steps |
|------|-------|
| **View my tasks** | Công Việc > Shows store + company tasks |
| **Mark task done** | Click task > Mark Complete |
| **See task details** | Click task to expand |

---

## Role Permissions Matrix

| Feature | Admin | Staff | Customer |
|---------|-------|-------|----------|
| View own store | ✅ All | ✅ Assigned only | - |
| View other stores | ✅ | ❌ | - |
| Add products | ✅ | ❌ | - |
| Edit products | ✅ | ❌ | - |
| Delete products | ✅ | ❌ | - |
| View all orders | ✅ | ✅ (own store) | ✅ (own only) |
| Update order status | ✅ | ✅ (own store) | ❌ |
| View analytics | ✅ (all/by store) | ✅ (own store) | ❌ |
| Create tasks | ✅ | ❌ | ❌ |
| Assign staff | ✅ | ❌ | - |
| View staff list | ✅ | ❌ | - |

---

## Store Selector - Admin Only

Located in header right side: `🏪 Cửa Hàng: [Dropdown ▼]`

**Options:**
```
Tất Cả Cửa Hàng          (All stores - company view)
├─ BubbleBakery HCM      (Store 1 - specific view)
├─ BubbleBakery Hà Nội   (Store 2 - specific view)
└─ BubbleBakery Đà Nẵng  (Store 3 - specific view)
```

**Behavior:**
- Selecting store → Dashboard filters to that store only
- Selecting "Tất Cả" → Dashboard shows company-wide data
- Changes apply instantly (no page reload needed)
- Selection persists while you navigate

---

## Staff Store Badge - Staff Only

Located in header left: `🏪 BubbleBakery HCM`

**What it shows:**
- Your assigned store name
- Visual confirmation of store isolation

**Note:** Badge cannot be changed by staff (admin must reassign)

---

## Common Status Codes

### Order Status
```
Pending       - New order, not yet processed
Processing    - Staff is preparing
Shipped       - Sent to customer
Delivered     - Customer received
Cancelled     - Order cancelled
```

### Task Priority
```
High   - 🔴 Must complete ASAP
Normal - 🟡 Regular priority
Low    - 🟢 Can be done later
```

---

## Error Messages & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "You cannot access this order" | Trying to view other store's order | Only view your store's orders |
| "Store not found" | Store ID doesn't exist | Refresh page or contact admin |
| "Permission denied" | Don't have access level | Check your role (admin/staff) |
| "Product not updated" | Network error | Try again or contact support |
| "Store selector not showing" | Only 1 store exists | Add more stores (admin only) |

---

## Keyboard Shortcuts

```
Ctrl + S     Save current form
Ctrl + Q     Quick search (orders)
Esc          Close dialog/modal
Ctrl + K     Command palette (if enabled)
```

---

## Dashboard Widgets

### Admin Dashboard Shows:
- 📊 Total Products (all/store)
- 📦 Total Orders (all/store)
- 🕐 Pending Orders (all/store)
- 💰 Revenue (all/store)
- 📈 Trends chart
- 🏆 Top Products

### Staff Dashboard Shows:
- 📊 My store products count
- 📦 My store orders count
- 🕐 My store pending orders
- 💰 My store revenue
- 📋 My tasks
- 🔔 Recent notifications

---

## Store Data Isolation

Staff can ONLY see:
```
✅ Their assigned store's data
✅ Company-wide tasks (no store)
❌ Other stores' data
❌ Other stores' orders
❌ Other stores' products
```

Admin CAN see:
```
✅ All stores' data
✅ Company-wide view
✅ Individual store views
✅ Filtered by any store
```

---

## Color Coding

| Color | Meaning | Where |
|-------|---------|-------|
| 🟢 Green | Active/Success | Store badge, success messages |
| 🟡 Yellow | Pending/Warning | Pending orders, warnings |
| 🔴 Red | Error/High | Errors, high priority tasks |
| 🔵 Blue | Info | Information messages |

---

## Useful URLs (Bookmarks)

```
Admin Dashboard:    /admin/
Admin by Store:     /admin/?store_id=1
Staff Dashboard:    /staff/
Products:          /admin/products
Orders:            /admin/orders
Staff Orders:      /staff/orders
Tasks:             /admin/todos or /staff/todos
Accounts:          /admin/accounts
Settings:          /admin/settings
```

---

## Data Flow

```
Customer places order
        ↓
Order goes to assigned store (store_id tagged)
        ↓
Staff in that store sees order (auto-filtered)
        ↓
Staff updates status → Customer sees update
        ↓
Admin can see all stores' orders
        ↓
Staff from other store CANNOT see this order
```

---

## Multi-Store Architecture

```
BubbleBakery (Company)
├─ Store 1 (HCM)
│  ├─ Staff: John, Jane
│  ├─ Products: 20 items
│  └─ Orders: 500+
├─ Store 2 (Hà Nội)
│  ├─ Staff: Mike
│  ├─ Products: 25 items
│  └─ Orders: 300+
└─ Store 3 (Đà Nẵng)
   ├─ Staff: Sarah
   ├─ Products: 15 items
   └─ Orders: 200+

Admin can see everything
Each Staff sees only their store
Customers see all public products
```

---

## Support Resources

- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **User Manual:** `USER_OPERATIONS_MANUAL.md`
- **This Guide:** `QUICK_REFERENCE.md`

For detailed information, see the full manuals.

---

**Multi-Store System v1.0** | Quick Reference | April 2026
