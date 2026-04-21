"""
Kiểm tra xem file JS có được load đúng không
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

response = requests.get(f"{BASE_URL}/?discount=true")
html = response.text

# Tìm link tới file JS index.js
import re

js_links = re.findall(r'<script[^>]*src="([^"]*index\.js[^"]*)"', html)
print(f"File JS index.js: {js_links}")

# Tìm phần khai báo hàm applyProductFilters
if "applyProductFilters" in html:
    print("\n✓ Tìm thấy 'applyProductFilters'")
    
    # Tìm xem lỗi gì
    if "Cannot read properties" in html:
        print("❌ Có lỗi 'Cannot read properties'")
    
    # Tìm hàm trong inline script
    if "function applyProductFilters() {" in html:
        print("✓ Có khai báo hàm")
    else:
        print("⚠ Không tìm thấy khai báo hàm")
else:
    print("❌ Không tìm thấy 'applyProductFilters' - JS chưa load!")

# Kiểm tra xem có inline script không
inline_scripts = html.count("<script>")
print(f"\nInline scripts: {inline_scripts}")

# Lấy phần script cuối cùng (scroll)
scroll_script = re.search(r'<script>.*?function scrollToTop', html, re.DOTALL)
if scroll_script:
    print("✓ Tìm thấy script scroll")
else:
    print("⚠ Không tìm thấy script scroll")

print("\n" + "="*60)
print("KIỂM TRA THÊM:")
print("="*60)

# Kiểm tra xem products-grid có HTML không
grid_start = html.find('id="products-grid"')
grid_end = html.find('</div>', grid_start)
grid_html = html[grid_start:grid_end+6]

product_count = grid_html.count('class="shop1 product-card')
print(f"Số sản phẩm trong HTML: {product_count}")

if product_count == 0:
    print("❌ Không có sản phẩm trong HTML!")
elif product_count == 21:
    print("✓ Có 21 sản phẩm trong HTML")
    print("👉 Vấn đề là JavaScript không hiển thị chúng")
