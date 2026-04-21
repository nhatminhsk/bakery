"""
Kiểm tra sản phẩm giảm giá có category không
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.products.services import get_discounted_products

def test_category():
    """Check if products have category."""
    app = create_app('development')
    
    with app.app_context():
        products = get_discounted_products()
        
        print(f"Tổng sản phẩm: {len(products)}\n")
        
        if not products:
            print("❌ Không có sản phẩm!")
            return
        
        # Kiểm tra sản phẩm đầu tiên
        p = products[0]
        print(f"Sản phẩm đầu: {p.name}")
        print(f"  - Category: {p.category}")
        print(f"  - is_discounted: {getattr(p, 'is_discounted', 'KHÔNG CÓ!')}")
        print(f"  - discount_percent: {getattr(p, 'discount_percent', 'KHÔNG CÓ!')}")
        print(f"  - discount_price: {getattr(p, 'discount_price', 'KHÔNG CÓ!')}")
        
        # Kiểm tra số sản phẩm không có category
        no_category = 0
        for p in products:
            if not p.category:
                no_category += 1
        
        print(f"\nSản phẩm không có category: {no_category}")
        
        if no_category == len(products):
            print("❌ TẤT CẢ sản phẩm không có category! Đây là vấn đề!")
            print("   → Jinja template sẽ fail trên: {{ product.category | replace(' ', '-') }}")

if __name__ == '__main__':
    test_category()
