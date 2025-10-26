// ==================== Navigation ====================
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');
const navLinks = document.querySelectorAll('.nav-link');

// Toggle mobile menu
hamburger?.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    hamburger.classList.toggle('active');
});

// Close menu when clicking nav link
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger?.classList.remove('active');
    });
});

// Active link on scroll
window.addEventListener('scroll', () => {
    let current = '';
    const sections = document.querySelectorAll('section');
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= (sectionTop - 200)) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// ==================== Smooth Scroll ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== Tabs Functionality ====================
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-tab');
        
        // Remove active class from all buttons and contents
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked button and corresponding content
        btn.classList.add('active');
        document.getElementById(targetTab)?.classList.add('active');
    });
});

// ==================== Copy Code ====================
function copyCode() {
    const code = document.querySelector('.code-example code').textContent;
    navigator.clipboard.writeText(code).then(() => {
        const btn = document.querySelector('.copy-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> 已复制';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    });
}

// ==================== Mini Chart ====================
function createMiniChart() {
    const canvas = document.getElementById('miniChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Sample data
    const data = [45000, 47000, 46500, 48000, 49500, 48800, 50000, 51200, 50800, 52000, 53500, 52800, 54500, 56000, 57200, 58500, 59800, 61000, 62500, 64000, 65500, 67000, 67234];
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min;
    
    // Draw line
    ctx.strokeStyle = '#27ae60';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    data.forEach((value, index) => {
        const x = (canvas.width / (data.length - 1)) * index;
        const y = canvas.height - ((value - min) / range) * canvas.height;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Draw area
    ctx.lineTo(canvas.width, canvas.height);
    ctx.lineTo(0, canvas.height);
    ctx.closePath();
    ctx.fillStyle = 'rgba(39, 174, 96, 0.1)';
    ctx.fill();
}

// ==================== Animations ====================
function animateOnScroll() {
    const elements = document.querySelectorAll('.feature-card, .doc-card, .stat-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s, transform 0.6s';
        observer.observe(el);
    });
}

// ==================== Progress Bar Animation ====================
function animateProgressBar() {
    const progressFill = document.querySelector('.progress-fill');
    if (!progressFill) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                progressFill.style.width = '79%';
            }
        });
    }, {
        threshold: 0.5
    });
    
    observer.observe(progressFill.parentElement);
}

// ==================== Stats Counter Animation ====================
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const text = target.textContent;
                const hasPercent = text.includes('%');
                const hasPlus = text.includes('+');
                const number = parseInt(text.replace(/[^0-9]/g, ''));
                
                if (isNaN(number)) return;
                
                let current = 0;
                const increment = number / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= number) {
                        current = number;
                        clearInterval(timer);
                    }
                    
                    let display = Math.floor(current).toLocaleString();
                    if (hasPercent) display += '%';
                    if (hasPlus && text.includes(',')) display += '+';
                    
                    target.textContent = display;
                }, 30);
            }
        });
    }, {
        threshold: 0.5
    });
    
    statNumbers.forEach(stat => observer.observe(stat));
}

// ==================== Dashboard Screenshot Placeholder ====================
function createDashboardPlaceholder() {
    const img = document.getElementById('dashboardImg');
    if (!img) return;
    
    // If image doesn't exist, create a placeholder
    img.onerror = function() {
        const parent = this.parentElement;
        parent.innerHTML = `
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 400px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 12px;
                color: white;
                font-size: 1.5rem;
                text-align: center;
                padding: 20px;
            ">
                <div>
                    <i class="fas fa-chart-line" style="font-size: 3rem; margin-bottom: 20px;"></i>
                    <p>Dashboard 正在运行</p>
                    <p style="font-size: 1rem; margin-top: 10px; opacity: 0.9;">
                        访问 <a href="http://localhost:8501" target="_blank" style="color: #f7931a; text-decoration: underline;">http://localhost:8501</a> 查看完整功能
                    </p>
                </div>
            </div>
        `;
    };
}

// ==================== Initialize ====================
document.addEventListener('DOMContentLoaded', () => {
    createMiniChart();
    animateOnScroll();
    animateProgressBar();
    animateStats();
    createDashboardPlaceholder();
    
    // Update copyright year
    const currentYear = new Date().getFullYear();
    const copyrightText = document.querySelector('.footer-bottom p');
    if (copyrightText) {
        copyrightText.textContent = copyrightText.textContent.replace('2025', currentYear);
    }
});

// ==================== Resize Handler ====================
window.addEventListener('resize', () => {
    createMiniChart();
});

// ==================== Export functions ====================
window.copyCode = copyCode;

