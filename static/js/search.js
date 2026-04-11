// Search Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Khởi tạo trang search
    initializeSearchPage();
});

function initializeSearchPage() {
    // Xử lý dữ liệu sản phẩm từ server
    processSearchResults();

    // Thêm event listeners cho các nút
    addEventListeners();

    // Lắng nghe sự kiện cập nhật giỏ hàng
    window.addEventListener('cartUpdated', handleCartUpdate);
}

function processSearchResults() {
    // Lấy dữ liệu từ server (nếu cần xử lý thêm)
    const resultsContainer = document.querySelector('.search-results');
    const noResultsContainer = document.querySelector('.no-results');

    if (resultsContainer && resultsContainer.querySelector('.products-grid')) {
        // Xử lý các sản phẩm đã được render từ server
        const productCards = resultsContainer.querySelectorAll('.product-card');

        productCards.forEach((card) => {
            // Thêm event listener cho nút mua ngay
            const buyButton = card.querySelector('.btn-custom');
            if (buyButton) {
                buyButton.addEventListener('click', function(event) {
                    event.stopPropagation();
                    handleAddToCart(card);
                });
            }

            card.addEventListener('click', function(event) {
                if (event.target.closest('button, a, input, select, textarea, label, form')) {
                    return;
                }
                const detailUrl = card.dataset.productUrl || `/product/${card.dataset.productId}`;
                if (detailUrl) {
                    window.location.href = detailUrl;
                }
            });

            card.addEventListener('keydown', function(event) {
                if (event.key !== 'Enter' && event.key !== ' ') {
                    return;
                }
                event.preventDefault();
                const detailUrl = card.dataset.productUrl || `/product/${card.dataset.productId}`;
                if (detailUrl) {
                    window.location.href = detailUrl;
                }
            });
        });

        console.log(`Đã xử lý ${productCards.length} sản phẩm`);
    }
}

function addEventListeners() {
    // Có thể thêm các event listener khác ở đây
    console.log('Search page initialized');
}

function handleAddToCart(productCard) {
    // Lấy thông tin sản phẩm từ card
    const productId = productCard.getAttribute('data-product-id');
    const productName = productCard.querySelector('.product-name').textContent;
    const productPrice = productCard.querySelector('.product-price').textContent;
    const productImage = productCard.querySelector('.product-image img');

    // Tạo object sản phẩm
    const product = {
        id: productId,
        name: productName,
        price: productPrice,
        image: productImage ? productImage.src : null
    };

    // Thêm vào giỏ hàng sử dụng CartManager
    if (window.cartManager) {
        window.cartManager.addItem(product);
        CartUtils.showNotification(`Đã thêm "${productName}" vào giỏ hàng!`, 'success');
    } else {
        console.error('CartManager chưa được khởi tạo');
        CartUtils.showNotification('Có lỗi xảy ra khi thêm vào giỏ hàng', 'error');
    }
}

function handleCartUpdate(event) {
    // Xử lý khi giỏ hàng được cập nhật
    const { totalItems, totalPrice } = event.detail;
    console.log(`Giỏ hàng cập nhật: ${totalItems} sản phẩm, tổng giá: ${CartUtils.formatPrice(totalPrice)}`);
}

// Export functions for global use (if needed)
window.SearchUtils = {
    initializeSearchPage,
    handleAddToCart
};
