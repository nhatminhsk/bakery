# Multi-Store System - User Operations Manual

**For:** Admins and Staff Users  
**Version:** 1.0  
**Last Updated:** April 2026

---

## Table of Contents

1. [Admin User Guide](#admin-user-guide)
2. [Staff User Guide](#staff-user-guide)
3. [Common Tasks](#common-tasks)
4. [FAQ](#faq)

---

## Admin User Guide

### What Can Admins Do?

✅ **View all stores' data** - Sales, products, orders, feedback  
✅ **Filter by specific store** - Focus on one location at a time  
✅ **Manage all products** - Add, edit, delete across all stores  
✅ **Manage all orders** - Accept, process, cancel orders from any store  
✅ **View company-wide reports** - Revenue, top products, trends  
✅ **Assign staff to stores** - 1 staff per store relationship  
✅ **Create company-wide tasks** - Visible to all staff  

### Admin Dashboard

**Access:** Click the BubbleBakery logo or visit `/admin/`

#### Header Navigation
```
[Dashboard] [Tổng Quan] [Quản Lý Đơn Hàng] [Sản Phẩm]
            [Công Việc]  [Phản Hồi]       [Quản Lý Tài Khoản] [Cài Đặt]
```

#### Store Selector (Header Right)
```
🏪 Cửa Hàng: [Dropdown showing "Tất Cả Cửa Hàng" ▼]
```

**Options:**
- **Tất Cả Cửa Hàng** - Company-wide view (default)
- **BubbleBakery HCM** - Filter to HCM store only
- **BubbleBakery Hà Nội** - Filter to Hà Nội store only
- etc.

### Key Admin Tasks

#### 1. View Dashboard by Store

1. Click **Dashboard** in sidebar
2. Click store selector dropdown in header
3. Select **Cửa Hàng muốn xem** (store to view)
4. Dashboard instantly shows:
   - Products count in that store
   - Orders count for that store
   - Revenue for that store
   - Pending orders in that store

#### 2. Manage Products by Store

1. Click **Sản Phẩm** in sidebar
2. Select store from dropdown (or leave as "Tất Cả" for all)
3. Can now:
   - **Add Product** - Will be added to selected store
   - **Edit Product** - Change price, stock, images
   - **Delete Product** - Remove from that store
   - **Bulk Actions** - Set price for multiple products

#### 3. Process Orders by Store

1. Click **Quản Lý Đơn Hàng** in sidebar
2. Select store from dropdown
3. View all orders for that store:
   - **Status Filter** - Latest, Pending, Delivered, Cancelled
   - **Date Filter** - Today, This Week, This Month
4. Click order to:
   - View full details
   - See customer info
   - Update status (Pending → Processing → Shipped → Delivered)
   - Print receipt or invoice

#### 4. View Revenue Reports by Store

1. Click **Tổng Quan** in sidebar
2. Select time period:
   - Today
   - This Week
   - This Month
   - Custom Date Range
3. Select store from dropdown
4. View:
   - Total revenue for period
   - Top 5 products by sales
   - Order count
   - Customer count
   - Charts and trends

#### 5. Manage Staff Assignments

1. Click **Quản Lý Tài Khoản** in sidebar
2. Search for staff member
3. Click **Assign to Store**
4. Select store from dropdown
5. Confirm assignment

**Important:** Each staff member can only be assigned to ONE store.

#### 6. Create Company-Wide Tasks

1. Click **Công Việc** in sidebar
2. Click **Thêm Công Việc Mới**
3. Fill form:
   - **Tiêu Đề** - Task title
   - **Mô Tả** - Details
   - **Ưu Tiên** - High, Normal, Low
   - **Cửa Hàng** - Leave blank for company-wide, OR select specific store
4. Click **Tạo Công Việc**
5. If store left blank: All staff see it
   If store selected: Only that store's staff sees it

---

## Staff User Guide

### What Can Staff Do?

✅ **View only their store's data** - Products, orders, analytics  
✅ **Cannot see other stores** - Complete isolation  
✅ **Manage own store products** - Check stock, update inventory  
✅ **Process own store orders** - Accept, ship, update status  
✅ **View assigned tasks** - Store tasks + company-wide tasks  
✅ **Respond to customer feedback** - Reviews and ratings  

### Staff Dashboard

**Access:** Click the BubbleBakery logo or visit `/staff/`

#### Header Navigation
```
🏪 BubbleBakery HCM    [Dashboard] [Đơn Hàng] [Kho Hàng] [Phản Hồi] [Công Việc]
```

**Store Badge:** Shows your assigned store (cannot change)

### Key Staff Tasks

#### 1. View Store Dashboard

1. Click **Dashboard** (or default landing page)
2. You automatically see:
   - Your store's products count
   - Your store's orders count
   - Your store's revenue today
   - Your store's pending orders
   - Recent orders for your store
   - Tasks assigned to your store

**Important:** You CANNOT see other stores' data.

#### 2. Manage Inventory

1. Click **Kho Hàng** in sidebar
2. View all products in your store:
   - Product name and image
   - Current stock quantity
   - Expiry date (if applicable)
   - Price
3. Can:
   - Click product to view details
   - See which products are low stock
   - Click "Update Stock" to add/remove items
   - Mark products as expired

#### 3. Process Orders

1. Click **Đơn Hàng** in sidebar
2. View all orders for your store:
   - Order ID and date
   - Customer name
   - Order total
   - Current status
3. For each order, you can:
   - **View Details** - Customer info, items, payment method
   - **Update Status** - Change from Pending → Processing → Shipped → Delivered
   - **Print Invoice** - For customer or shipping
   - **Contact Customer** - If needed

#### 4. Check Order Status

**Order Status Flow:**
```
Pending (New) → Processing → Shipped → Delivered
                    ↓
              Can Cancel Here
```

How to update status:
1. Click order in list
2. Click "Change Status"
3. Select new status from dropdown
4. Add note (optional) - e.g., "Shipped to Ha Noi"
5. Click "Save"

#### 5. Respond to Feedback

1. Click **Phản Hồi** in sidebar
2. View customer reviews and ratings:
   - 1 star, 2 star, 3 star, etc.
   - Filter by rating level
   - Search for specific feedback
3. Click feedback to expand
4. Click "Phản Hồi" to reply to customer
5. Write response and submit

#### 6. Check Tasks

1. Click **Công Việc** in sidebar
2. See two types of tasks:
   - **Store Tasks** - For your store only
   - **Company Tasks** - Visible to all staff
3. For each task:
   - View title and description
   - See priority (High/Normal/Low)
   - Mark as Complete when done
   - Can delete if assigned to you

---

## Common Tasks

### Task: Assign a New Staff Member to Store

**Who:** Admin only

**Steps:**
1. Go to **Quản Lý Tài Khoản**
2. Search for staff member name
3. Click staff member row
4. Click **Assign to Store**
5. Select store from dropdown
6. Click **Confirm**

**Result:** Staff member now sees only that store's data

### Task: Change Product Price

**Admin Way:**
1. Go to **Sản Phẩm**
2. Select store from dropdown
3. Find product
4. Click **Edit**
5. Change price field
6. Click **Save**

**Staff Way:**
1. Go to **Kho Hàng**
2. Find product
3. Can see current price but CANNOT change it
   (Only admins can change prices)

### Task: Create Company-Wide Announcement

**Who:** Admin only

**Steps:**
1. Go to **Công Việc**
2. Click **Thêm Công Việc Mới**
3. Fill in:
   - Title: "Company Announcement: Holiday Schedule"
   - Description: "Stores will close on April 30"
   - Priority: High
   - **Cửa Hàng: LEAVE BLANK** (This makes it visible to ALL staff)
4. Click **Tạo Công Việc**

**Result:** All staff members see this task

### Task: Create Store-Specific Task

**Who:** Admin only

**Steps:**
1. Go to **Công Việc**
2. Click **Thêm Công Việc Mới**
3. Fill in:
   - Title: "Clean storage room"
   - Description: "Deep clean before holiday"
   - Priority: Normal
   - **Cửa Hàng: Select "BubbleBakery HCM"** (Specific store)
4. Click **Tạo Công Việc**

**Result:** Only HCM store staff see this task

### Task: View Revenue for Specific Store

**Who:** Admin only

**Steps:**
1. Go to **Tổng Quan**
2. Store selector dropdown → Select store
3. Select date range (Today, Week, Month)
4. View:
   - Total revenue for period
   - Top products
   - Order count
   - Charts showing trends

### Task: Compare Stores Performance

**Who:** Admin only

**Steps:**
1. Go to **Dashboard**
2. Store selector → **Tất Cả Cửa Hàng** (All stores)
3. View company-wide dashboard
4. To see individual stores:
   - Open store selector
   - Click each store one by one
   - Note revenue, orders, performance
5. Can export reports for analysis

---

## FAQ

### Q: Why can't I see other stores' data?
**A:** Staff members are assigned to ONE store for security and organization. You can only see your store's data. This prevents confusion and ensures data isolation.

### Q: How do I know which store I'm assigned to?
**A:** Look at the top left of your dashboard. You'll see a green badge showing your store name:
```
🏪 BubbleBakery HCM
```

### Q: Can I change my assigned store?
**A:** No, only admins can assign or reassign staff to stores. Contact your admin if you need to switch stores.

### Q: Why can't I see the store dropdown?
**A:** 
- **If you're Admin:** Store dropdown only shows if there are multiple stores
- **If you're Staff:** You don't see a dropdown (your store is fixed)

### Q: What's the difference between "All Stores" and a specific store in admin view?
**A:**
- **All Stores** - View combined data from all locations
- **Specific Store** - Focus on one location's metrics

Example: Revenue might be ₫50M total for all stores, but ₫20M for HCM store only.

### Q: I updated an order status but it didn't save. Why?
**A:** Possible reasons:
1. You're trying to update an order from a different store
2. The order is locked (admin is viewing it)
3. Network connection issue - try again

To verify: Click on the order - if you can see it, you should be able to update it.

### Q: Can I delete products?
**A:** 
- **Admin:** Yes, can delete any product
- **Staff:** No, cannot delete products (only view inventory)

### Q: What happens if I try to access another store's order?
**A:** 
- **Admin:** Nothing (you can see all stores)
- **Staff:** You'll get error "You cannot access this order" (security measure)

### Q: Can I reply to customer feedback?
**A:** 
- **Admin:** Yes, can reply to all feedback
- **Staff:** Yes, can reply to feedback for own store

### Q: How do I know if a task is for my store or company-wide?
**A:** In the task list, look for:
- **No store specified** = Company-wide (all staff)
- **Store name shown** = That specific store only

### Q: What if there's a task for another store?
**A:** You won't see it. Tasks are filtered by your assigned store.

### Q: Can I create tasks?
**A:** 
- **Admin:** Yes, can create tasks for any store or company-wide
- **Staff:** No, can only view and complete assigned tasks

### Q: How often should I check my dashboard?
**A:** Recommended:
- **Morning:** Check today's orders and pending tasks
- **After each order:** Update order status
- **End of day:** Check sales, pending orders for tomorrow
- **Weekly:** Review revenue report

### Q: What if I forget my password?
**A:** Click "Forgot Password" on login screen or contact admin.

### Q: Can I see sales reports?
**A:** 
- **Admin:** Yes, detailed reports by store or company-wide
- **Staff:** Yes, can see your store's sales on dashboard (basic overview)

### Q: Who should I contact for technical issues?
**A:** Contact your admin or support team with:
- What you were doing
- What error message you got
- Screenshot if possible
- Time of issue

### Q: Is my data private?
**A:** 
- **Admin:** Can see all stores' data
- **Staff:** Can ONLY see their assigned store
- **Customer:** Can only see their own orders

### Q: Can staff from Store A see Store B's data?
**A:** No. The system prevents cross-store access. Even if staff tries to access other store's data via URL, they get "Access Denied" error.

---

## Keyboard Shortcuts

```
Ctrl + K    - Quick search for orders
Ctrl + N    - New task
Ctrl + S    - Save form
Ctrl + Q    - Quick filter (orders, products)
Esc         - Close dialog or modal
```

---

## Support

For questions or issues:
1. Check this guide's FAQ section
2. Contact your admin
3. Email support@bubblebakery.vn
4. Call: (028) 1234-5678

---

**End of User Operations Manual**

Version 1.0 | April 2026 | Multi-Store System User Guide
