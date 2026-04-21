"""
Fix product categories in database.
Update product.category from Banh kem/Banh ngot to Bánh kem/Bánh ngọt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.product import Product

def fix_product_categories():
    """Fix Vietnamese diacritics in product categories."""
    app = create_app('development')
    
    with app.app_context():
        print("🔧 Fixing product categories...\n")
        
        # Mapping
        replacements = {
            'Banh kem': 'Bánh kem',
            'Banh ngot': 'Bánh ngọt',
        }
        
        for old_cat, new_cat in replacements.items():
            products = Product.query.filter_by(category=old_cat).all()
            if products:
                print(f"   ✓ Updating {len(products)} products: '{old_cat}' → '{new_cat}'")
                for product in products:
                    product.category = new_cat
            else:
                print(f"   ✗ No products found with category '{old_cat}'")
        
        db.session.commit()
        print("\n✅ Product categories fixed!")
        
        # Verify
        print("\n📊 Verification:")
        categories = {}
        products = Product.query.filter_by(store_id=1).all()
        for product in products:
            cat = product.category or "NO_CATEGORY"
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        for cat in sorted(categories.keys()):
            print(f"   '{cat}': {categories[cat]} products")

if __name__ == '__main__':
    fix_product_categories()
