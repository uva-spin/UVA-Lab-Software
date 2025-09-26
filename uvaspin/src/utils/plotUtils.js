// Plot utilities for data processing and trace creation
import Plotly from 'plotly.js-basic-dist';

const COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
];

function getColumnUnits(column) {
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
        return '';
    }
};

function shouldComponentUpdate(nextProps, currentProps) {
    if (currentProps.height !== nextProps.height ||
       currentProps.width !== nextProps.width) {
      return true;
    }

    return false;
  }
export const formatNumber = (value) => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    if (Math.abs(value) < 0.001 || Math.abs(value) > 1000000) {
        return value.toExponential(3);
    }
    return value.toFixed(3);
};

function scaleValues(values) {
    // Filter out null/undefined values for calculation
    const validValues = values.filter(value => value !== null && value !== undefined && !isNaN(value));
    
    if (validValues.length === 0) {
        return values; // Return original if no valid values
    }
    
    // Find maximum absolute value in valid values to avoid division by zero
    const maxValue = Math.max(...validValues.map(Math.abs));
    
    if (maxValue === 0) {
        return values; // Return original if all values are zero
    }
    
    // Divide each value by the maximum value to get relative scaling factor
    const scaledValues = values.map(value => {
        if (value === null || value === undefined || isNaN(value)) {
            return null; // Preserve null/undefined values
        }
        return value / maxValue;
    });
    
    return scaledValues;
};

// Note: Data sampling is now handled in dataProcessor.js before traces are created

// Function to create plot traces from data (data is already sampled in dataProcessor.js)
function createTracesFromData(data, availableKeys, selectedKeys) {
    if (!data || data.length === 0) return [];
    
    // Data is already sampled in dataProcessor.js, so we work with the provided data directly
    console.log('Selected keys:', selectedKeys);
    console.log(`Creating traces from ${data.length} data points (already sampled)`);
    
    // Log data timestamp range for verification
    if (data.length > 0) {
        console.log('Data timestamp range:', 
            data[0].timestamp || data[0][0], 
            'to', 
            data[data.length - 1].timestamp || data[data.length - 1][0]
        );
    }
    
    // Detect data format: object format vs array format
    const isObjectFormat = data.length > 0 && typeof data[0] === 'object' && !Array.isArray(data[0]);
    console.log('Data format detected:', isObjectFormat ? 'object' : 'array');
    
    let timestamps, valuesByKey;
    
    if (isObjectFormat) {
        // Object format: [{timestamp: ..., pt501_ai: ..., pt502_ai: ...}, ...]
        timestamps = data.map(point => new Date(point.timestamp));
        valuesByKey = {};
        selectedKeys.forEach(key => {
            valuesByKey[key] = data.map(point => point[key]);
        });
    } else {
        // Array format: [["timestamp", val1, val2, ...], ...] or [[val1, val2, ..., "timestamp"], ...]
        // Check if timestamp is first or last element
        const firstPoint = data[0];
        const lastElement = firstPoint[firstPoint.length - 1];
        const firstElement = firstPoint[0];
        
        // Check if last element looks like a timestamp (contains 'T' or is a date string)
        const isTimestampLast = typeof lastElement === 'string' && (lastElement.includes('T') || lastElement.includes('-'));
        
        if (isTimestampLast) {
            // Timestamp is last: [val1, val2, ..., timestamp]
            timestamps = data.map(point => new Date(point[point.length - 1]));
            valuesByKey = {};
            selectedKeys.forEach((key, index) => {
                const columnIndex = availableKeys.indexOf(key);
                valuesByKey[key] = data.map(point => point[columnIndex]);
            });
        } else {
            // Timestamp is first: [timestamp, val1, val2, ...]
            timestamps = data.map(point => new Date(point[0]));
            valuesByKey = {};
            selectedKeys.forEach((key, index) => {
                const columnIndex = availableKeys.indexOf(key) + 1; // +1 because timestamp is at index 0
                valuesByKey[key] = data.map(point => point[columnIndex]);
            });
        }
    }
    
    console.log('Timestamps:', timestamps);
    
    // Create plot traces for each selected parameter
    return selectedKeys.map((column, index) => {
        const values = valuesByKey[column] || [];
        const units = getColumnUnits(column);
        const scaledValues = scaleValues(values);
        // console.log(`Column ${column} values:`, values);
        
        return {
            x: timestamps,
            y: scaledValues,
            type: 'scatter',
            mode: 'markers',
            name: column + units,
            marker: { 
                size: 6,
                color: COLOR_PALETTE[index % COLOR_PALETTE.length]
            },
            hovertemplate: 
                '<b>%{fullData.name}</b><br>' +
                'Time: %{x}<br>' +
                'Value: %{y}<br>' +
                '<extra></extra>',
            connectgaps: false
        };
    });
};

