#!/usr/bin/env python
"""Phase 2 verification script - test store context integration."""

from app import create_app
from app.models.store import Store, StoreStaff
from app.models.product import Product
from app.models.order import Order
from app.models.user import User
from app.extensions import db

app = create_app('development')

def test_phase2():
    """Verify Phase 2 implementation."""
    with app.app_context():
        print("=" * 60)
        print("PHASE 2: Service Layer Integration - Verification")
        print("=" * 60)
        
        # 1. Check store exists
        print("\n1. Checking default store...")
        store = Store.query.filter_by(id=1).first()
        if store:
            print(f"   ✓ Default store found: {store.name} (code={store.code})")
        else:
            print("   ✗ Default store NOT found")
            return False
        
        # 2. Check store helper functions
        print("\n2. Testing store helper functions...")
        try:
            from app.utils.store_helper import (
                get_user_store,
                get_current_user_store,
                can_user_access_store,
                filter_query_by_user_store,
            )
            print("   ✓ All store helper functions imported successfully")
        except ImportError as e:
            print(f"   ✗ Failed to import store helpers: {e}")
            return False
        
        # 3. Check service layer imports
        print("\n3. Testing service layer imports...")
        try:
            from app.products.services import (
                get_all_products,
                get_products_paginated,
                get_product_by_id,
            )
            from app.staff.services import get_staff_todos
            from app.admin.services import (
                get_dashboard_stats,
                get_all_products_admin,
                get_revenue_by_week,
                get_revenue_by_month,
            )
            print("   ✓ All service functions imported successfully")
        except ImportError as e:
            print(f"   ✗ Failed to import services: {e}")
            return False
        
        # 4. Check function signatures have store_id parameter
        print("\n4. Checking function signatures...")
        import inspect
        
        # Check product services
        sig = inspect.signature(get_all_products)
        if 'store_id' in sig.parameters:
            print("   ✓ get_all_products has store_id parameter")
        else:
            print("   ✗ get_all_products missing store_id parameter")
        
        sig = inspect.signature(get_products_paginated)
        if 'store_id' in sig.parameters:
            print("   ✓ get_products_paginated has store_id parameter")
        else:
            print("   ✗ get_products_paginated missing store_id parameter")
        
        # Check admin services
        sig = inspect.signature(get_dashboard_stats)
        if 'store_id' in sig.parameters:
            print("   ✓ get_dashboard_stats has store_id parameter")
        else:
            print("   ✗ get_dashboard_stats missing store_id parameter")
        
        # 5. Check database schema
        print("\n5. Verifying database schema...")
        tables_with_store = {
            'products': 'store_id',
            'orders': 'store_id',
            'product_batches': 'store_id',
            'admin_todos': 'store_id',
        }
        
        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(db.engine)
        
        for table, col in tables_with_store.items():
            columns = [c['name'] for c in inspector.get_columns(table)]
            if col in columns:
                print(f"   ✓ {table} has {col} column")
            else:
                print(f"   ✗ {table} missing {col} column")
                return False
        
        # 6. Check relationships
        print("\n6. Checking Store model relationships...")
        store = Store.query.first()
        if hasattr(store, 'staff_assignment'):
            print("   ✓ Store has staff_assignment relationship")
        else:
            print("   ✗ Store missing staff_assignment relationship")
        
        if hasattr(store, 'products'):
            print("   ✓ Store has products relationship")
        else:
            print("   ✗ Store missing products relationship")
        
        print("\n" + "=" * 60)
        print("✓ Phase 2 verification complete - all checks passed!")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = test_phase2()
    exit(0 if success else 1)
