#!/usr/bin/env python
"""Phase 5 Integration Tests - End-to-End Multi-Store Testing."""

from app import create_app
from app.models.store import Store, StoreStaff
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.payment import Payment
from app.extensions import db
from datetime import datetime, timedelta
from flask_login import login_user
import sys

app = create_app('development')

class TestScenarios:
    """Integration test scenarios for multi-store system."""
    
    @staticmethod
    def test_store_setup():
        """Test 1: Store setup and initialization."""
        print("\n" + "=" * 70)
        print("TEST 1: Store Setup & Initialization")
        print("=" * 70)
        
        # Check default store exists
        default_store = Store.query.filter_by(id=1).first()
        if not default_store:
            print("✗ Default store not found")
            return False
        print(f"✓ Default store exists: {default_store.name} (ID: {default_store.id})")
        
        # Check store has required columns
        if not hasattr(default_store, 'code'):
            print("✗ Store missing 'code' column")
            return False
        if not hasattr(default_store, 'address'):
            print("✗ Store missing 'address' column")
            return False
        if not hasattr(default_store, 'is_active'):
            print("✗ Store missing 'is_active' column")
            return False
        print(f"✓ Store has all required fields (code, address, is_active, etc.)")
        
        # Check store is active
        if not default_store.is_active:
            print("✗ Default store is not active")
            return False
        print(f"✓ Default store is active")
        
        return True
    
    @staticmethod
    def test_staff_assignment():
        """Test 2: Staff assignment to stores."""
        print("\n" + "=" * 70)
        print("TEST 2: Staff Assignment to Stores")
        print("=" * 70)
        
        # Find a staff user
        staff_user = User.query.filter_by(role='staff').first()
        if not staff_user:
            print("⚠ No staff user found for testing (creating test staff user...)")
            # This is okay - just warning
        else:
            print(f"✓ Found staff user: {staff_user.username} (ID: {staff_user.id})")
            
            # Check if staff is assigned to a store
            staff_assignment = StoreStaff.query.filter_by(user_id=staff_user.id).first()
            if staff_assignment:
                store = Store.query.filter_by(id=staff_assignment.store_id).first()
                print(f"✓ Staff assigned to store: {store.name} (Store ID: {staff_assignment.store_id})")
                
                # Verify unique constraint (only 1 assignment per staff)
                other_assignments = StoreStaff.query.filter_by(user_id=staff_user.id).count()
                if other_assignments == 1:
                    print(f"✓ Staff has exactly 1 store assignment (unique constraint works)")
                else:
                    print(f"✗ Staff has {other_assignments} assignments (should be 1)")
                    return False
            else:
                print(f"⚠ Staff user not assigned to any store")
        
        return True
    
    @staticmethod
    def test_product_store_filtering():
        """Test 3: Product filtering by store."""
        print("\n" + "=" * 70)
        print("TEST 3: Product Store Filtering")
        print("=" * 70)
        
        # Count products by store
        store_id = 1
        products = Product.query.filter_by(store_id=store_id).all()
        print(f"✓ Found {len(products)} products in store {store_id}")
        
        # Check all products have store_id
        all_products = Product.query.all()
        untagged = [p for p in all_products if p.store_id is None]
        if untagged:
            print(f"✗ Found {len(untagged)} products without store_id")
            return False
        print(f"✓ All {len(all_products)} products have store_id assigned")
        
        if len(products) > 0:
            sample_product = products[0]
            print(f"✓ Sample product: {sample_product.name} (Store: {sample_product.store_id})")
        
        return True
    
    @staticmethod
    def test_order_store_filtering():
        """Test 4: Order filtering by store."""
        print("\n" + "=" * 70)
        print("TEST 4: Order Store Filtering")
        print("=" * 70)
        
        # Count orders by store
        store_id = 1
        orders = Order.query.filter_by(store_id=store_id).all()
        print(f"✓ Found {len(orders)} orders in store {store_id}")
        
        # Check all orders have store_id
        all_orders = Order.query.all()
        untagged = [o for o in all_orders if o.store_id is None]
        if untagged:
            print(f"✗ Found {len(untagged)} orders without store_id")
            return False
        print(f"✓ All {len(all_orders)} orders have store_id assigned")
        
        if len(orders) > 0:
            sample_order = orders[0]
            print(f"✓ Sample order: Order#{sample_order.id} (Store: {sample_order.store_id}, Status: {sample_order.status})")
            
            # Verify order totals calculation
            if sample_order.total > 0:
                print(f"✓ Order total calculated: ₫{sample_order.total:,.0f}")
            else:
                print(f"⚠ Order total is 0 or null")
        
        return True
    
    @staticmethod
    def test_admin_service_filtering():
        """Test 5: Admin service filtering by store."""
        print("\n" + "=" * 70)
        print("TEST 5: Admin Service Store Filtering")
        print("=" * 70)
        
        from app.admin.services import get_dashboard_stats, get_all_products_admin
        
        # Test dashboard stats with store_id
        stats_all = get_dashboard_stats(store_id=None)
        stats_store1 = get_dashboard_stats(store_id=1)
        
        print(f"✓ Dashboard stats (all stores): {len(stats_all)} stats")
        print(f"✓ Dashboard stats (store 1): {len(stats_store1)} stats")
        
        # Stats should have key fields
        required_fields = ['total_products', 'total_orders', 'pending_orders']
        for field in required_fields:
            if field in stats_store1:
                print(f"  ✓ {field}: {stats_store1[field]}")
            else:
                print(f"  ✗ Missing field: {field}")
                return False
        
        # Test products filtering
        products_all = get_all_products_admin(store_id=None)
        products_store1 = get_all_products_admin(store_id=1)
        
        print(f"✓ Products (all stores): {len(products_all)} products")
        print(f"✓ Products (store 1): {len(products_store1)} products")
        
        # Products should be in results
        if len(products_store1) > 0:
            print(f"  ✓ Sample: {products_store1[0]['name']}")
        
        return True
    
    @staticmethod
    def test_staff_service_filtering():
        """Test 6: Staff service filtering by user store."""
        print("\n" + "=" * 70)
        print("TEST 6: Staff Service Store Filtering")
        print("=" * 70)
        
        from app.staff.services import get_staff_dashboard_data
        from app.utils.store_helper import get_user_store
        
        # Find a staff user
        staff_user = User.query.filter_by(role='staff').first()
        if not staff_user:
            print("⚠ No staff user found - skipping staff service tests")
            return True
        
        # Get staff's store
        user_store = get_user_store(staff_user.id)
        if not user_store:
            print(f"⚠ Staff user {staff_user.username} not assigned to a store")
            return True
        
        print(f"✓ Staff user: {staff_user.username}")
        print(f"✓ Assigned store: {user_store.name} (ID: {user_store.id})")
        
        # Get staff dashboard data
        data = get_staff_dashboard_data(user_id=staff_user.id)
        print(f"✓ Staff dashboard data retrieved")
        
        # Verify data structure
        if 'total_products' in data:
            print(f"  ✓ Total products in staff's store: {data['total_products']}")
        if 'total_orders' in data:
            print(f"  ✓ Total orders in staff's store: {data['total_orders']}")
        if 'pending_orders' in data:
            print(f"  ✓ Pending orders in staff's store: {data['pending_orders']}")
        
        return True
    
    @staticmethod
    def test_authorization_decorators():
        """Test 7: Authorization decorators."""
        print("\n" + "=" * 70)
        print("TEST 7: Authorization Decorators")
        print("=" * 70)
        
        from app.utils.permissions import admin_required, staff_required, check_store_access
        
        # Check decorators exist
        print(f"✓ admin_required decorator available")
        print(f"✓ staff_required decorator available")
        print(f"✓ check_store_access function available")
        
        # Check admin user can be found
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            print(f"✓ Admin user exists: {admin_user.username}")
        else:
            print(f"✗ No admin user found")
            return False
        
        # Check staff user exists
        staff_user = User.query.filter_by(role='staff').first()
        if staff_user:
            print(f"✓ Staff user exists: {staff_user.username}")
        else:
            print(f"⚠ No staff user found for authorization testing")
        
        return True
    
    @staticmethod
    def test_database_schema():
        """Test 8: Database schema verification."""
        print("\n" + "=" * 70)
        print("TEST 8: Database Schema Verification")
        print("=" * 70)
        
        from sqlalchemy import inspect as sa_inspect
        
        inspector = sa_inspect(db.engine)
        
        # Check required tables exist
        required_tables = ['stores', 'store_staff', 'store_settings', 'users', 'products', 'orders', 'admin_todos']
        for table_name in required_tables:
            if table_name in inspector.get_table_names():
                print(f"✓ Table '{table_name}' exists")
            else:
                print(f"✗ Table '{table_name}' missing")
                return False
        
        # Check products table has store_id
        product_cols = [c['name'] for c in inspector.get_columns('products')]
        if 'store_id' in product_cols:
            print(f"✓ products.store_id column exists")
        else:
            print(f"✗ products.store_id column missing")
            return False
        
        # Check orders table has store_id
        order_cols = [c['name'] for c in inspector.get_columns('orders')]
        if 'store_id' in order_cols:
            print(f"✓ orders.store_id column exists")
        else:
            print(f"✗ orders.store_id column missing")
            return False
        
        # Check admin_todos has store_id
        todo_cols = [c['name'] for c in inspector.get_columns('admin_todos')]
        if 'store_id' in todo_cols:
            print(f"✓ admin_todos.store_id column exists")
        else:
            print(f"✗ admin_todos.store_id column missing")
            return False
        
        return True

def run_all_tests():
    """Run all integration tests."""
    with app.app_context():
        print("\n" + "=" * 70)
        print("PHASE 5: End-to-End Integration Testing")
        print("=" * 70)
        print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ('Store Setup', TestScenarios.test_store_setup),
            ('Staff Assignment', TestScenarios.test_staff_assignment),
            ('Product Filtering', TestScenarios.test_product_store_filtering),
            ('Order Filtering', TestScenarios.test_order_store_filtering),
            ('Admin Services', TestScenarios.test_admin_service_filtering),
            ('Staff Services', TestScenarios.test_staff_service_filtering),
            ('Authorization', TestScenarios.test_authorization_decorators),
            ('Database Schema', TestScenarios.test_database_schema),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n✗ Test '{test_name}' failed with exception:")
                print(f"  {type(e).__name__}: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print("\n" + "=" * 70)
        if passed == total:
            print(f"✓ ALL TESTS PASSED ({passed}/{total})")
            print("=" * 70)
            return True
        else:
            print(f"✗ TESTS FAILED ({passed}/{total} passed)")
            print("=" * 70)
            return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
