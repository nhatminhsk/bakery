"""
Test the discount filter endpoint
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_discount_filter():
    """Test the discount filter endpoint."""
    print("Testing discount filter endpoint...\n")
    
    # Test 1: Regular products
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✓ Main page loads successfully")
        if "Danh sách sản phẩm" in response.text:
            print("✓ Products section found\n")
    else:
        print(f"✗ Main page error: {response.status_code}\n")
    
    # Test 2: Category filter
    response = requests.get(f"{BASE_URL}/?category=Bánh%20kem")
    if response.status_code == 200:
        print("✓ Category filter works")
        if "Bánh kem" in response.text:
            print("✓ Category products displayed\n")
    else:
        print(f"✗ Category filter error: {response.status_code}\n")
    
    # Test 3: Discount filter
    response = requests.get(f"{BASE_URL}/?discount=true")
    if response.status_code == 200:
        print("✓ Discount filter endpoint responds")
        
        # Check if discount products are in the page
        if "GIẢM GIÁ" in response.text or "discount" in response.text.lower():
            print("✓ Discount filter is active\n")
            
            # Look for discount indicators
            if "24,500" in response.text or "24500" in response.text:
                print("✓ Discount prices found in response\n")
            else:
                print("⚠ No discount prices found in HTML\n")
        else:
            print("⚠ Discount filter not found in response\n")
    else:
        print(f"✗ Discount filter error: {response.status_code}\n")

if __name__ == '__main__':
    try:
        test_discount_filter()
    except Exception as e:
        print(f"Error: {e}")
