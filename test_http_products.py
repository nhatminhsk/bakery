"""
Kiểm tra sản phẩm trong HTML từ HTTP request
"""
import requests
import re

BASE_URL = "http://127.0.0.1:5000"

print("Kiểm tra 3 endpoint:")
print("=" * 60)

# Test 1: Tất cả sản phẩm
print("\n1. Tất Cả (trang chủ)")
response = requests.get(f"{BASE_URL}/")
product_count = response.text.count('class="shop1 product-card')
print(f"   Sản phẩm: {product_count}")
if product_count > 0:
    names = re.findall(r'<h2 class="product-name">([^<]+)</h2>', response.text)
    print(f"   Ví dụ: {names[:2] if names else 'Không tìm thấy'}")

# Test 2: Bánh kem
print("\n2. Bánh kem (category filter)")
response = requests.get(f"{BASE_URL}/?category=Bánh kem")
product_count = response.text.count('class="shop1 product-card')
print(f"   Sản phẩm: {product_count}")
if product_count > 0:
    names = re.findall(r'<h2 class="product-name">([^<]+)</h2>', response.text)
    print(f"   Ví dụ: {names[:2] if names else 'Không tìm thấy'}")

# Test 3: Giảm giá
print("\n3. Giảm Giá (discount filter)")
response = requests.get(f"{BASE_URL}/?discount=true")
html = response.text
product_count = html.count('class="shop1 product-card')
print(f"   Sản phẩm: {product_count}")

if product_count > 0:
    names = re.findall(r'<h2 class="product-name">([^<]+)</h2>', html)
    print(f"   Ví dụ: {names[:3] if names else 'Không tìm thấy'}")
    
    # Kiểm tra badge
    badges = html.count('discount-badge')
    print(f"   Badge: {badges}")
    
    # Kiểm tra strikethrough
    strikethrough = html.count('text-decoration: line-through')
    print(f"   Strikethrough: {strikethrough}")
else:
    print("   ❌ KHÔNG CÓ SẢN PHẨM!")
    # Kiểm tra lỗi
    if "Không tìm thấy" in html:
        print("   ⚠ Message: 'Không tìm thấy sản phẩm'")
    else:
        print("   ⚠ Không có message lỗi")

print("\n" + "=" * 60)
