from app import create_app
from app.models.user import User
from app.models.store import Store, StoreStaff
from app.models.product import Product

app = create_app('development')
with app.app_context():
    # Get all users
    all_users = User.query.all()
    print(f'Total users: {len(all_users)}')
    for u in all_users:
        print(f'  - {u.username} (ID: {u.id}, Role: {u.role})')
    
    print('\nAll store assignments:')
    assignments = StoreStaff.query.all()
    if assignments:
        for a in assignments:
            user = User.query.get(a.user_id)
            store = Store.query.get(a.store_id)
            print(f'  - User {user.username if user else "Unknown"} -> Store {store.name if store else "Unknown"}')
    else:
        print('  No store assignments found')
    
    print('\nAll stores:')
    stores = Store.query.all()
    for s in stores:
        print(f'  - {s.name} (ID: {s.id})')
    
    print('\nAll products:')
    products = Product.query.all()
    print(f'Total products: {len(products)}')
    for p in products[:10]:
        print(f'  - {p.name} (Store ID: {p.store_id}, In Stock: {p.in_stock})')
