/**
 * Chart and plotting functions for the UVA Lab System Panel
 */

/**
 * Generate evenly spaced time ticks based on time range
 * @param {number} minTime - Minimum timestamp
 * @param {number} maxTime - Maximum timestamp
 * @param {number} numTicks - Number of ticks to generate
 * @returns {Array} - Array of [timestamp, formattedString] pairs
 */
function generateTimeTicks(minTime, maxTime, numTicks = 10) {
    const timeRange = maxTime - minTime;
    const interval = timeRange / (numTicks - 1);
    
    const ticks = [];
    for (let i = 0; i < numTicks; i++) {
        const tickTime = minTime + (i * interval);
        const date = new Date(tickTime);
        
        // Format based on time range
        let timeFormat;
        if (timeRange > 24 * 60 * 60 * 1000) { // > 1 day
            timeFormat = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        } else if (timeRange > 60 * 60 * 1000) { // > 1 hour
            timeFormat = date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        } else if (timeRange > 60 * 1000) { // > 1 minute
            // For ranges under 1 hour, always include AM/PM to avoid confusion
            timeFormat = date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});
        } else { // < 1 minute
            // For very short time ranges, show seconds with milliseconds
            const seconds = date.getSeconds().toString().padStart(2, '0');
            const milliseconds = date.getMilliseconds().toString().padStart(3, '0');
            timeFormat = `${seconds}.${milliseconds}`;
        }
        
        ticks.push([tickTime, timeFormat]);
    }
    
    return ticks;
}

/**
 * Get appropriate y-axis configuration based on data
 * @param {Array} values - Array of values to analyze
 * @returns {Object} - Y-axis configuration object
 */
function getYAxisConfig(values) {
    const needsSciNotation = Utils.needsScientificNotation(values);
    
    console.log('Y-axis config check:', {
        values: values.slice(0, 10), // Log first 10 values
        needsSciNotation: needsSciNotation,
        valueRange: values.length > 0 ? { min: Math.min(...values), max: Math.max(...values) } : 'no values'
    });
    
    if (needsSciNotation) {
        console.log('Using scientific notation for y-axis');
        return {
            axisLabel: 'Value',
            axisLabelUseCanvas: true,
            color: window.isDarkMode ? '#ffffff' : '#333333',
            font: {
                color: window.isDarkMode ? '#ffffff' : '#333333'
            },
            tickColor: window.isDarkMode ? '#ffffff' : '#333333',
            tickFormatter: function(val, axis) {
                console.log('Tick formatter called with:', val);
                return val.toExponential(3);
            },
            transform: function(v) { return v; },
            inverseTransform: function(v) { return v; },
            ticks: function(axis) {
                const ticks = [];
                const min = axis.min;
                const max = axis.max;
                const step = (max - min) / 5;
                
                for (let i = 0; i <= 5; i++) {
                    const val = min + i * step;
                    ticks.push([val, val.toExponential(8)]);
                }
                return ticks;
            }
        };
    } else {
        console.log('Using decimal notation for y-axis');
        return {
            axisLabel: 'Value',
            axisLabelUseCanvas: true,
            color: window.isDarkMode ? '#ffffff' : '#333333',
            font: {
                color: window.isDarkMode ? '#ffffff' : '#333333'
            },
            tickColor: window.isDarkMode ? '#ffffff' : '#333333',
            tickFormatter: function(val, axis) {
                return val.toFixed(8);
            }
        };
    }
}

/**
 * Update the plot with new data
 * @param {Array} data - Data array from database
 * @param {Array} selectedColumns - Array of selected column names
 * @param {Array} availableKeys - Array of available column keys
 */
