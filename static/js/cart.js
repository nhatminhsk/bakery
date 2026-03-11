const formatMoney = (amount) => '₫' + amount.toLocaleString('en-US');
function removeFromCart(productId) {
    if (confirm('Bạn chắc chắn muốn xóa sản phẩm này?')) {
        fetch('/api/cart/remove/' + productId, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Xóa mượt mà thẻ HTML của sản phẩm đó đi
                document.getElementById(`cart-item-${productId}`).remove();
                
                // Nếu giỏ hàng trống trơn (số lượng = 0), ép reload để hiện giao diện "Giỏ hàng trống"
                if (data.cart_count === 0) {
                    location.reload();
                    return;
                }

                // Cập nhật lại Tóm tắt đơn hàng
                updateCartSummary(data);
            }
        });
    }
}
function updateQuantity(productId, delta) {
    fetch('/api/cart/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, delta: delta })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cập nhật số lượng và giá của RIÊNG sản phẩm đó
            document.getElementById(`qty-display-${productId}`).textContent = data.item_qty;
            document.getElementById(`item-price-${productId}`).textContent = 
                `${formatMoney(data.item_price)} x ${data.item_qty}`;

            // Cập nhật Tóm tắt đơn hàng (Tạm tính, Ship, Tổng cộng)
            updateCartSummary(data);
        }
    });
}

function updateCartSummary(data) {
    // 1. Cập nhật Icon giỏ hàng trên thanh menu (base.html)
    const cartBadge = document.getElementById('cart-count');
    if (cartBadge) cartBadge.textContent = data.cart_count;

    // 2. Cập nhật tiền
    document.getElementById('cart-subtotal').textContent = formatMoney(data.subtotal);
    document.getElementById('cart-total').textContent = formatMoney(data.total);

    // 3. Xử lý đổi màu phí ship nếu được Freeship
    const shippingEl = document.getElementById('cart-shipping');
    if (data.shipping === 0) {
        shippingEl.textContent = 'Miễn phí';
        shippingEl.style.color = '#22c55e'; // Màu xanh lá
    } else {
        shippingEl.textContent = formatMoney(data.shipping);
        shippingEl.style.color = ''; // Xóa màu xanh
    }
}