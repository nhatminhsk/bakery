function sortProducts() {
    const sortValue = document.getElementById('sort').value;
    // Tìm các thẻ có class .product-card mà chúng ta vừa thêm vào HTML
    const products = Array.from(document.querySelectorAll('.product-card'));
    
    products.sort((a, b) => {
        switch(sortValue) {

            case 'newest':
                const dateA = new Date(a.dataset.date || 0);
                const dateB = new Date(b.dataset.date || 0);
                return dateB - dateA;
            case 'price-low':
                return parseInt(a.dataset.price) - parseInt(b.dataset.price);
            case 'price-high':
                return parseInt(b.dataset.price) - parseInt(a.dataset.price);
            case 'rating':
                return parseFloat(b.dataset.rating) - parseFloat(a.dataset.rating);
            default:
                return 0;
        }
    });

    const grid = document.getElementById('products-grid');
    products.forEach(product => grid.appendChild(product));
}
    function updateCartCount() {
        // Cập nhật số lượng giỏ hàng
        const cartCount = document.getElementById('cart-count');
        const current = parseInt(cartCount.textContent) || 0;
        cartCount.textContent = current + 1;
    }

function addToCart(productId) {
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cập nhật số hiển thị trên icon giỏ hàng (giả sử icon có id là cart-count)
            const cartCountElement = document.getElementById('cart-count');
            if (cartCountElement) {
                cartCountElement.textContent = data.cart_count;
            }
            alert('Đã thêm vào giỏ hàng thành công!');
        }
    })
    .catch(err => console.error('Lỗi:', err));
}
document.addEventListener('DOMContentLoaded', function () {
    const categoryLinks = document.querySelectorAll('.category-badge');
    const products = document.querySelectorAll('.product-card');

    categoryLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // CHẶN LOAD LẠI TRANG

            // 1. Cập nhật trạng thái Active của nút
            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // 2. Lấy danh mục cần lọc từ URL (Bánh Mì, Bánh Kem...)
            const url = new URL(this.href, window.location.origin);
            let selectedCategory = url.searchParams.get('category');
            if (selectedCategory) {
              selectedCategory = selectedCategory.replace(/\s+/g, '-');
            }
            // 3. Ẩn/Hiện sản phẩm dựa trên class
            products.forEach(product => {
                // Kiểm tra xem classList của thẻ có chứa tên danh mục không
                if (!selectedCategory || product.classList.contains(selectedCategory)) {
                    product.style.display = 'flex'; // Hiện
                } else {
                    product.style.display = 'none'; // Ẩn
                }
            });
        });
    });
});