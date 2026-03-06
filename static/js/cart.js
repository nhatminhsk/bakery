// Cart Management System
class CartManager {
    constructor() {
        this.cartKey = 'bakery_cart';
        this.init();
    }

    init() {
        // Khởi tạo giỏ hàng nếu chưa có
        if (!localStorage.getItem(this.cartKey)) {
            localStorage.setItem(this.cartKey, JSON.stringify([]));
        }
    }

    getCart() {
        return JSON.parse(localStorage.getItem(this.cartKey) || '[]');
    }

    saveCart(cart) {
        localStorage.setItem(this.cartKey, JSON.stringify(cart));
    }

    addItem(product) {
        const cart = this.getCart();
        const existingItem = cart.find(item => item.id === product.id);

        if (existingItem) {
            existingItem.quantity = (existingItem.quantity || 1) + 1;
        } else {
            cart.push({
                id: product.id,
                name: product.name,
                price: product.price,
                image: product.image,
                quantity: 1
            });
        }

        this.saveCart(cart);
        this.updateCartDisplay();
        return cart;
    }

    removeItem(productId) {
        const cart = this.getCart().filter(item => item.id !== productId);
        this.saveCart(cart);
        this.updateCartDisplay();
        return cart;
    }

    updateQuantity(productId, quantity) {
        const cart = this.getCart();
        const item = cart.find(item => item.id === productId);

        if (item) {
            item.quantity = Math.max(0, quantity);
            if (item.quantity === 0) {
                this.removeItem(productId);
            } else {
                this.saveCart(cart);
                this.updateCartDisplay();
            }
        }
        return cart;
    }

    getTotalItems() {
        return this.getCart().reduce((total, item) => total + (item.quantity || 1), 0);
    }

    getTotalPrice() {
        return this.getCart().reduce((total, item) => {
            const price = parseFloat(item.price.replace(/[^\d]/g, '')) || 0;
            return total + (price * (item.quantity || 1));
        }, 0);
    }

    clearCart() {
        this.saveCart([]);
        this.updateCartDisplay();
    }

    updateCartDisplay() {
        // Cập nhật số lượng trên header
        const cartCountElements = document.querySelectorAll('.cart-count');
        const totalItems = this.getTotalItems();

        cartCountElements.forEach(element => {
            element.textContent = totalItems;
            element.style.display = totalItems > 0 ? 'inline' : 'none';
        });

        // Dispatch event để các component khác có thể lắng nghe
        window.dispatchEvent(new CustomEvent('cartUpdated', {
            detail: {
                totalItems: totalItems,
                totalPrice: this.getTotalPrice(),
                cart: this.getCart()
            }
        }));
    }
}

// Utility functions
const CartUtils = {
    formatPrice(price) {
        // Định dạng giá tiền VND
        if (typeof price === 'string') {
            price = parseFloat(price.replace(/[^\d]/g, ''));
        }
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price);
    },

    showNotification(message, type = 'info') {
        // Tạo notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';

        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        notification.innerHTML = `
            <i class="fa-solid ${iconMap[type] || 'fa-info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Thêm vào body
        document.body.appendChild(notification);

        // Tự động ẩn sau 3 giây
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    },

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
};

// Khởi tạo CartManager khi DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.cartManager = new CartManager();
    window.cartManager.updateCartDisplay();
});

// Export for global use
window.CartManager = CartManager;
window.CartUtils = CartUtils;