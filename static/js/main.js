function myNav() {
  let bar = document.querySelector(".bar");
  let nav = document.querySelector(".navigation");
  bar.onclick = () => {
    if (nav.style.left == "0%") {
      nav.style.left = "-100%";
      bar.src = "assets/images/others/menu.png";
      document.body.style.overflow = "";
    } else {
      nav.style.left = "0%";
      bar.src = "assets/images/others/x.png";
      document.body.style.overflow = "hidden";
    }
  };
  document.onclick = (event) => {
    if (
      !nav.contains(event.target) &&
      !bar.contains(event.target) &&
      nav.style.left == "0%"
    ) {
      nav.style.left = "-100%";
      bar.src = "assets/images/others/menu.png";
      document.body.style.overflow = "";
    }
  };
}
myNav();

function ensureToastContainer() {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(container);
  }
  return container;
}

function showToast(message, type = 'info', title = '') {
  const container = ensureToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast-message toast-${type}`;

  const iconMap = {
    success: 'fa-circle-check',
    error: 'fa-circle-xmark',
    warning: 'fa-triangle-exclamation',
    info: 'fa-circle-info'
  };

  const titleText = title || {
    success: 'Thành công',
    error: 'Có lỗi',
    warning: 'Lưu ý',
    info: 'Thông báo'
  }[type] || 'Thông báo';

  toast.innerHTML = `
    <div class="toast-icon"><i class="fa-solid ${iconMap[type] || iconMap.info}"></i></div>
    <div class="toast-body">
      <div class="toast-title">${titleText}</div>
      <div>${message}</div>
    </div>
  `;

  container.appendChild(toast);

  window.setTimeout(() => {
    toast.classList.add('is-hiding');
    window.setTimeout(() => toast.remove(), 180);
  }, 2800);
}

window.showToast = showToast;

if (!window.CartUtils) {
  window.CartUtils = {
    formatPrice(price) {
      if (typeof price === 'string') {
        price = parseFloat(price.replace(/[^\d]/g, ''));
      }
      return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
      }).format(price || 0);
    },

    showNotification(message, type = 'info') {
      showToast(message, type);
    }
  };
}

document.addEventListener("contextmenu", function (e) {
  e.preventDefault();
});

document.addEventListener("keydown", function (e) {
  if (e.key === "F12") {
    e.preventDefault();
  }
  if (e.ctrlKey && e.shiftKey && (e.key === "I" || e.key === "J")) {
    e.preventDefault();
  }
  if (e.ctrlKey && e.key === "u") {
    e.preventDefault();
  }
  if (e.ctrlKey && e.key === "s") {
    e.preventDefault();
  }
});


function setActive(element) {
        const links = document.querySelectorAll(".link-menu");
        links.forEach((link) => link.classList.remove("active"));
        element.classList.add("active");
      }

function getGreeting() {
        const hour = new Date().getHours();
        if (hour >= 4 && hour < 12) {
          return "selamat pagi";
        } else if (hour >= 12 && hour < 15) {
          return "selamat siang";
        } else if (hour >= 15 && hour < 18) {
          return "selamat sore";
        } else {
          return "selamat malam";
        }
      }
/*function scrollToSection(event, sectionId, element) {
        event.preventDefault();

        const links = document.querySelectorAll("a");
        links.forEach((link) => link.classList.remove("active"));

        const activeLink = document.getElementById(element);
        if (activeLink) {
          activeLink.classList.add("active");
        }

        const targetElement = document.getElementById(sectionId);
        const offset = -80;
        const elementPosition =
          targetElement.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition + offset;
        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth",
        });
      }
*/
function handleNavClick(event, sectionId, navId) {
  // Kiểm tra nếu đang ở trang chủ (pathname là '/' hoặc trống)
  if (window.location.pathname === '/' || window.location.pathname === '/index') {
    if (typeof scrollToSection === 'function') {
      scrollToSection(event, sectionId, navId);
    }
  } else {
    // Nếu đang ở trang khác (như /login), cho phép trình duyệt 
    // chuyển hướng về index.html#about theo thuộc tính href mặc định
    return true; 
  }
}

function scrollToSection(event, sectionId, elementId) {
  const targetElement = document.getElementById(sectionId);
  if (targetElement) {
    event.preventDefault(); // Chỉ ngăn chặn chuyển hướng nếu tìm thấy ID trên trang hiện tại
    const offset = -80;
    const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({
      top: elementPosition + offset,
      behavior: "smooth",
    });
    
    // Cập nhật class active cho menu
    document.querySelectorAll('.navigation a').forEach(a => a.classList.remove('active'));
    document.getElementById(elementId).classList.add('active');
  }
}


  // Chờ cho đến khi toàn bộ nội dung trang được tải xong
  document.addEventListener("DOMContentLoaded", function() {
    // Tìm tất cả các phần tử có class 'alert' (Bootstrap dùng class này cho flash)
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
      // Thiết lập thời gian chờ 4000ms (4 giây) trước khi ẩn
      setTimeout(function() {
        // Tạo hiệu ứng mờ dần (nếu dùng Bootstrap 5)
        alert.style.transition = "opacity 0.6s ease";
        alert.style.opacity = "0";
        
        // Sau khi mờ hẳn thì xóa hoàn toàn khỏi giao diện để không chiếm diện tích
        setTimeout(function() {
          alert.remove();
        }, 600); 
      }, 500);
    });
  });
