from app import create_app
from app.models.user import User
from app.models.store import Store, StoreStaff
from app.extensions import db

app = create_app('development')
with app.app_context():
    # Get FreshGarden store
    store = Store.query.filter_by(name='FreshGarden').first()
    if not store:
        print('Store FreshGarden not found')
        exit(1)
    
    # Check if store already has a staff assigned
    existing_assignment = StoreStaff.query.filter_by(store_id=store.id).first()
    if existing_assignment:
        user = User.query.get(existing_assignment.user_id)
        print(f'Store {store.name} already has staff assigned: {user.username}')
        print('Note: Only 1 staff can be assigned per store (1:1 relationship)')
        exit(0)
    
    # Get first staff user
    staff_user = User.query.filter_by(role='staff').first()
    
    if not staff_user:
        print('No staff user found')
        exit(1)
    
    print(f'Assigning {staff_user.username} to {store.name}...')
    assignment = StoreStaff(user_id=staff_user.id, store_id=store.id)
    db.session.add(assignment)
    db.session.commit()
    print(f'✓ {staff_user.username} assigned to {store.name}!')
