/**
 * Main application logic and initialization for the UVA Lab System Panel
 */

// Global variables
let hours = 1;
let minutes = 0;
let seconds = 0;
let remainingTime = null;
let timerInterval = null;
let selectedKeys = [];
let isDarkMode = false;
let availableColumns = [];
let columnsByTable = {};
let plotInstance = null;
let updateTime = 5; // Default update interval in seconds

// Make variables globally accessible
window.hours = hours;
window.minutes = minutes;
window.seconds = seconds;
window.selectedKeys = selectedKeys;
window.isDarkMode = isDarkMode;
window.availableColumns = availableColumns;
window.columnsByTable = columnsByTable;
window.plotInstance = plotInstance;
window.updateTime = updateTime;

/**
 * Refresh update time display
 */
function refreshUpdatetime() {
    const display = document.getElementById('countdown');
    display.textContent = remainingTime;

    if (remainingTime > 0) {
        remainingTime--;
    } else {
        startCountdownFromServer();
    }
}

/**
 * Update last updated time display
 */
function updateLastUpdatedTime() {
    const now = new Date();
    const formatted = now.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });

    document.getElementById('last-updated').textContent = `Last updated: ${formatted}`;
}

/**
 * Start countdown timer from server
 */
async function startCountdownFromServer() {
    remainingTime = updateTime;

    if (timerInterval) clearInterval(timerInterval);
    refreshUpdatetime();
    timerInterval = setInterval(refreshUpdatetime, 1000);

    await updateFromDB();
    updateLastUpdatedTime();
}

/**
 * Apply settings from form inputs
 */
async function applySettings() {
    const applyBtn = document.querySelector('.apply-btn');
    const removeLoading = Utils.addLoadingState(applyBtn);

    try {
        // Get values directly from the form
        const formHours = parseInt(document.getElementById('hours').value) || 0;
        const formMinutes = parseInt(document.getElementById('minutes').value) || 0;
        const formSeconds = parseInt(document.getElementById('seconds').value) || 0;
        const formUpdateTime = parseInt(document.getElementById('update_every').value) || 1;

        // Update global variables
        hours = formHours;
        minutes = formMinutes;
        seconds = formSeconds;
        updateTime = formUpdateTime;

        // Update global window variables
        window.hours = hours;
        window.minutes = minutes;
        window.seconds = seconds;
        window.updateTime = updateTime;

        console.log('Form values updated:', { hours, minutes, seconds, updateTime });

        // Get currently selected keys
        const selectedKeys = Array.from(document.querySelectorAll('.parameter-item.selected'))
            .map(item => item.dataset.key);

        if (selectedKeys.length > 0) {
            // Force an immediate data update
            await updateFromDB();
        }

        // Restart the countdown with new update interval
        await startCountdownFromServer();
        
        Utils.showToast('> Settings applied successfully!', 'success');
    } catch (error) {
        console.error('> Error applying settings:', error);
        Utils.showToast('> Error applying settings: ', error);
    } finally {
        removeLoading();
    }
}

/**
 * Call to the DB to get a range of data!
 */
async function applyDateRangeSettings() {
    const applyBtn = document.querySelector('.apply-btn');
    const removeLoading = Utils.addLoadingState(applyBtn);

    try {
        // 1. Get values directly from the form
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        if (!startDate || !endDate) {
            Utils.showToast('> Please select both start and end dates.', 'error');
            return;
        }

        if (new Date(startDate) > new Date(endDate)) {
            Utils.showToast('> Start date must be before end date.', 'error');
            return;
        }

        // 2. Update global variables (mirror applySettings style)
        window.startDate = startDate;
        window.endDate = endDate;

        console.log('> Date range updated:', { startDate, endDate });

        // 3. Get currently selected keys (sidebar params)
        const selectedKeys = Array.from(document.querySelectorAll('.parameter-item.selected'))
            .map(item => item.dataset.key);

        console.log(`> Selected keys are: ${selectedKeys}`)

        if (selectedKeys.length > 0) {
            // Force immediate data update with date filtering
            await updateFromDB();
        }

        // ⏳ Countdown may or may not apply to date range.
        // If you want to keep auto-refresh, uncomment this line:
        // await startCountdownFromServer();

        Utils.showToast('> Date range applied successfully!', 'success');
    } catch (error) {
        console.error('> Error applying date range settings:', error);
        Utils.showToast('> Error applying date range: ', error);
    } finally {
        removeLoading();
    }
}

/**
 * Initialize the application
 */
async function initializeApp() {
    console.log('DOM loaded, initializing...');
    
    // Show the rainbow text immediately when page loads
    updateEmptyChartDisplay();
    
    // Show loading state for data selection
    const sidebar = document.getElementById('data-sidebar');
    sidebar.innerHTML = `
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p>Loading available data columns...</p>
        </div>
    `;

    try {
        // Fetch available columns from database
        console.log('Fetching available columns...');
        availableColumns = await fetchAvailableColumns();
        window.availableColumns = availableColumns;
        console.log('Available columns:', availableColumns);
        
        if (availableColumns.length === 0) {
            sidebar.innerHTML = `
                <div class="error-container">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>No data columns available. Please check if the database is properly configured.</p>
                </div>
            `;
        } else {
            // Create the data selection sidebar
            console.log('Creating data selection sidebar...');
            createDataSelectionSidebar(availableColumns);
            
            // Test the toggle functions
            setTimeout(() => {
                console.log('Testing toggle functions...');
                const testSection = document.querySelector('.data-section');
                if (testSection) {
                    console.log('Found test section:', testSection);
                    const header = testSection.querySelector('.section-header');
                    if (header) {
                        console.log('Found header, adding click test...');
                        header.onclick = () => {
                            console.log('Header clicked!');
                            if (testSection.id === 'qt') {
                                toggleMainSection(testSection.id);
                            } else {
                                toggleMainSection(testSection.id);
                            }
                        };
                    }
                }
            }, 1000);
        }
    } catch (error) {
        console.error('Error during initialization:', error);
        sidebar.innerHTML = `
            <div class="error-container">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error initializing: ${error.message}</p>
            </div>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeApp);

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        refreshUpdatetime,
        updateLastUpdatedTime,
        startCountdownFromServer,
        applySettings,
        applyDateRangeSettings,
        initializeApp
    };
}
