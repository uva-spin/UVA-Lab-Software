// Plot utilities for data processing and trace creation
import Plotly from 'plotly.js-basic-dist';

const COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
];

/** Shared plot style (font, line width, margins) matching NMR display */
const PLOT_BASE_STYLE = {
    margin: { t: 50, r: 50, b: 50, l: 50 },
    showlegend: true,
    hovermode: 'closest',
    plot_bgcolor: 'white',
    paper_bgcolor: 'white',
    font: { family: 'Arial, sans-serif', size: 12 },
    xaxis: {
        showgrid: true,
        gridcolor: '#e0e0e0',
        zeroline: false,
        tickfont: { size: 11 },
    },
    yaxis: {
        showgrid: true,
        gridcolor: '#e0e0e0',
        zeroline: false,
        tickfont: { size: 11 },
    },
    legend: {
        font: { size: 11 },
        bgcolor: 'rgba(255,255,255,0.8)',
        bordercolor: '#e0e0e0',
        borderwidth: 1,
    },
};

const TRACE_LINE_WIDTH = 2;

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

// Case-insensitive key lookup (DB may return Timestamp, buffer_pressure, etc. with varying case)
function getObjVal(obj, key) {
    if (obj[key] !== undefined) return obj[key];
    const k = Object.keys(obj).find(kk => kk.toLowerCase() === key.toLowerCase());
    return k !== undefined ? obj[k] : undefined;
}

// Build (x, y) arrays for one key from object-format data, excluding null/invalid points
function pointsForKey(data, key) {
    const x = [];
    const y = [];
    for (const point of data) {
        const ts = getObjVal(point, 'timestamp');
        const val = getObjVal(point, key);
        if (ts != null && val != null && !Number.isNaN(Number(val))) {
            x.push(new Date(ts));
            y.push(Number(val));
        }
    }
    return { x, y };
}

// Create plot traces from object-format data. Excludes null data points per key.
function createTracesFromData(data, availableKeys, selectedKeys) {
    if (!data || data.length === 0) return [];

    const isObjectFormat = typeof data[0] === 'object' && !Array.isArray(data[0]);
    if (!isObjectFormat) {
        // Convert array format [timestamp, v1, v2, ...] to object format for unified handling
        data = data.map(row => {
            const obj = { timestamp: row[0] };
            availableKeys.forEach((k, i) => { obj[k] = row[i + 1]; });
            return obj;
        });
    }

    return selectedKeys.map((column, index) => {
        const { x, y } = pointsForKey(data, column);
        const units = getColumnUnits(column);
        const color = COLOR_PALETTE[index % COLOR_PALETTE.length];
        return {
            x,
            y,
            type: 'scatter',
            mode: 'lines',
            name: column + units,
            line: { color, width: TRACE_LINE_WIDTH },
            hovertemplate: '<b>%{fullData.name}</b><br>Time: %{x}<br>Value: %{y}<br><extra></extra>',
            connectgaps: false,
        };
    });
};

// Function to extend existing traces with new data
function extendTracesWithData(plotRef, newData, availableKeys, selectedKeys) {
    if (!newData || newData.length === 0 || !plotRef.current) {
        console.log('Cannot extend traces: no data or plot ref not available');
        return;
    }
    
    // Prepare extension data for each trace, excluding null values
    const extensionData = selectedKeys.map((column) => {
        const x = [];
        const y = [];
        for (const point of newData) {
            const ts = getObjVal(point, 'timestamp');
            const val = getObjVal(point, column);
            if (ts != null && val != null && !Number.isNaN(Number(val))) {
                x.push(new Date(ts));
                y.push(Number(val));
            }
        }
        return {
            x: [x],
            y: [y]
        };
    });
    
    // Use Plotly.extendTraces to add new data
    Plotly.extendTraces(plotRef.current, extensionData, Array.from({length: selectedKeys.length}, (_, i) => i));
    
    // Check if we need to limit data points to prevent memory issues
    // const maxPoints = 100000;
    // if (newTimestamps.length > maxPoints) {
    //     // Get current data lengths
    //     const currentData = plotRef.current.data;
    //     const currentLength = currentData[0]?.x?.length || 0;
        
    //     if (currentLength > maxPoints) {
    //         // Remove old data points by keeping only the last maxPoints
    //         const removeCount = currentLength - maxPoints;
    //         Plotly.relayout(plotRef.current, {
    //             'xaxis.range': [newTimestamps[Math.max(0, newTimestamps.length - maxPoints)], newTimestamps[newTimestamps.length - 1]]
    //         });
    //     }
    // }
    };

