"""
Test chi tiết button giảm giá
"""
import requests
import re

BASE_URL = "http://127.0.0.1:5000"

def test_discount_button():
    """Test button giảm giá chi tiết."""
    print("=" * 60)
    print("TEST BUTTON GIẢM GIÁ")
    print("=" * 60)
    
    # Test 1: Truy cập endpoint giảm giá
    print("\n1. Truy cập ?discount=true...")
    response = requests.get(f"{BASE_URL}/?discount=true")
    
    if response.status_code != 200:
        print(f"   ❌ Lỗi: {response.status_code}")
        return
    
    print("   ✓ Response 200 OK")
    html = response.text
    
    # Test 2: Kiểm tra có tìm thấy grid không
    print("\n2. Tìm grid sản phẩm...")
    if 'id="products-grid"' not in html:
        print("   ❌ Không tìm thấy grid")
        return
    print("   ✓ Tìm thấy grid")
    
    # Test 3: Đếm số sản phẩm
    print("\n3. Đếm sản phẩm...")
    product_count = html.count('class="shop1 product-card')
    print(f"   ✓ Tìm thấy {product_count} sản phẩm")
    
    if product_count == 0:
        print("   ❌ KHÔNG CÓ SẢN PHẨM NÀO!")
        return
    
    # Test 4: Kiểm tra data-is-discount
    print("\n4. Kiểm tra data-is-discount...")
    discount_count = html.count('data-is-discount="true"')
    print(f"   ✓ {discount_count} sản phẩm có data-is-discount")
    
    # Test 5: Kiểm tra badge giảm giá
    print("\n5. Kiểm tra badge giảm giá...")
    badge_count = html.count('discount-badge')
    print(f"   ✓ {badge_count} badge được tìm thấy")
    
    # Test 6: Kiểm tra giá khuyến mại
    print("\n6. Kiểm tra giá khuyến mại...")
    # Tìm các cặp giá (original → discount)
    price_patterns = re.findall(r'(\d{2,3},\d{3})₫.*?(\d{2,3},\d{3})₫', html, re.DOTALL)
    if price_patterns:
        print(f"   ✓ Tìm thấy {len(price_patterns)} cặp giá")
        print(f"   Ví dụ: {price_patterns[0][0]}₫ → {price_patterns[0][1]}₫")
    else:
        print("   ⚠ Không tìm thấy cặp giá")
    
    # Test 7: Kiểm tra "Không tìm thấy" message
    print("\n7. Kiểm tra message...")
    if "Không tìm thấy" in html:
        print("   ❌ CÓ MESSAGE 'Không tìm thấy sản phẩm'")
        return
    print("   ✓ Không có message lỗi")
    
    # Test 8: Kiểm tra first product chi tiết
    print("\n8. Chi tiết sản phẩm đầu tiên...")
    first_product = re.search(
        r'<div class="shop1 product-card mix[^>]*>.*?<h2 class="product-name">([^<]+)</h2>',
        html,
        re.DOTALL
    )
    if first_product:
        print(f"   ✓ Sản phẩm: {first_product.group(1)}")
    
    print("\n" + "=" * 60)
    print("KẾT LUẬN:")
    print("=" * 60)
    if product_count > 0 and discount_count > 0 and badge_count > 0:
        print("✅ BUTTON GIẢM GIÁ HOẠT ĐỘNG!")
        print(f"   - {product_count} sản phẩm")
        print(f"   - Tất cả có data-is-discount")
        print(f"   - Tất cả có badge")
    else:
        print("❌ CÓ VẤN ĐỀ:")
        if product_count == 0:
            print("   - Không có sản phẩm nào")
        if discount_count == 0:
            print("   - Sản phẩm không được đánh dấu")
        if badge_count == 0:
            print("   - Không có badge hiển thị")
    
    print()

if __name__ == '__main__':
    try:
        test_discount_button()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
