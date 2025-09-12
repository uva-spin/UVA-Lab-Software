/**
 * Data fetching and database operations for the UVA Lab System Panel
 */

/**
 * Fetch data from database based on selected keys and time range
 * @param {Array} selectedKeys - Array of selected column keys
 * @returns {Object} - Object containing data, availableKeys, and missingKeys
 */
async function fetchDataFromDB(selectedKeys) {
    const totalMilliseconds = (window.hours * 3600 + window.minutes * 60 + window.seconds) * 1000;
    const now = new Date();
    const start = new Date(now.getTime() - totalMilliseconds); 
    
    // Format timestamps in YYYY-MM-DD HH:mm:ss format
    const startTimeStr = start.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).replace(',', '');

    const endTimeStr = now.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).replace(',', '');
    
    console.log('Fetching data for time range:', {
        hours: window.hours,
        minutes: window.minutes,
        seconds: window.seconds,
        totalMilliseconds,
        startTime: startTimeStr,
        endTime: endTimeStr,
        humanReadable: `${window.hours}h ${window.minutes}m ${window.seconds}s`
    });
    console.log('Selected keys:', selectedKeys);

    const params = new URLSearchParams();
    params.append('keys', selectedKeys.join(','));
    params.append('start_time', startTimeStr);
    params.append('end_time', endTimeStr);
    
    try {
        const response = await fetch(`/query_db?${params.toString()}`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error('Failed to fetch data from server');
        }

        const result = await response.json();
        console.log('Received data points:', result.data ? result.data.length : 0);
        if (result.data && result.data.length > 0) {
            console.log('Time range of received data:',
                'from', result.data[0][0], // First element is timestamp
                'to', result.data[result.data.length - 1][0] // First element is timestamp
            );
        }
        
        return {
            data: result.data || [],
            availableKeys: result.available_keys || [],
            missingKeys: result.missing_keys || []
        };
    } catch (err) {
        console.error('Error fetching from server:', err);
        throw new Error('Error obtaining data from database. Retrying...');
    }
}

/**
 * Fetch available columns from database
 * @returns {Array} - Array of available column names
 */
async function fetchAvailableColumns() {
    try {
        const response = await fetch('/get_available_columns');
        if (!response.ok) throw new Error('Failed to fetch available columns');
        
        const result = await response.json();
        console.log('Available columns response:', result);
        // Store table->columns map for NMR section
        window.columnsByTable = result.tables || {};
    
        if (result.columns && result.columns.length > 0) {
            return result.columns;
        } else {
            console.warn('No columns available in database');
            return [];
        }
    } catch (err) {
        console.error('Error fetching available columns:', err);
        return [];
    }
}

/**
 * Update data from database and refresh plot
 */
async function updateFromDB() {
    const selectedKeys = Array.from(
        document.querySelectorAll('.parameter-item.selected')
    ).map(item => item.dataset.key);

    if (selectedKeys.length === 0) {
        updateEmptyChartDisplay();
        document.getElementById('chart-title').textContent = 'No Data Selected';
        return;
    }

    try {
        const { data, availableKeys, missingKeys } = await fetchDataFromDB(selectedKeys);
        
        if (missingKeys && missingKeys.length > 0) {
            console.warn('Missing data for keys:', missingKeys);
        }

        await updatePlot(data, selectedKeys, availableKeys);
        
    } catch (error) {
        console.error('Error updating from database:', error);
        const chartContainer = document.getElementById('chart');
        chartContainer.innerHTML = `
            <div class="error-container">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error fetching data: ${error.message}</p>
            </div>
        `;
    }
}

/**
 * Check database status
 */
async function checkDatabaseStatus() {
    try {
        const response = await fetch('/db_status');
        const result = await response.json();
        
        console.log('Database status:', result);
        
        if (result.status === 'ok') {
            alert(`Database Status:\n- Table exists: ${result.table_exists}\n- Total columns: ${result.total_columns}\n- Total records: ${result.total_records}\n- Has data: ${result.has_data}\n\nColumns: ${result.columns.join(', ')}`);
        } else {
            alert(`Database Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error checking database status:', error);
        alert('Error checking database status. Check console for details.');
    }
}

/**
 * Shutdown server function
 */
async function shutdownServer() {
    if (confirm('Are you sure you want to shutdown the server? This action cannot be undone.')) {
        const button = event.target.closest('button');
        const removeLoading = Utils.addLoadingState(button);
        
        try {
            const response = await fetch('/shutdown', { method: 'POST' });
            if (response.ok) {
                Utils.showToast('Server shutdown initiated. The page will close shortly.', 'success');
                setTimeout(() => {
                    window.close();
                }, 2000);
            } else {
                Utils.showToast('Failed to shutdown server. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error shutting down server:', error);
            Utils.showToast('Error shutting down server. Please check the console for details.', 'error');
        } finally {
            removeLoading();
        }
    }
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fetchDataFromDB,
        fetchAvailableColumns,
        updateFromDB,
        checkDatabaseStatus,
        shutdownServer
    };
}
