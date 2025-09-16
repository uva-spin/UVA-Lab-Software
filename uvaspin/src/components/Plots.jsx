import React, { useState, useEffect, useCallback } from 'react';
import Plot from 'react-plotly.js';
import { useDataSelection } from '../utils/useDataSelection';

const COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
];

const getColumnUnits = (column) => {
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

const formatNumber = (value) => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    if (Math.abs(value) < 0.001 || Math.abs(value) > 1000000) {
        return value.toExponential(3);
    }
    return value.toFixed(3);
};

// Data fetching function
const fetchDataFromDB = async (selectedKeys, startTime = null, endTime = null) => {
    const now = new Date();
    const defaultStartTime = startTime || new Date(now.getTime() - 24 * 60 * 60 * 1000); // 24 hours ago
    const defaultEndTime = endTime || now;
    
    const startTimeStr = defaultStartTime.toISOString();
    const endTimeStr = defaultEndTime.toISOString();
    
    const params = new URLSearchParams();
    params.append('keys', selectedKeys.join(','));
    params.append('start_time', startTimeStr);
    params.append('end_time', endTimeStr);
    
    try {
        const response = await fetch(`/query_db?${params.toString()}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error('Failed to fetch data from server');
        }

        const result = await response.json();
        console.log('Received data points:', result.data ? result.data.length : 0);
        
        return {
            data: result.data || [],
            availableKeys: result.available_keys || [],
            missingKeys: result.missing_keys || []
        };
    } catch (err) {
        console.warn('Database connection failed, returning empty data:', err.message);
        
        // Return empty data when database is not available
        return {
            data: [],
            availableKeys: [],
            missingKeys: selectedKeys
        };
    }
};

// Main plotting component
function DataPlot({ selectedParameters, labType = 'lab42', dateRange }) {
    const [plotData, setPlotData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [cachedData, setCachedData] = useState(new Map()); // Cache for existing data
    const [lastTimestamp, setLastTimestamp] = useState(null); // Track last data timestamp

    // Function to create plot traces from data
    const createTracesFromData = useCallback((data, availableKeys, selectedKeys) => {
        if (!data || data.length === 0) return [];
        
        // Extract timestamps (first column)
        const timestamps = data.map(point => new Date(point[0]));
        
        // Create plot traces for each selected parameter
        return selectedKeys.map((column, index) => {
            const columnIndex = availableKeys.indexOf(column) + 1; // +1 because timestamp is at index 0
            const values = data.map(point => point[columnIndex]);
            const units = getColumnUnits(column);
            
            return {
                x: timestamps,
                y: values,
                type: 'scatter',
                mode: 'markers+lines',
                name: column + units,
                line: { 
                    width: 2,
                    color: COLOR_PALETTE[index % COLOR_PALETTE.length]
                },
                marker: { 
                    size: 4,
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
    }, []);

    // Function to merge new data with existing cached data
    const mergeDataWithCache = useCallback((newData, selectedKeys, availableKeys) => {
        if (!newData || newData.length === 0) return { data: [], lastTimestamp: null };
        
        const newCachedData = new Map(cachedData);
        const newLastTimestamp = newData[newData.length - 1][0]; // Last timestamp
        
        // For each selected key, merge new data with cached data
        selectedKeys.forEach(key => {
            const columnIndex = availableKeys.indexOf(key) + 1;
            const existingData = newCachedData.get(key) || [];
            const newValues = newData.map(point => [point[0], point[columnIndex]]); // [timestamp, value]
            
            // Merge and sort by timestamp, removing duplicates
            const mergedData = [...existingData, ...newValues]
                .sort((a, b) => new Date(a[0]) - new Date(b[0]))
                .filter((point, index, arr) => 
                    index === 0 || point[0] !== arr[index - 1][0]
                );
            
            // Keep only last 1000 points to prevent memory issues
            if (mergedData.length > 1000) {
                mergedData.splice(0, mergedData.length - 1000);
            }
            
            newCachedData.set(key, mergedData);
        });
        
        setCachedData(newCachedData);
        setLastTimestamp(newLastTimestamp);
        
        // Reconstruct the data array in the original format
        const allTimestamps = Array.from(new Set(
            Array.from(newCachedData.values())
                .flat()
                .map(point => point[0])
        )).sort((a, b) => new Date(a) - new Date(b));
        
        const reconstructedData = allTimestamps.map(timestamp => {
            const row = [timestamp];
            selectedKeys.forEach(key => {
                const keyData = newCachedData.get(key) || [];
                const point = keyData.find(p => p[0] === timestamp);
                row.push(point ? point[1] : null);
            });
            return row;
        });
        
        return { data: reconstructedData, lastTimestamp: newLastTimestamp };
    }, [cachedData]);

    // Generate plot data from selected parameters
    const generatePlotData = useCallback(async (selectedParams, isIncremental = false) => {
        if (selectedParams.size === 0) {
            setPlotData([]);
            setError(null);
            setCachedData(new Map());
            setLastTimestamp(null);
            return;
        }

        // Only show loading for initial load, not incremental updates
        if (!isIncremental) {
            setLoading(true);
        }
        setError(null);

        try {
            const selectedKeys = Array.from(selectedParams);
            
            // Use dateRange for history plots, default behavior for others
            let startTime = null;
            let endTime = null;
            
            if (labType === 'history' && dateRange && dateRange.start && dateRange.end) {
                startTime = dateRange.start;
                endTime = dateRange.end;
            } else if (isIncremental && lastTimestamp) {
                // For incremental updates, only fetch data after the last timestamp
                startTime = new Date(lastTimestamp);
                endTime = new Date();
            }
            
            const { data, availableKeys, missingKeys } = await fetchDataFromDB(selectedKeys, startTime, endTime);
            
            if (missingKeys && missingKeys.length > 0) {
                console.warn('Missing data for keys:', missingKeys);
            }

            if (!data || data.length === 0) {
                if (!isIncremental) {
                    setPlotData([]);
                    setError('No data available for selected parameters');
                }
                return;
            }

            let finalData = data;
            let finalLastTimestamp = data[data.length - 1][0];
            
            if (isIncremental) {
                // Merge with cached data for incremental updates
                const merged = mergeDataWithCache(data, selectedKeys, availableKeys);
                finalData = merged.data;
                finalLastTimestamp = merged.lastTimestamp;
            } else {
                // For initial load, cache the data
                const merged = mergeDataWithCache(data, selectedKeys, availableKeys);
                finalData = merged.data;
                finalLastTimestamp = merged.lastTimestamp;
            }

            // Create traces from the final data
            const traces = createTracesFromData(finalData, availableKeys, selectedKeys);
            setPlotData(traces);
            setLastUpdate(new Date());
            
        } catch (err) {
            console.error('Error generating plot data:', err);
            if (!isIncremental) {
                setError(err.message);
            }
        } finally {
            if (!isIncremental) {
                setLoading(false);
            }
        }
    }, [labType, dateRange, lastTimestamp, mergeDataWithCache, createTracesFromData]);

    // Update plot when selected parameters or date range changes
    useEffect(() => {
        // Clear cache when parameters change to ensure fresh data
        setCachedData(new Map());
        setLastTimestamp(null);
        generatePlotData(selectedParameters, false); // Full refresh for parameter changes
    }, [selectedParameters, generatePlotData]);

    // Auto-refresh only for non-history plots or when no date range is set
    useEffect(() => {
        if (selectedParameters.size === 0) return;
        
        // Don't auto-refresh history plots with custom date ranges
        if (labType === 'history' && dateRange && dateRange.start && dateRange.end) {
            return;
        }

        const interval = setInterval(() => {
            generatePlotData(selectedParameters, true); // Use incremental updates
        }, 1000);

        return () => clearInterval(interval);
    }, [selectedParameters, generatePlotData, labType, dateRange]);

    // Plot layout configuration
    const layout = {
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
            zeroline: false
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
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { family: 'Arial, sans-serif' },
        hovermode: 'closest',
        showlegend: true
    };

    // Plot configuration
    const config = {
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: `${labType}_plot_${new Date().toISOString().split('T')[0]}`,
            height: 600,
            width: 1000,
            scale: 2
        }
    };

    if (loading) {
        return (
            <div className="plot-container loading">
                <div className="loading-spinner">
                    <i className="fas fa-spinner fa-spin"></i>
                    <p>Loading data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="plot-container error">
                <div className="error-message">
                    <i className="fas fa-exclamation-triangle"></i>
                    <h3>Error Loading Data</h3>
                    <p>{error}</p>
                    <button 
                        className="retry-button"
                        onClick={() => generatePlotData(selectedParameters)}
                    >
                        <i className="fas fa-redo"></i> Retry
                    </button>
                </div>
            </div>
        );
    }

    if (selectedParameters.size === 0) {
        return (
            <div className="plot-container empty">
                <div className="empty-message">
                    <i className="fas fa-chart-line"></i>
                    <h3>Select Data to Plot</h3>
                    <p>Choose parameters from the sidebar to display on the plot</p>
                </div>
            </div>
        );
    }

    return (
        <div className="plot-container">
            <div className="plot-header">
                <div className="plot-info">
                    <span className="parameter-count">
                        {selectedParameters.size} parameter{selectedParameters.size !== 1 ? 's' : ''} selected
                    </span>
                    {lastUpdate && (
                        <span className="last-update">
                            Last updated: {lastUpdate.toLocaleTimeString()}
                        </span>
                    )}
                </div>
                <div className="plot-controls">
                    <button 
                        className="refresh-button"
                        onClick={() => generatePlotData(selectedParameters, true)}
                        title="Refresh Data"
                    >
                        <i className="fas fa-sync-alt"></i>
                    </button>
                </div>
            </div>
            
            <div className="plot-wrapper">
                <Plot
                    data={plotData}
                    layout={layout}
                    config={config}
                    style={{ width: '100%', height: '100%', minHeight: '400px' }}
                    onInitialized={(figure, graphDiv) => {
                        console.log('Plot initialized');
                    }}
                    onUpdate={(figure, graphDiv) => {
                        console.log('Plot updated');
                    }}
                />
            </div>
        </div>
    );
}


// Lab-specific plot components
function Lab42Plot({ selectedParameters }) {
    return <DataPlot selectedParameters={selectedParameters} labType="lab42" />;
}

function Lab36Plot({ selectedParameters }) {
    return <DataPlot selectedParameters={selectedParameters} labType="lab36" />;
}

function HistoryPlot({ selectedParameters, dateRange }) {
    return <DataPlot selectedParameters={selectedParameters} labType="history" dateRange={dateRange} />;
}

export { Lab42Plot, Lab36Plot, HistoryPlot, DataPlot };
