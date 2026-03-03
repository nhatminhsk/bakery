/**
 * Quản lý giao diện và kiểm tra dữ liệu cho trang Login/Register
 */

document.addEventListener('DOMContentLoaded', () => {
    const wrapper = document.querySelector('.wrapper');
    const loginLink = document.querySelector('.login-link');
    const registerLink = document.querySelector('.register-link');
    const registerForm = document.querySelector(".form-box.register form");
    const loginForm = document.querySelector(".form-box.login form");

    // --- 1. XỬ LÝ CHUYỂN ĐỔI GIAO DIỆN ---

    // Chuyển sang form Đăng ký
    registerLink.addEventListener('click', (e) => {
        e.preventDefault();
        wrapper.classList.add('active');
    });

    // Chuyển sang form Đăng nhập
    loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        wrapper.classList.remove('active');
    });

    // Tự động chuyển form dựa trên trạng thái từ Backend (Flash messages)
    const status = document.getElementById('reg_status')?.value;
    if (status === 'success') {
        wrapper.classList.remove('active');
    } else if (status === 'error') {
        wrapper.classList.add('active');
    }

    // --- 2. VALIDATION (KIỂM TRA DỮ LIỆU) ---

    /**
     * Hàm hiển thị thông báo lỗi nhanh
     */
    const showError = (message) => {
        // Bạn có thể thay alert bằng một thông báo nội bộ đẹp hơn nếu muốn
        alert(message);
    };

    /**
     * Xử lý kiểm tra form Đăng ký
     */
    registerForm.addEventListener('submit', (e) => {
        const username = registerForm.querySelector('input[name="username"]').value.trim();
        const email = registerForm.querySelector('input[name="email"]').value.trim();
        const password = registerForm.querySelector('input[name="password"]').value.trim();

        // Regex: Chỉ chấp nhận đuôi @gmail.com
        const emailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;

        // Regex: Ít nhất 8 ký tự, 1 chữ hoa, 1 chữ thường và 1 số
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

        // Kiểm tra Tên đăng nhập
        if (username.length < 3) {
            showError("Tên đăng nhập phải có ít nhất 3 ký tự!");
            e.preventDefault();
            return;
        }

        // Kiểm tra Email @gmail.com
        if (!emailRegex.test(email)) {
            showError("Vui lòng sử dụng địa chỉ Email định dạng @gmail.com!");
            e.preventDefault();
            return;
        }

        // Kiểm tra Mật khẩu mạnh
        if (!passwordRegex.test(password)) {
            showError("Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và chữ số!");
            e.preventDefault();
            return;
        }

        console.log("Dữ liệu đăng ký hợp lệ!");
    });

    /**
     * Xử lý kiểm tra form Đăng nhập (Cơ bản)
     */
    loginForm.addEventListener('submit', (e) => {
        const username = loginForm.querySelector('input[name="username"]').value.trim();
        const password = loginForm.querySelector('input[name="password"]').value.trim();

        if (!username || !password) {
            showError("Vui lòng nhập đầy đủ tài khoản và mật khẩu!");
            e.preventDefault();
        }
    });

    // --- 3. HIỆU ỨNG THÔNG BÁO FLASH ---

    const flashMessages = document.querySelectorAll('.flash-msg');
    flashMessages.forEach((msg) => {
        // Tự động ẩn sau 4 giây
        setTimeout(() => {
            msg.style.transition = "all 0.5s ease";
            msg.style.opacity = "0";
            msg.style.transform = "translateY(-10px)";
            
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });
});