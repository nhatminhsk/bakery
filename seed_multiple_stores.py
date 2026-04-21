"""
Seed script to create 5 new stores and assign staff users (demo_user_01 to demo_user_05)
Each store gets sample products with batches
Batch expiry: 24 hours from creation time
"""
from datetime import datetime, timedelta, timezone
from app import create_app
from app.models.user import User
from app.models.store import Store, StoreStaff, StoreSetting
from app.models.product import Product, ProductBatch
from app.extensions import db

# Vietnam timezone (UTC+7)
VN_OFFSET = timezone(timedelta(hours=7))
VN_NOW = datetime.now(VN_OFFSET)

STORE_NAMES = [
    'FreshGarden',  # 0 - already exists
    'Sweet Bakery Ha Noi',
    'Golden Cake Ho Chi Minh',
    'Artisan Pastry Da Nang',
    'Premium Donuts Can Tho',
    'Delicious Bread Hai Phong',
]

STORE_CODES = [
    'FG',
    'SBH',
    'GCM',
    'APD',
    'PDC',
    'DBH',
]

STORE_ADDRESSES = [
    'Số 123 Đường Trần Duy Hưng, Hà Nội',
    '456 Đường Nguyễn Huệ, TP.HCM',
    '789 Đường Lê Lợi, Đà Nẵng',
    '321 Đường 3 Tháng 2, Cần Thơ',
    '654 Đường Trần Phú, Hải Phòng',
    '987 Đường Võ Văn Tần, Hà Nội',
]

PRODUCT_NAMES = [
    'Bánh mousse Chanh leo',
    'Bánh kem Mật ngọt',
    'Bánh su kem sô cô la',
    'Bánh chiffon ba vị',
    'Bánh cuộn sô cô la',
    'Bánh madeleine',
    'Bánh su kem',
    'Tiramisu',
    'Bánh sô cô la sữa',
    'Bánh trứng vàng baby',
]

def seed_stores():
    app = create_app('development')
    with app.app_context():
        print('🌱 Seeding stores and staff...')
        
        # Create staff users if they don't exist
        print('\n👤 Creating staff users...')
        for i in range(1, 6):
            username = f'demo_user_{i:02d}'
            user = User.query.filter_by(username=username).first()
            if user:
                # Update role to staff if needed
                if user.role != 'staff':
                    old_role = user.role
                    user.role = 'staff'
                    db.session.commit()
                    print(f'  ↻ {username} role updated: {old_role} -> staff')
                else:
                    print(f'  ℹ️  {username} already staff')
            else:
                user = User(
                    username=username,
                    email=f'{username}@bakery.local',
                    role='staff',
                )
                user.set_password('password123')
                db.session.add(user)
                print(f'  ✓ Created {username}')
        
        db.session.commit()
        
        # Get staff users
        staff_users = User.query.filter_by(role='staff').order_by(User.id).limit(5).all()
        if len(staff_users) < 5:
            print(f'❌ Need at least 5 staff users, found {len(staff_users)}')
            return
        
        created_stores = []
        
        # Create 4 new stores (skip index 0 as FreshGarden already exists)
        for i in range(1, 5):
            store_name = STORE_NAMES[i]
            
            # Check if store already exists
            existing = Store.query.filter_by(name=store_name).first()
            if existing:
                print(f'  ℹ️  Store {store_name} already exists (ID: {existing.id})')
                created_stores.append(existing)
                continue
            
            store = Store(
                name=store_name,
                code=STORE_CODES[i],
                address=STORE_ADDRESSES[i],
                phone=f'0{3000000 + i * 100000:07d}',
                email=f'contact@{STORE_CODES[i].lower()}.bakery',
                is_active=True,
            )
            db.session.add(store)
            db.session.flush()  # Get ID
            
            # Create store settings
            settings = StoreSetting(store_id=store.id)
            db.session.add(settings)
            
            print(f'  ✓ Created store: {store_name} (ID: {store.id})')
            created_stores.append(store)
        
        db.session.commit()
        
        # Assign staff to stores (demo_user_01 to demo_user_05)
        print('\n👤 Assigning staff to stores...')
        
        # Get all stores
        all_stores = Store.query.all()
        
        # Create/update staff assignments for first 5 staff users
        for idx, staff_user in enumerate(staff_users[:5]):
            store = all_stores[idx]
            
            # Check if already assigned
            existing = StoreStaff.query.filter_by(user_id=staff_user.id).first()
            if existing:
                # Update store
                existing.store_id = store.id
                print(f'  ↻ {staff_user.username} -> {store.name} (reassigned)')
            else:
                # Remove old assignment to this store
                old = StoreStaff.query.filter_by(store_id=store.id).first()
                if old:
                    db.session.delete(old)
                
                assignment = StoreStaff(user_id=staff_user.id, store_id=store.id)
                db.session.add(assignment)
                print(f'  ✓ {staff_user.username} -> {store.name}')
        
        db.session.commit()
        
        # Add products to stores
        print('\n📦 Adding products to stores...')
        
        for store_idx, store in enumerate(all_stores):
            existing_products = Product.query.filter_by(store_id=store.id).count()
            if existing_products > 0:
                print(f'  ℹ️  Store {store.name} already has {existing_products} products')
                continue
            
            # Add 8-10 random products to this store
            import random
            num_products = random.randint(8, 10)
            selected_products = random.sample(PRODUCT_NAMES, num_products)
            
            for product_name in selected_products:
                product = Product(
                    name=product_name,
                    category='Bakery',
                    price=random.randint(50000, 250000),
                    description=f'{product_name} - Tươi ngon mỗi ngày',
                    store_id=store.id,
                    in_stock=0,
                )
                db.session.add(product)
                db.session.flush()
            
            print(f'  ✓ Added {num_products} products to {store.name}')
        
        db.session.commit()
        print('\n✅ Seeding complete!')

if __name__ == '__main__':
    seed_stores()
