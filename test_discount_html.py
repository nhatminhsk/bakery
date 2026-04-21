"""
Check what HTML is rendered for discount filter
"""
import requests
import re

BASE_URL = "http://127.0.0.1:5000"

def test_discount_html():
    """Check the rendered HTML for discount products."""
    print("Testing discount HTML rendering...\n")
    
    response = requests.get(f"{BASE_URL}/?discount=true")
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    
    html = response.text
    
    # Count product cards
    product_cards = html.count('class="product-card')
    print(f"Found {product_cards} product cards\n")
    
    # Check for discount data attribute
    discount_attr_count = html.count('data-is-discount="true"')
    print(f"Products marked with data-is-discount: {discount_attr_count}")
    
    # Check for discount indicators
    discount_badges = html.count('class="discount-badge')
    print(f"Discount badges found: {discount_badges}")
    
    # Check for strikethrough prices
    strikethrough_count = html.count('text-decoration: line-through')
    print(f"Strikethrough prices: {strikethrough_count}")
    
    # Check for red discount prices
    dc2626_count = html.count('#dc2626')
    print(f"Red price elements (#dc2626): {dc2626_count}")
    
    # Look for specific price numbers
    prices_35000 = html.count('35,000')
    prices_24500 = html.count('24,500')
    
    print(f"\nPrice occurrences:")
    print(f"  Original (35,000): {prices_35000}")
    print(f"  Discounted (24,500): {prices_24500}")
    
    # Find a discount product card to show details
    if 'data-is-discount="true"' in html:
        print("\n✓ Discount products properly marked with data-is-discount")
        
        # Find first discount product card
        start = html.find('data-is-discount="true"')
        if start != -1:
            # Get the product card div opening
            card_start = html.rfind('<div', 0, start)
            snippet = html[card_start:start+200]
            print(f"\nDiscount product card snippet:")
            print(snippet)

if __name__ == '__main__':
    try:
        test_discount_html()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
