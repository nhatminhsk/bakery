"""
Duplicate all products from store 1 (Freshgarden-Ha Noi) to stores 2-5.
This establishes the chain model where all 5 stores have identical products.
"""
import os
import sys

# Add the bakery directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.product import Product
from datetime import datetime

def duplicate_products_to_all_stores():
    """Duplicate all products from store 1 to stores 2, 3, 4, 5."""
    app = create_app('development')
    
    with app.app_context():
        # Get all products from store 1
        store_1_products = Product.query.filter_by(store_id=1).all()
        print(f"📦 Found {len(store_1_products)} products in Freshgarden-Ha Noi (store 1)")
        
        if not store_1_products:
            print("❌ No products found in store 1!")
            return
        
        # Target stores (2, 3, 4, 5)
        target_stores = [2, 3, 4, 5]
        store_names = {
            2: "Freshgarden-HCMC",
            3: "Freshgarden-Da Nang",
            4: "Freshgarden-Can Tho",
            5: "Freshgarden-Hai Phong"
        }
        
        for target_store_id in target_stores:
            print(f"\n🔄 Duplicating products to {store_names[target_store_id]} (store {target_store_id})...")
            
            duplicated_count = 0
            for source_product in store_1_products:
                # Create new product with same attributes but different store_id
                new_product = Product(
                    name=source_product.name,
                    category=source_product.category,
                    description=source_product.description,
                    price=source_product.price,
                    image_url=source_product.image_url,
                    rating=source_product.rating,
                    store_id=target_store_id,
                    in_stock=0,  # No batches yet
                    created_at=datetime.utcnow()
                )
                db.session.add(new_product)
                duplicated_count += 1
            
            try:
                db.session.commit()
                print(f"   ✅ Successfully duplicated {duplicated_count} products to store {target_store_id}")
            except Exception as e:
                db.session.rollback()
                print(f"   ❌ Error duplicating to store {target_store_id}: {str(e)}")
                return
        
        # Verify
        print("\n📊 Verification:")
        for store_id in [1, 2, 3, 4, 5]:
            count = Product.query.filter_by(store_id=store_id).count()
            store_name = store_names.get(store_id, "Freshgarden-Ha Noi")
            print(f"   Store {store_id} ({store_name}): {count} products")
        
        print("\n✨ Chain model established! All 5 stores now have identical 43 products.")

if __name__ == '__main__':
    duplicate_products_to_all_stores()
