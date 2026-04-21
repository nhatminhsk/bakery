"""
Debug what the backend is actually returning
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_discount_debug():
    """Debug discount endpoint."""
    print("Testing discount endpoint...\n")
    
    response = requests.get(f"{BASE_URL}/?discount=true")
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    
    html = response.text
    
    # Look for product grid
    grid_start = html.find('id="products-grid"')
    if grid_start == -1:
        print("ERROR: products-grid not found")
        return
    
    # Get the grid section
    grid_section = html[grid_start:grid_start+2000]
    print("Grid section start:")
    print(grid_section[:500])
    print("\n...")
    
    # Count product cards in grid
    grid_end = html.find('</div>', grid_start)
    grid_html = html[grid_start:grid_end]
    product_count = grid_html.count('product-card')
    print(f"\nProduct cards in grid: {product_count}")
    
    # Check for "no products" message
    if "Không tìm thấy" in html:
        print("\n✗ 'No products found' message present in page")
    
    # Look for product name elements
    product_names = []
    import re
    for match in re.finditer(r'<h2 class="product-name">([^<]+)</h2>', html):
        product_names.append(match.group(1))
    
    print(f"\nProduct names found: {len(product_names)}")
    if product_names:
        for name in product_names[:5]:
            print(f"  - {name}")

if __name__ == '__main__':
    try:
        test_discount_debug()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
