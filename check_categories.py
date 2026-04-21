"""
Check product categories in database
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.product import Product

def check_categories():
    """Check what categories products have."""
    app = create_app('development')
    
    with app.app_context():
        print("📊 Checking product categories...\n")
        
        # Get all store 1 products
        products = Product.query.filter_by(store_id=1).all()
        print(f"Total products in store 1: {len(products)}\n")
        
        # Group by category
        categories = {}
        for product in products:
            cat = product.category or "NO_CATEGORY"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(product.name)
        
        print("Categories and product counts:")
        for cat in sorted(categories.keys()):
            print(f"  '{cat}': {len(categories[cat])} products")
            # Show first 3 products
            for name in categories[cat][:3]:
                print(f"    - {name}")
            if len(categories[cat]) > 3:
                print(f"    ... and {len(categories[cat]) - 3} more")
        
        print(f"\n✅ Total categories: {len(categories)}")

if __name__ == '__main__':
    check_categories()