async function updatePlot(data, selectedColumns, availableKeys = []) {
    console.log('Updating plot with data:', data);
    console.log('Selected columns:', selectedColumns);

    if (!data || !Array.isArray(data) || data.length === 0) {
        console.warn('No data available for plotting');
        const chartContainer = document.getElementById('chart');
        chartContainer.innerHTML = `
            <div class="error-container">
                <i class="fas fa-exclamation-triangle"></i>
                <p>No data available for the selected time range.</p>
            </div>
        `;
        return;
    }

    // Create timestamps array and ensure they're properly parsed
    const timestamps = data.map(point => {
        // Handle raw database row format - timestamp is first element
        const timestamp = typeof point[0] === 'string' ? 
            Date.parse(point[0]) : 
            Number(point[0]);
        return timestamp;
    });

    const plotData = selectedColumns.map(column => {
        // Find the index of this column in the available keys
        const columnIndex = availableKeys.indexOf(column) + 1; // +1 because timestamp is at index 0
        const values = data.map(point => point[columnIndex]);
        const units = Utils.getColumnUnits(column);
        return {
            label: column + units,
            data: timestamps.map((t, i) => [t, values[i]]),
            points: { show: true, radius: 2 },
            lines: { show: false, lineWidth: 1 }
        };
    });

    // Collect all values to determine y-axis formatting
    const allValues = [];
    selectedColumns.forEach(column => {
        const columnIndex = availableKeys.indexOf(column) + 1; // +1 because timestamp is at index 0
        const values = data.map(point => {
            const val = point[columnIndex];
            return val !== null && val !== undefined ? Number(val) : null;
        }).filter(val => val !== null && !isNaN(val));
        allValues.push(...values);
    });

    // Get actual timestamps from data for ticks
    const sortedTimestamps = [...timestamps].sort((a, b) => a - b);
    const minTime = sortedTimestamps[0];
    const maxTime = sortedTimestamps[sortedTimestamps.length - 1];

    const options = {
        xaxis: {
            mode: "time",
            timezone: "browser",
            timeformat: "%H:%M:%S",
            min: minTime,
            max: maxTime,
            ticks: generateTimeTicks(minTime, maxTime, 10),
            tickLength: 5,
            axisLabel: 'Time (EST)',
            axisLabelUseCanvas: true,
            axisLabelFontSizePixels: 12,
            axisLabelFontFamily: 'Inter, sans-serif',
            color: window.isDarkMode ? '#ffffff' : '#333333',
            font: {
                color: window.isDarkMode ? '#ffffff' : '#333333'
            },
            tickColor: window.isDarkMode ? '#ffffff' : '#333333',
        },
        yaxis: getYAxisConfig(allValues),
        legend: {
            position: 'ne',
            backgroundOpacity: 0,
            labelBoxBorderColor: 'transparent',
            show: true,
            noColumns: 1,
            margin: [10, 10],
            labelFormatter: function(label) {
                return label;  
            }
        },
        grid: {
            hoverable: true,
            clickable: true,
            borderWidth: 1,
            color: window.isDarkMode ? '#444444' : '#dddddd',
            backgroundColor: window.isDarkMode ? '#1a1a1a' : '#ffffff'
        },
        tooltip: true,
        tooltipOpts: {
            content: "%s: %y.3",
            xDateFormat: "%Y-%m-%d %H:%M:%S",
            defaultTheme: !window.isDarkMode
        },
    };

    $('#chart').empty();
    if (selectedColumns.length > 0) {
        try {
            window.plotInstance = $.plot($('#chart'), plotData, options);

            // Add hover event for tooltips
            $("#chart").bind("plothover", function (event, pos, item) {
                if (item) {
                    const x = new Date(item.datapoint[0]).toLocaleTimeString();
                    const y = Utils.formatNumber(item.datapoint[1]);
                    const series = item.series.label;
                    
                    $("#tooltip").remove();
                    Utils.showTooltip(item.pageX, item.pageY,
                        `${series}<br>${x}<br>${y}`);
                } else {
                    $("#tooltip").remove();
                }
            });

        } catch (error) {
            console.error('Error plotting data:', error);
            const chartContainer = document.getElementById('chart');
            chartContainer.innerHTML = `
                <div class="error-container">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error plotting data: ${error.message}</p>
                </div>
            `;
        }
    } else {
        updateEmptyChartDisplay();
    }

    // Update chart title
    const titleElement = document.getElementById('chart-title');
    if (selectedColumns.length === 1) {
        titleElement.textContent = `${selectedColumns[0]} vs. Time`;
    } else if (selectedColumns.length === 0) {
        titleElement.textContent = 'No Data Selected';
    } else {
        titleElement.textContent = `Multiple Signals vs. Time`;
    }
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateTimeTicks,
        getYAxisConfig,
        updatePlot
    };
}