// Function to merge new data with existing cached data
function mergeDataWithCache(newData, selectedKeys, availableKeys, cachedData) {
    if (!newData || newData.length === 0) return { data: [], lastTimestamp: null };
    
    const newCachedData = new Map(cachedData);
    const newLastTimestamp = getObjVal(newData[newData.length - 1], 'timestamp');
    
    // For each selected key, merge new data with cached data (exclude null values)
    selectedKeys.forEach(key => {
        const existingData = newCachedData.get(key) || [];
        const newValues = newData
            .map(point => [getObjVal(point, 'timestamp'), getObjVal(point, key)])
            .filter(([ts, val]) => ts != null && val != null && !Number.isNaN(Number(val)));
        
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
    
    // Reconstruct as object format for createTracesFromData; include rows with any valid values
    const allTimestamps = Array.from(new Set(
        Array.from(newCachedData.values())
            .flat()
            .map(point => point[0])
    )).sort((a, b) => new Date(a) - new Date(b));
    
    const reconstructedData = allTimestamps
        .map(timestamp => {
            const row = { timestamp };
            let hasAny = false;
            selectedKeys.forEach(key => {
                const keyData = newCachedData.get(key) || [];
                const point = keyData.find(p => p[0] === timestamp);
                if (point && point[1] != null && !Number.isNaN(Number(point[1]))) {
                    row[key] = Number(point[1]);
                    hasAny = true;
                }
            });
            return hasAny ? row : null;
        })
        .filter(row => row !== null);
    
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
            timestamps = data.map(point => new Date(getObjVal(point, 'timestamp')));
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
        ...PLOT_BASE_STYLE,
        xaxis: {
            ...PLOT_BASE_STYLE.xaxis,
            title: { text: 'Time (EST)', font: { size: 12 } },
            type: 'date',
            range: xaxisRange,
        },
        yaxis: {
            ...PLOT_BASE_STYLE.yaxis,
            title: { text: 'Value', font: { size: 12 } },
        },
        legend: {
            ...PLOT_BASE_STYLE.legend,
            orientation: 'v',
            x: 1.02,
            y: 1,
        },
        margin: { ...PLOT_BASE_STYLE.margin, r: 80 },
        width: width,
        height: height,
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

/** Shared layout/config for History, Averaging, NMR pages - NMR-style look */
export function getTimeSeriesPlotConfig(title, filenamePrefix = 'plot') {
  return {
    layout: {
      ...PLOT_BASE_STYLE,
      autosize: true,
      xaxis: {
        ...PLOT_BASE_STYLE.xaxis,
        title: { text: 'Time (EST)', font: { size: 12 } },
        type: 'date',
      },
      yaxis: {
        ...PLOT_BASE_STYLE.yaxis,
        title: { text: 'Value', font: { size: 12 } },
      },
      legend: {
        ...PLOT_BASE_STYLE.legend,
        orientation: 'v',
        x: 1.02,
        y: 1,
        xanchor: 'left',
      },
    },
    config: {
      displayModeBar: true,
      responsive: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
      toImageButtonOptions: {
        format: 'png',
        filename: `${filenamePrefix}_${new Date().toISOString().split('T')[0]}`,
        height: 600,
        width: 1000,
        scale: 2,
      },
    },
  };
}

export const LAB_COLORS = { lab42: '#667eea', lab36: '#764ba2' };
export { PLOT_BASE_STYLE, TRACE_LINE_WIDTH };

export { getColumnUnits, getObjVal, shouldComponentUpdate, createTracesFromData, extendTracesWithData, mergeDataWithCache, getPlotLayout, getPlotConfig };