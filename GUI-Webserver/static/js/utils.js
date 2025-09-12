/**
 * Utility functions for the UVA Lab System Panel
 */

// Global utility object
const Utils = {
    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - The type of toast (info, success, error)
     */
    showToast: function(message, type = 'info') {
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
    },
    
    /**
     * Add loading state to a button
     * @param {HTMLElement} button - The button element
     * @returns {Function} - Function to remove loading state
     */
    addLoadingState: function(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        button.disabled = true;
        button.classList.add('loading');
        
        return function() {
            button.innerHTML = originalText;
            button.disabled = false;
            button.classList.remove('loading');
        };
    },

    /**
     * Format numbers with scientific notation for small values
     * @param {number} value - The value to format
     * @returns {string} - Formatted number string
     */
    formatNumber: function(value) {
        const absValue = Math.abs(value);
        if (absValue < 0.001 || absValue > 1000) {
            // For very small values, use more precision in scientific notation
            if (absValue < 1e-10) {
                return value.toExponential(10);
            } else if (absValue < 1e-6) {
                return value.toExponential(10);
            } else {
                return value.toExponential(8);
            }
        } else {
            return value.toFixed(3);
        }
    },

    /**
     * Check if data needs scientific notation formatting
     * @param {Array} values - Array of values to check
     * @returns {boolean} - True if scientific notation is needed
     */
    needsScientificNotation: function(values) {
        if (!values || values.length === 0) return false;
        
        console.log('Checking scientific notation for values:', values.slice(0, 10));
        
        for (let value of values) {
            const absValue = Math.abs(value);
            if (absValue > 0 && (absValue < 0.001 || absValue > 1000)) {
                console.log('Found value needing scientific notation:', value, 'absValue:', absValue);
                return true;
            }
        }
        console.log('No values need scientific notation');
        return false;
    },

    /**
     * Show tooltip at specified coordinates
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @param {string} contents - Tooltip content
     */
    showTooltip: function(x, y, contents) {
        $('<div id="tooltip">' + contents + '</div>').css({
            position: 'absolute',
            display: 'none',
            top: y + 5,
            left: x + 5,
            border: '1px solid ' + (window.isDarkMode ? '#666' : '#ddd'),
            padding: '2px',
            'background-color': window.isDarkMode ? '#333' : '#fff',
            color: window.isDarkMode ? '#fff' : '#333',
            'font-size': '12px',
            'border-radius': '3px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
            'pointer-events': 'none',
            'z-index': 1000
        }).appendTo("body").fadeIn(200);
    },

    /**
     * Get column units based on column name
     * @param {string} column - Column name
     * @returns {string} - Unit string
     */
    getColumnUnits: function(column) {
        if (column.includes('fridge_vapor_pressure') || column.includes('root_exhausted_pressure')) {
            return ' (torr)';
        } else if (column.includes('ti') || column.includes('temperature')) {
            return ' (K)';
        } else if (column.includes('pt') || column.includes('magnet_pressure') || column.includes('purifier_inlet_pressure') || column.includes('buffer_pressure')) {
            return ' (psi)';
        } else if (column.includes('fc') || column.includes('flow')) {
            return ' (slm)';
        } else if (column.includes('lit') || column.includes('level')) {
            return ' (%)';
        } else if (column.includes('ait') || column.includes('analyzer')) {
            return ' (Mol %)';
        } else if (column.includes('seperator_inlet_pressure') || column.includes('upper_roots_pressure')) {
            return ' (mbar)';
        } else {
            return ''; // No units for unknown columns
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}
