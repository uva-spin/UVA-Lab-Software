
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

// Utility functions for the application
const Utils = {
    // Add loading state to a button
    addLoadingState: function(button) {
        if (!button) return () => {};
        
        const originalText = button.innerHTML;
        button.classList.add('loading');
        button.disabled = true;
        
        return function() {
            button.classList.remove('loading');
            button.disabled = false;
            button.innerHTML = originalText;
        };
    },
    
    // Show toast notification
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="${icon}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    },
    
    // Get appropriate icon for toast type
    getToastIcon: function(type) {
        switch (type) {
            case 'success':
                return 'fas fa-check-circle';
            case 'error':
                return 'fas fa-exclamation-circle';
            case 'warning':
                return 'fas fa-exclamation-triangle';
            default:
                return 'fas fa-info-circle';
        }
    },
    
    // Format timestamp for display
    formatTimestamp: function(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    },
    
    // Debounce function for performance
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function for performance
    throttle: function(func, limit) {
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
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
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

// Export functions for global use
window.Utils = {
    addLoadingState,
    showToast,
    logPerformance,
    debounce,
    throttle
};