// Function to extend existing traces with new data
function extendTracesWithData(plotRef, newData, availableKeys, selectedKeys) {
    if (!newData || newData.length === 0 || !plotRef.current) {
        console.log('Cannot extend traces: no data or plot ref not available');
        return;
    }
    
    // Extract timestamps and values from object format
    const newTimestamps = newData.map(point => new Date(point.timestamp));
    console.log('Extending traces with data from', newTimestamps[0], 'to', newTimestamps[newTimestamps.length - 1]);
    
    // Prepare extension data for each trace
    const extensionData = selectedKeys.map((column, index) => {
        const newValues = newData.map(point => point[column]);
        
        return {
            x: [newTimestamps],
            y: [newValues]
        };
    });
    
    // Use Plotly.extendTraces to add new data
    Plotly.extendTraces(plotRef.current, extensionData, Array.from({length: selectedKeys.length}, (_, i) => i));
    
    // Check if we need to limit data points to prevent memory issues
    const maxPoints = 100000;
    if (newTimestamps.length > maxPoints) {
        // Get current data lengths
        const currentData = plotRef.current.data;
        const currentLength = currentData[0]?.x?.length || 0;
        
        if (currentLength > maxPoints) {
            // Remove old data points by keeping only the last maxPoints
            const removeCount = currentLength - maxPoints;
            Plotly.relayout(plotRef.current, {
                'xaxis.range': [newTimestamps[Math.max(0, newTimestamps.length - maxPoints)], newTimestamps[newTimestamps.length - 1]]
            });
        }
    }
};

// Function to merge new data with existing cached data
function mergeDataWithCache(newData, selectedKeys, availableKeys, cachedData) {
    if (!newData || newData.length === 0) return { data: [], lastTimestamp: null };
    
    const newCachedData = new Map(cachedData);
    const newLastTimestamp = newData[newData.length - 1].timestamp;
    
    // For each selected key, merge new data with cached data
    selectedKeys.forEach(key => {
        const existingData = newCachedData.get(key) || [];
        const newValues = newData.map(point => [point.timestamp, point[key]]); // [timestamp, value]
        
        // Merge and sort by timestamp, removing duplicates
        const mergedData = [...existingData, ...newValues]
            .sort((a, b) => new Date(a[0]) - new Date(b[0]))
            .filter((point, index, arr) => 
                index === 0 || point[0] !== arr[index - 1][0]
            );
        
        // Remove cache limit - we'll handle sampling in the plotting function instead
        // This allows us to keep all historical data and sample it for display
        
        newCachedData.set(key, mergedData);
    });
    
    // Reconstruct the data array in the original format
    // Only include timestamps where ALL selected keys have valid data points
    const allTimestamps = Array.from(new Set(
        Array.from(newCachedData.values())
            .flat()
            .map(point => point[0])
    )).sort((a, b) => new Date(a) - new Date(b));
    
    const reconstructedData = allTimestamps
        .map(timestamp => {
            const row = [timestamp];
            let hasAllValues = true;
            
            selectedKeys.forEach(key => {
                const keyData = newCachedData.get(key) || [];
                const point = keyData.find(p => p[0] === timestamp);
                if (point && point[1] !== null && point[1] !== undefined) {
                    row.push(point[1]);
                } else {
                    hasAllValues = false;
                }
            });
            
            return hasAllValues ? row : null;
        })
        .filter(row => row !== null); // Remove rows where not all parameters have values
    
    console.log(`Data reconstruction: ${allTimestamps.length} total timestamps, ${reconstructedData.length} valid data points (with all parameters)`);
    
    return { 
        data: reconstructedData, 
        lastTimestamp: newLastTimestamp,
        cachedData: newCachedData
    };
};

