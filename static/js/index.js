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
    const searchInput = document.querySelector('.search-header input[name="q"]');
    const categoryLinks = document.querySelectorAll('.category-badge');
    const products = document.querySelectorAll('.product-card');

    function normalizeText(value) {
        if (!value) {
            return '';
        }
        return value
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
    }

    function getSelectedCategoryClass() {
        const activeLink = document.querySelector('.category-badge.active');
        if (!activeLink) {
            return '';
        }

        const url = new URL(activeLink.href, window.location.origin);
        const selectedCategory = url.searchParams.get('category');
        return selectedCategory ? selectedCategory.replace(/\s+/g, '-') : '';
    }

    function applyProductFilters() {
        const selectedCategoryClass = getSelectedCategoryClass();
        const keyword = normalizeText(searchInput ? searchInput.value.trim() : '');

        products.forEach(product => {
            const nameElement = product.querySelector('.product-name');
            const productName = normalizeText(nameElement ? nameElement.textContent : '');

            const matchesCategory = !selectedCategoryClass || product.classList.contains(selectedCategoryClass);
            const matchesKeyword = !keyword || productName.includes(keyword);

            product.style.display = (matchesCategory && matchesKeyword) ? 'flex' : 'none';
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyProductFilters);
    }

    categoryLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // CHẶN LOAD LẠI TRANG

            // 1. Cập nhật trạng thái Active của nút
            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // 2. Lọc lại theo cả danh mục và từ khóa hiện tại
            applyProductFilters();
        });
    });

    applyProductFilters();
});