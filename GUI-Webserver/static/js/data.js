/**
 * Data fetching and database operations for the UVA Lab System Panel
 */

/**
 * Fetch data from database based on selected keys and time range
 * @param {Array} selectedKeys - Array of selected column keys
 * @returns {Object} - Object containing data, availableKeys, and missingKeys
 */
async function fetchDataFromDB(selectedKeys) {

    // Print out the "keys"  --- these are the NAMES OF THE SENSORS!
    console.log('> Selected keys:', selectedKeys);

    // If there are NO columns selected...
    if (selectedKeys === undefined) {

        // ... inform the user about that in the console!
        console.log('> Selected keys were undefined!');

        // And throw an error too!
        throw new Error("> You did not select any keys (sensor/data-column names) when making the DB fetch!");
    }

    /**
     * Compute the total number of milliseconds in the interval of time determined by the *global* window
     * properties `hours`, `minutes`, `seconds`.
     */
    const totalMilliseconds = (window.hours * 3600 + window.minutes * 60 + window.seconds) * 1000;

    // Initialize the two obejcts that define the range of the query:
    let start, now;

    // If there *exists* (not null) these window properties...
    if (window.startDate && window.endDate) {

        // FYI: `startDate` and `endDate` come as strings in the form "YYYY-MM-DD":

        // Compute a Date object based on that string for the starting date:
        const startDateObj = new Date(window.startDate);

        // Compute a Date object based on the end date:
        const endDateObj = new Date(window.endDate);

        // If the construction of Date objects was successful...
        if (!isNaN(startDateObj) && !isNaN(endDateObj)) {

            // ... log the start date...
            console.log(`> Start date received: ${window.startDate}`);

            // ... log the end date...
            console.log(`> End date received: ${window.endDate}`);

            // ... and set the `start` variable to corresponding startDate Date object:
            start = startDateObj;
            
            // And do the same of the end date:
            now = endDateObj;

        // If the construction did not work...
        } else {

            /**
             * ... warn the user about the failure to compute a Date(), and revert to the old
             * logic to avoid hangups and/or crashes.
             */
            console.warn("> Invalid date format detected, falling back to timer mode.");
        }
    }

    // If these two variables are *never* defined i.e. nullish...
    if (!start || !now) {

        // ... fall back to the standard logic to define `now`:
        now = new Date();

        // And do the same for `start`:
        start = new Date(now.getTime() - totalMilliseconds);
    }

    console.log(`> After all the logic, we have determined the starting datetime to be: ${start}`);
    console.log(`> We also determined the ending datetime to be: ${now}`);
    
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

    // Construct a new URL params object:
    const params = new URLSearchParams();
    params.append('keys', selectedKeys.join(','));
    params.append('start_time', startTimeStr);
    params.append('end_time', endTimeStr);
    
    try {

        // (X): Fetch to the backend:
        const response = await fetch(`/query_db?${params.toString()}`);

        // (X) Log the response:
        console.log('> Received DB response:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`> Failed to fetch data from server: f{errorText}`);
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

    console.log(`> Selected keys are: ${selectedKeys}`)

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
