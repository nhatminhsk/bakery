"""
Seed script: Import 1 batch of 5 random products to Fresh Garden at 18/4 20:30
- Store: Fresh Garden (ID=1)
- Time: 18/4 2026 20:30 (UTC+7)
- Products: 5 random products from Fresh Garden
- Quantity: 50 units per product
- Expiry: 24 hours from imported_at
"""
from datetime import datetime, timedelta, timezone
from app import create_app
from app.models.product import Product, ProductBatch
from app.extensions import db
import random

# UTC+7 timezone
LOCAL_TIMEZONE = timezone(timedelta(hours=7))

def seed_single_batch():
    app = create_app('development')
    
    with app.app_context():
        # Get 5 random products from Fresh Garden (store_id=1)
        fresh_garden_products = Product.query.filter_by(store_id=1).all()
        
        if len(fresh_garden_products) < 5:
            print(f"❌ Fresh Garden has only {len(fresh_garden_products)} products (need at least 5)")
            return
        
        selected_products = random.sample(fresh_garden_products, 5)
        
        # Set batch time: 18/4 20:30 UTC+7
        batch_imported_at = datetime(2026, 4, 18, 20, 30, 0, tzinfo=LOCAL_TIMEZONE)
        batch_expiry_date = (batch_imported_at + timedelta(hours=24)).date()
        
        print(f"🌱 Creating batch for Fresh Garden:")
        print(f"   Imported at: {batch_imported_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Expiry date: {batch_expiry_date.strftime('%d/%m/%Y')}")
        print(f"   Products: 5 random items from Fresh Garden")
        print()
        
        total_created = 0
        
        for product in selected_products:
            quantity = 5
            cost_price = int(product.price * 0.5)
            
            batch = ProductBatch(
                product_id=product.id,
                store_id=1,  # Fresh Garden
                quantity=quantity,
                cost_price=cost_price,
                expiry_date=batch_expiry_date,
                imported_at=batch_imported_at,
            )
            db.session.add(batch)
            db.session.flush()
            total_created += 1
            
            # Update product in_stock
            total_qty = ProductBatch.query.filter_by(product_id=product.id).with_entities(
                db.func.sum(ProductBatch.quantity)
            ).scalar() or 0
            product.in_stock = int(total_qty)
            
            print(f"   ✓ {product.name}: {quantity} units, expiry 24/4")
        
        db.session.commit()
        
        print()
        print(f"✅ Successfully created 1 batch with {total_created} products to Fresh Garden")
        print(f"   Total units: {total_created * quantity}")
        print(f"   Batch will show 'Sắp hết hạn' alert when time is near 19/4 20:30")

if __name__ == '__main__':
    seed_single_batch()
