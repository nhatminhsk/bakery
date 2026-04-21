"""
Save discount HTML to file for inspection
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

response = requests.get(f"{BASE_URL}/?discount=true")
html = response.text

# Save to file
with open("discount_page.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Saved to discount_page.html")

# Quick analysis
import re

# Find grid start
grid_match = re.search(r'<div class="products-slider-track"[^>]*id="products-grid"[^>]*>(.*?)</div>\s*</div>\s*<div class="products-pagination"', html, re.DOTALL)

if grid_match:
    grid_content = grid_match.group(1)
    print(f"Grid content length: {len(grid_content)} chars")
    
    # Count product divs
    product_divs = len(re.findall(r'<div class="shop1 product-card', grid_content))
    print(f"Product divs found: {product_divs}")
    
    # Show first 1000 chars
    print("\nFirst 1000 chars of grid:")
    print(grid_content[:1000])
else:
    print("Grid section not found with regex")
