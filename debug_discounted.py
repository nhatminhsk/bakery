"""
Debug get_discounted_products function with detailed logging
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.product import Product, ProductBatch

LOCAL_TIMEZONE = timezone(timedelta(hours=7))
EXPIRY_WARNING_HOURS = 8

def debug_discounted():
    """Debug the discounted products function."""
    app = create_app('development')
    
    with app.app_context():
        print("Debugging get_discounted_products()...\n")
        
        now_local = datetime.now(LOCAL_TIMEZONE)
        now_vn_naive = now_local.replace(tzinfo=None)
        
        print(f"Current time: {now_vn_naive}\n")
        
        # Get all products from store 1 with batches
        products = Product.query.filter_by(store_id=1).options(
            db.joinedload(Product.batches)
        ).all()
        
        print(f"Total store 1 products: {len(products)}\n")
        
        discounted_list = []
        
        for product in products:
            # Check if product has batches expiring soon
            active_batches = [
                batch for batch in (product.batches or [])
                if int(batch.quantity or 0) > 0 and batch.expiry_date
            ]
            
            if not active_batches:
                continue
            
            nearest_batch = min(active_batches, key=lambda item: item.expiry_date)
            
            # Calculate hours until expiry
            if nearest_batch.imported_at:
                imported_at_naive = nearest_batch.imported_at.replace(tzinfo=None) if nearest_batch.imported_at.tzinfo else nearest_batch.imported_at
                batch_expiry_datetime = imported_at_naive + timedelta(hours=24)
                hours_left = (batch_expiry_datetime - now_vn_naive).total_seconds() / 3600
            else:
                expiry_datetime = datetime.combine(nearest_batch.expiry_date, datetime.max.time())
                hours_left = (expiry_datetime - now_vn_naive).total_seconds() / 3600
            
            print(f"Product: {product.name}")
            print(f"  Active batches: {len(active_batches)}")
            print(f"  Nearest batch expiry_date: {nearest_batch.expiry_date}")
            print(f"  Nearest batch imported_at: {nearest_batch.imported_at}")
            print(f"  Calculated hours_left: {hours_left:.1f}")
            print(f"  <= {EXPIRY_WARNING_HOURS}h? {hours_left <= EXPIRY_WARNING_HOURS}")
            
            # Only include if expiring soon
            if hours_left <= EXPIRY_WARNING_HOURS:
                discounted_list.append({
                    'name': product.name,
                    'hours_left': hours_left
                })
                print(f"  [INCLUDED]\n")
            else:
                print(f"  [SKIPPED]\n")
        
        print("="*60)
        print(f"Total products expiring soon: {len(discounted_list)}\n")
        
        for item in discounted_list:
            print(f"- {item['name']} ({item['hours_left']:.1f}h)")

if __name__ == '__main__':
    debug_discounted()
