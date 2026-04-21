"""
Test render template trực tiếp
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.products.services import get_discounted_products, get_categories

def test_render():
    """Test template rendering."""
    app = create_app('development')
    
    with app.app_context():
        # Get data
        products = get_discounted_products()
        categories = get_categories()
        discount_filter = True
        selected_category = ''
        
        print(f"Backend data:")
        print(f"  - Products: {len(products)}")
        print(f"  - Categories: {len(categories)}")
        print(f"  - discount_filter: {discount_filter}")
        print()
        
        # Render template
        from flask import render_template_string
        from jinja2 import Environment, FileSystemLoader
        
        # Load template
        template_path = os.path.join(os.path.dirname(__file__), 'Templates')
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template('index.html')
        
        # Render
        try:
            html = template.render(
                products=products,
                categories=categories,
                selected_category=selected_category,
                discount_filter=discount_filter
            )
            print("✓ Template rendered successfully")
            print()
            
            # Count products in HTML
            product_count = html.count('class="shop1 product-card')
            print(f"Products in HTML: {product_count}")
            
            # Check for errors
            if "Traceback" in html or "Error" in html:
                print("\n❌ Lỗi template:")
                start = html.find("Traceback")
                if start > -1:
                    print(html[start:start+500])
            else:
                print("✓ Không có lỗi")
            
            # Show first product
            import re
            first_product = re.search(r'<h2 class="product-name">([^<]+)</h2>', html)
            if first_product:
                print(f"\nSản phẩm đầu: {first_product.group(1)}")
            
        except Exception as e:
            print(f"❌ Lỗi render: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_render()
