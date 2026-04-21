"""
Detailed test of get_discounted_products with attribute checking
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.products.services import get_discounted_products

def test_discounted_attrs():
    """Test that discount attributes are properly set."""
    app = create_app('development')
    
    with app.app_context():
        print("Testing discount products attributes...\n")
        
        products = get_discounted_products()
        
        print(f"Returned {len(products)} discounted products\n")
        
        if not products:
            print("ERROR: No products returned!")
            return
        
        # Check first product
        product = products[0]
        print(f"First product: {product.name}\n")
        print(f"Attributes:")
        print(f"  - has is_discounted? {hasattr(product, 'is_discounted')}")
        if hasattr(product, 'is_discounted'):
            print(f"    value: {product.is_discounted}")
        
        print(f"  - has discount_percent? {hasattr(product, 'discount_percent')}")
        if hasattr(product, 'discount_percent'):
            print(f"    value: {product.discount_percent}")
        
        print(f"  - has original_price? {hasattr(product, 'original_price')}")
        if hasattr(product, 'original_price'):
            print(f"    value: {product.original_price}")
        
        print(f"  - has discount_price? {hasattr(product, 'discount_price')}")
        if hasattr(product, 'discount_price'):
            print(f"    value: {product.discount_price}")
        
        print(f"  - has expiry_hours_left? {hasattr(product, 'expiry_hours_left')}")
        if hasattr(product, 'expiry_hours_left'):
            print(f"    value: {product.expiry_hours_left}")
        
        print(f"  - has price? {hasattr(product, 'price')}")
        if hasattr(product, 'price'):
            print(f"    value: {product.price}")
        
        print(f"  - has rating? {hasattr(product, 'rating')}")
        if hasattr(product, 'rating'):
            print(f"    value: {product.rating}")

if __name__ == '__main__':
    test_discounted_attrs()
