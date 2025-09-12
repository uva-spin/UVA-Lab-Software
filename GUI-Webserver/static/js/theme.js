/**
 * Theme management functions for the UVA Lab System Panel
 */

/**
 * Toggle between dark and light theme
 */
function toggleTheme() {
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    const isDark = html.getAttribute('data-theme') === 'dark';
    
    if (isDark) {
        html.setAttribute('data-theme', 'light');
        themeIcon.className = 'fas fa-moon';
        window.isDarkMode = false;
    } else {
        html.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        window.isDarkMode = true;
    }
    
    updateChartTheme();
}

/**
 * Update chart theme based on current mode
 */
function updateChartTheme() {
    if (window.selectedKeys.length === 0) {
        updateEmptyChartDisplay();
    }
}

/**
 * Dynamic RGB gradient animation for empty chart
 */
function updateEmptyChartDisplay() {
    const chartContainer = document.getElementById('chart');
    chartContainer.innerHTML = `
        <div class="empty-chart-container">
            <div class="gradient-text">
                <span class="swirling-text">Select Data Entries</span>
            </div>
        </div>
    `;
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        toggleTheme,
        updateChartTheme,
        updateEmptyChartDisplay
    };
}
