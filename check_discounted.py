"""
Check if there are any batches expiring soon (within 8 hours)
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.product import Product, ProductBatch

LOCAL_TIMEZONE = timezone(timedelta(hours=7))
EXPIRY_WARNING_HOURS = 8

def check_discounted_products():
    """Check if there are products expiring soon."""
    app = create_app('development')
    
    with app.app_context():
        print("Checking batches for discount products...\n")
        
        now_local = datetime.now(LOCAL_TIMEZONE)
        now_vn_naive = now_local.replace(tzinfo=None)
        
        print(f"Current time (VN): {now_vn_naive}\n")
        
        # Get all batches from store 1 products
        products = Product.query.filter_by(store_id=1).all()
        print(f"Total store 1 products: {len(products)}")
        
        all_batches = ProductBatch.query.join(Product).filter(
            Product.store_id == 1
        ).all()
        print(f"Total batches in store 1: {len(all_batches)}\n")
        
        if not all_batches:
            print("NO BATCHES FOUND IN DATABASE!\n")
            return
        
        # Count batches by quantity status
        zero_qty = 0
        nonzero_qty = 0
        
        expiring_soon = []
        for batch in all_batches:
            product = Product.query.get(batch.product_id)
            if not product:
                continue
            
            qty = int(batch.quantity or 0)
            if qty > 0:
                nonzero_qty += 1
            else:
                zero_qty += 1
            
            if not batch.imported_at:
                continue
                
            imported_at_naive = batch.imported_at.replace(tzinfo=None) if batch.imported_at.tzinfo else batch.imported_at
            batch_expiry_datetime = imported_at_naive + timedelta(hours=24)
            hours_left = (batch_expiry_datetime - now_vn_naive).total_seconds() / 3600
            
            if qty > 0 and hours_left <= EXPIRY_WARNING_HOURS:
                expiring_soon.append({
                    'product': product.name,
                    'hours_left': hours_left,
                    'batch_id': batch.id,
                    'quantity': qty
                })
        
        print("="*60)
        print("SUMMARY:")
        print(f"Total batches: {len(all_batches)}")
        print(f"Batches with qty > 0: {nonzero_qty}")
        print(f"Batches with qty = 0: {zero_qty}")
        print(f"Batches expiring soon (<= {EXPIRY_WARNING_HOURS}h): {len(expiring_soon)}")
        
        if expiring_soon:
            print("\nProducts that should be discounted:")
            for item in expiring_soon:
                print(f"  - {item['product']} (qty={item['quantity']}, hours={item['hours_left']:.1f})")
        else:
            print(f"\nPROBLEM: NO PRODUCTS EXPIRING SOON!")
            print("Reason: All batches either have qty=0 or hours_left > 8 hours")
            print("\nTo fix, click the TEST button (04/18 batch) in admin panel")
            print("Or import new batches with import button")

if __name__ == '__main__':
    check_discounted_products()