// Plot layout configuration
function getPlotLayout(selectedParameters, data = null, dimensions = null) {
    let xaxisRange = undefined;
    
    // If data is provided, calculate the proper x-axis range
    if (data && data.length > 0) {
        let timestamps;
        
        // Note: We use the original data (not sampled) to get the true time range
        // This ensures the x-axis shows the full time span even with sampled points
        
        // Detect data format and extract timestamps accordingly
        const isObjectFormat = data.length > 0 && typeof data[0] === 'object' && !Array.isArray(data[0]);
        
        if (isObjectFormat) {
            // Object format: [{timestamp: ..., pt501_ai: ..., pt502_ai: ...}, ...]
            timestamps = data.map(point => new Date(point.timestamp));
        } else {
            // Array format: detect if timestamp is first or last
            const firstPoint = data[0];
            const lastElement = firstPoint[firstPoint.length - 1];
            const isTimestampLast = typeof lastElement === 'string' && (lastElement.includes('T') || lastElement.includes('-'));
            
            if (isTimestampLast) {
                // Timestamp is last: [val1, val2, ..., timestamp]
                timestamps = data.map(point => new Date(point[point.length - 1]));
            } else {
                // Timestamp is first: [timestamp, val1, val2, ...]
                timestamps = data.map(point => new Date(point[0]));
            }
        }
        
        const minTime = new Date(Math.min(...timestamps));
        const maxTime = new Date(Math.max(...timestamps));
        
        // Add some padding to the range (5% on each side)
        const timeRange = maxTime.getTime() - minTime.getTime();
        // const padding = timeRange * 0.05;
        
        xaxisRange = [
            new Date(minTime.getTime()),
            new Date(maxTime.getTime())
        ];
        
        console.log('Setting x-axis range:', xaxisRange);
    }
    
    // Calculate dynamic dimensions if provided
    let width = undefined;
    let height = undefined;
    
    if (dimensions && dimensions.width > 0 && dimensions.height > 0) {
        width = Math.max(300, dimensions.width - 20); // Account for container padding
        height = Math.max(400, dimensions.height - 120); // Account for header and margins
    }
    
    return {
        title: {
            text: selectedParameters.size === 0 
                ? 'No Data Selected' 
                : selectedParameters.size === 1 
                    ? `${Array.from(selectedParameters)[0]} vs. Time`
                    : 'Multiple Signals vs. Time',
            font: { size: 18, color: '#333' }
        },
        xaxis: {
            title: 'Time (EST)',
            type: 'date',
            showgrid: true,
            gridcolor: '#e0e0e0',
            zeroline: false,
            range: xaxisRange
        },
        yaxis: {
            title: 'Value',
            showgrid: true,
            gridcolor: '#e0e0e0',
            zeroline: false
        },
        legend: {
            orientation: 'v',
            x: 1.02,
            y: 1,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: '#ccc',
            borderwidth: 1
        },
        margin: { r: 150, t: 50, b: 50, l: 60 },
        width: width,
        height: height,
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif' },
        hovermode: 'closest',
        showlegend: true
    };
};

// Plot configuration
function getPlotConfig(labType) {
    return {
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        modeBarButtons: [
            ['toImage', 'zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
        ],
        toImageButtonOptions: {
            format: 'png',
            filename: `${labType}_plot_${new Date().toLocaleString()}`,
            height: 600,
            width: 1000,
            scale: 2
        }
    };
};

export { getColumnUnits, shouldComponentUpdate, createTracesFromData, extendTracesWithData, mergeDataWithCache, getPlotLayout, getPlotConfig };