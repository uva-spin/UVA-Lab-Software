
// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
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
});

// Add loading states to buttons
function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    button.disabled = true;
    button.classList.add('loading');
    
    return function() {
        button.innerHTML = originalText;
        button.disabled = false;
        button.classList.remove('loading');
    };
}

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to toggle theme
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        toggleTheme();
    }
    
    // Ctrl/Cmd + S to apply settings
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        document.getElementById('refresh-form').dispatchEvent(new Event('submit'));
    }

    if (e.key === 'Enter') {
        retry_column_refresh();
    }
});

// Performance monitoring
function logPerformance(label, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${label}: ${(end - start).toFixed(2)}ms`);
    return result;
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for performance
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function retry_column_refresh() {
    const column_refresh_button = document.getElementById('column-refresh-button');
    column_refresh_button.click();  
}

// Export functions for global use
window.Utils = {
    addLoadingState,
    showToast,
    logPerformance,
    debounce,
    throttle
};