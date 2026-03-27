function sortProducts() {
    if (typeof window.__refreshProductsSlider === 'function') {
        window.__refreshProductsSlider(true);
    }
}

function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    const current = parseInt(cartCount.textContent, 10) || 0;
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
    const categoryLinks = document.querySelectorAll('.categories-list .category-badge');
    const sortSelect = document.getElementById('sort');
    const grid = document.getElementById('products-grid');
    const prevButton = document.getElementById('products-prev');
    const nextButton = document.getElementById('products-next');
    const pageButtonsContainer = document.getElementById('products-page-buttons');
    const pageIndicator = document.getElementById('products-page-indicator');

    if (!grid) {
        return;
    }

    const allProducts = Array.from(grid.querySelectorAll('.product-card'));
    const PRODUCTS_PER_PAGE = 16;
    let filteredProducts = [...allProducts];
    let currentPage = 1;
    let totalPages = 1;

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
        const activeLink = document.querySelector('.categories-list .category-badge.active');
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
        const sortValue = sortSelect ? sortSelect.value : 'newest';

        filteredProducts = allProducts.filter(product => {
            const nameElement = product.querySelector('.product-name');
            const productName = normalizeText(nameElement ? nameElement.textContent : '');

            const matchesCategory = !selectedCategoryClass || product.classList.contains(selectedCategoryClass);
            const matchesKeyword = !keyword || productName.includes(keyword);

            return matchesCategory && matchesKeyword;
        });

        filteredProducts.sort((a, b) => {
            switch (sortValue) {
                case 'newest': {
                    const dateA = new Date(a.dataset.date || 0);
                    const dateB = new Date(b.dataset.date || 0);
                    return dateB - dateA;
                }
                case 'price-low':
                    return parseInt(a.dataset.price, 10) - parseInt(b.dataset.price, 10);
                case 'price-high':
                    return parseInt(b.dataset.price, 10) - parseInt(a.dataset.price, 10);
                case 'rating':
                    return parseFloat(b.dataset.rating) - parseFloat(a.dataset.rating);
                default:
                    return 0;
            }
        });

        totalPages = Math.max(1, Math.ceil(filteredProducts.length / PRODUCTS_PER_PAGE));
        if (currentPage > totalPages) {
            currentPage = totalPages;
        }

        renderPages();
        renderPaginationButtons();
        updateSlider();
    }

    function renderPages() {
        grid.innerHTML = '';

        if (filteredProducts.length === 0) {
            const emptyPage = document.createElement('div');
            emptyPage.className = 'products-page';

            const emptyState = document.createElement('div');
            emptyState.className = 'products-empty';
            emptyState.textContent = 'Không tìm thấy sản phẩm phù hợp.';

            emptyPage.appendChild(emptyState);
            grid.appendChild(emptyPage);
            return;
        }

        for (let page = 1; page <= totalPages; page += 1) {
            const pageWrapper = document.createElement('div');
            pageWrapper.className = 'products-page';

            const start = (page - 1) * PRODUCTS_PER_PAGE;
            const end = start + PRODUCTS_PER_PAGE;
            filteredProducts.slice(start, end).forEach(product => {
                pageWrapper.appendChild(product);
            });

            grid.appendChild(pageWrapper);
        }
    }

    function updateSlider() {
        const offset = (currentPage - 1) * 100;
        grid.style.transform = `translateX(-${offset}%)`;

        if (prevButton) {
            prevButton.disabled = currentPage <= 1;
            prevButton.style.opacity = currentPage <= 1 ? '0.4' : '1';
            prevButton.style.pointerEvents = currentPage <= 1 ? 'none' : 'auto';
        }

        if (nextButton) {
            nextButton.disabled = currentPage >= totalPages;
            nextButton.style.opacity = currentPage >= totalPages ? '0.4' : '1';
            nextButton.style.pointerEvents = currentPage >= totalPages ? 'none' : 'auto';
        }

        if (pageIndicator) {
            pageIndicator.textContent = `Trang ${currentPage} / ${totalPages}`;
        }
    }

    function renderPaginationButtons() {
        if (!pageButtonsContainer) {
            return;
        }

        pageButtonsContainer.innerHTML = '';

        for (let page = 1; page <= totalPages; page += 1) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = page === currentPage
                ? 'category-badge products-page-btn active'
                : 'category-badge products-page-btn';
            button.textContent = page;
            button.addEventListener('click', function () {
                currentPage = page;
                renderPaginationButtons();
                updateSlider();
            });
            pageButtonsContainer.appendChild(button);
        }
    }

    if (prevButton) {
        prevButton.addEventListener('click', function () {
            if (currentPage > 1) {
                currentPage -= 1;
                renderPaginationButtons();
                updateSlider();
            }
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', function () {
            if (currentPage < totalPages) {
                currentPage += 1;
                renderPaginationButtons();
                updateSlider();
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyProductFilters);
    }

    categoryLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();

            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            currentPage = 1;
            applyProductFilters();
        });
    });

    window.__refreshProductsSlider = function (keepCurrentPage) {
        if (!keepCurrentPage) {
            currentPage = 1;
        }
        applyProductFilters();
    };

    applyProductFilters();
});