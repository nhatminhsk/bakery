from app import create_app
from app.extensions import db
from sqlalchemy import inspect

app = create_app('development')
with app.app_context():
    inspector = inspect(db.engine)
    
    tables = ['stores', 'store_staff', 'store_settings', 'products', 'orders', 'product_batches', 'admin_todos']
    
    for table in tables:
        print(f'\n{table}:')
        if table in inspector.get_table_names():
            columns = inspector.get_columns(table)
            for col in columns:
                print(f'  - {col["name"]}: {col["type"]}')
        else:
            print('  TABLE NOT FOUND')
