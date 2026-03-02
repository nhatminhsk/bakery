const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');

// Xử lý chuyển đổi form bằng tay
registerLink.addEventListener('click', (e) => {
    e.preventDefault();
    wrapper.classList.add('active');
});

loginLink.addEventListener('click', (e) => {
    e.preventDefault();
    wrapper.classList.remove('active');
});

// Tự động chuyển form dựa trên trạng thái từ Backend
window.onload = () => {
    // Lấy giá trị trạng thái từ thẻ input ẩn (được tạo ở bước 3)
    const status = document.getElementById('reg_status')?.value;
    
    if (status === 'success') {
        // Đăng ký xong -> Hiện form Đăng nhập (Xóa class active)
        wrapper.classList.remove('active');
    } else if (status === 'error') {
        // Đăng ký lỗi -> Giữ nguyên form Đăng ký (Thêm class active)
        wrapper.classList.add('active');
    }
};
const registerForm = document.querySelector(".form-box.register form");
registerForm.addEventListener("submit", (e) => {
    // Nếu bạn muốn xử lý đăng ký qua AJAX thì dùng e.preventDefault()
    // Còn nếu gửi form truyền thống về Flask, trình duyệt sẽ tải lại trang.
    // Đoạn code dưới đây giúp giao diện quay về Đăng nhập ngay lập tức.
    wrapper.classList.remove("active");
    
    
    console.log("Đăng ký hoàn tất, đang quay lại đăng nhập...");
});


// Chờ trang web tải xong hoàn toàn
document.addEventListener('DOMContentLoaded', function() {
    // Tìm tất cả các thông báo flash
    const flashMessages = document.querySelectorAll('.alert, .flash-msg');

    flashMessages.forEach(function(message) {
        // Sau 5000ms (5 giây) sẽ thực hiện ẩn
        setTimeout(function() {
            // Thêm hiệu ứng mờ dần bằng CSS
            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";
            
            // Sau khi hiệu ứng mờ kết thúc (0.5s), xóa hẳn phần tử khỏi giao diện
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 500);
    });
});