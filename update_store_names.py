"""
Update all store names to "Freshgarden-{Province}"
"""
from app import create_app
from app.models.store import Store
from app.extensions import db

def update_store_names():
    app = create_app('development')
    
    with app.app_context():
        # Mapping: store_id -> new_name
        store_updates = {
            1: 'Freshgarden-Ha Noi',
            2: 'Freshgarden-HCMC',
            3: 'Freshgarden-Da Nang',
            4: 'Freshgarden-Can Tho',
            5: 'Freshgarden-Hai Phong',
        }
        
        updated_count = 0
        for store_id, new_name in store_updates.items():
            store = Store.query.get(store_id)
            if store:
                old_name = store.name
                store.name = new_name
                db.session.add(store)
                updated_count += 1
                print(f"✓ Store ID {store_id}: '{old_name}' → '{new_name}'")
            else:
                print(f"❌ Store ID {store_id} not found")
        
        db.session.commit()
        print()
        print(f"✅ Updated {updated_count} stores successfully!")
        print()
        print("Updated stores:")
        for store in Store.query.all():
            print(f"  - ID {store.id}: {store.name}")

if __name__ == '__main__':
    update_store_names()
