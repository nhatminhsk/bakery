"""
Test get_discounted_products function
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.products.services import get_discounted_products

def test_discounted():
    """Test the discounted products function."""
    app = create_app('development')
    
    with app.app_context():
        print("Testing get_discounted_products()...\n")
        
        products = get_discounted_products()
        
        print(f"Returned {len(products)} discounted products\n")
        
        if products:
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.name}")
                print(f"   Price: {product.price} -> {product.discount_price}")
                print(f"   Discount: {product.discount_percent}%")
                print(f"   Hours left: {product.expiry_hours_left}")
                print()
        else:
            print("ERROR: No products returned!")

if __name__ == '__main__':
    test_discounted()
