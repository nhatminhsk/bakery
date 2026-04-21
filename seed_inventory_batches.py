"""
Seed inventory with batches that expire in 24 hours
This can be called from admin route /admin/import-stock
"""
from datetime import datetime, timedelta, timezone
from app import create_app
from app.models.product import Product, ProductBatch
from app.extensions import db

# Vietnam timezone (UTC+7)
VN_OFFSET = timezone(timedelta(hours=7))

def seed_inventory_batches(store_id=None):
    """
    Create new batches for all products in a store with 24-hour expiry
    
    Args:
        store_id: Filter by store (if None, create for all stores)
    
    Returns:
        dict with status info
    """
    app = create_app('development')
    with app.app_context():
        # Current time in Vietnam timezone
        now_vn = datetime.now(VN_OFFSET)
        
        # Batch creation time
        batch_created = now_vn
        
        # Expiry time: +24 hours
        batch_expiry = now_vn + timedelta(hours=24)
        
        # Get products
        query = Product.query
        if store_id:
            query = query.filter_by(store_id=store_id)
        
        products = query.all()
        
        total_batches = 0
        
        for product in products:
            # Create 1-3 batches per product
            import random
            num_batches = random.randint(1, 3)
            
            for b in range(num_batches):
                quantity = random.randint(10, 30)
                cost_price = int(product.price * 0.5)  # 50% margin
                
                batch = ProductBatch(
                    product_id=product.id,
                    store_id=product.store_id,
                    quantity=quantity,
                    cost_price=cost_price,
                    expiry_date=batch_expiry.date(),
                    imported_at=batch_created,
                )
                db.session.add(batch)
                total_batches += 1
            
            # Update product in_stock
            total_qty = sum(int(b.quantity or 0) for b in product.batches)
            product.in_stock = total_qty
        
        db.session.commit()
        
        return {
            'status': 'success',
            'total_products': len(products),
            'total_batches': total_batches,
            'created_at': batch_created.isoformat(),
            'expiry_at': batch_expiry.isoformat(),
            'store_id': store_id,
        }

if __name__ == '__main__':
    # Test seed for all stores
    result = seed_inventory_batches()
    print(f'✅ Seeded {result["total_batches"]} batches')
    print(f'   Created: {result["created_at"]}')
    print(f'   Expires: {result["expiry_at"]}')
