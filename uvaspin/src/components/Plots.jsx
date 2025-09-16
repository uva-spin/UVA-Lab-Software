import React, { useState, useEffect, useCallback } from 'react';
import Plot from 'react-plotly.js';
import SidepanelData from './SidepanelData';
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
const fetchDataFromDB = async (selectedKeys, startTime = null, endTime = null, tableName = 'measurements') => {
    const now = new Date();
    const defaultStartTime = startTime || new Date(now.getTime() - 24 * 60 * 60 * 1000); // 24 hours ago
    const defaultEndTime = endTime || now;
    
    const startTimeStr = defaultStartTime.toISOString();
    const endTimeStr = defaultEndTime.toISOString();
    
    const params = new URLSearchParams();
    params.append('keys', selectedKeys.join(','));
    params.append('start_time', startTimeStr);
    params.append('end_time', endTimeStr);
    params.append('table', tableName);
    
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

// Create a mapping from keys to their table names
const createKeyToTableMapping = () => {
    const keyToTable = new Map();
    
    SidepanelData.forEach(table => {
        if (table.columns && Array.isArray(table.columns)) {
            // Handle simple array of keys
            table.columns.forEach(key => {
                keyToTable.set(key, table.title);
            });
        } else if (table.columns && typeof table.columns === 'object') {
            // Handle nested structure (like QT)
            Object.values(table.columns).forEach(columnGroup => {
                if (columnGroup.keys && Array.isArray(columnGroup.keys)) {
                    columnGroup.keys.forEach(key => {
                        keyToTable.set(key, table.title);
                    });
                }
            });
        }
    });
    
    return keyToTable;
};

// Function to determine which table to use based on selected keys
const determineTableFromKeys = (selectedKeys) => {
    const keyToTable = createKeyToTableMapping();
    const tableCounts = new Map();
    
    // Count how many keys belong to each table
    selectedKeys.forEach(key => {
        const table = keyToTable.get(key);
        if (table) {
            tableCounts.set(table, (tableCounts.get(table) || 0) + 1);
        }
    });
    
    // Return the table with the most keys, or default to 'measurements'
    if (tableCounts.size === 0) {
        return 'measurements';
    }
    
    let maxCount = 0;
    let selectedTable = 'measurements';
    
    tableCounts.forEach((count, table) => {
        if (count > maxCount) {
            maxCount = count;
            selectedTable = table;
        }
    });
    
    return selectedTable;
};

// Function to fetch available tables
const fetchAvailableTables = async () => {
    try {
        const response = await fetch('/tables');
        if (!response.ok) {
            throw new Error('Failed to fetch tables');
        }
        const result = await response.json();
        return result.tables || [];
    } catch (err) {
        console.warn('Failed to fetch tables:', err.message);
        return ['measurements']; // Default fallback
    }
};

// Main plotting component
function DataPlot({ selectedParameters, labType = 'lab42', dateRange }) {
    const [plotData, setPlotData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    // Table is now automatically determined based on selected keys

    // Generate plot data from selected parameters
    const generatePlotData = useCallback(async (selectedParams) => {
        if (selectedParams.size === 0) {
            setPlotData([]);
            setError(null);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const selectedKeys = Array.from(selectedParams);
            
            // Use dateRange for history plots, default behavior for others
            let startTime = null;
            let endTime = null;
            
            if (labType === 'history' && dateRange && dateRange.start && dateRange.end) {
                startTime = dateRange.start;
                endTime = dateRange.end;
            }
            
            // Automatically determine the table based on selected keys
            const determinedTable = determineTableFromKeys(selectedKeys);
            console.log(`Selected keys: [${selectedKeys.join(', ')}] -> Using table: ${determinedTable}`);
            
            const { data, availableKeys, missingKeys } = await fetchDataFromDB(selectedKeys, startTime, endTime, determinedTable);
            
            if (missingKeys && missingKeys.length > 0) {
                console.warn('Missing data for keys:', missingKeys);
            }

            if (!data || data.length === 0) {
                setPlotData([]);
                setError('No data available for selected parameters');
                return;
            }

            // Extract timestamps (first column)
            const timestamps = data.map(point => new Date(point[0]));
            
            // Create plot traces for each selected parameter
            const traces = selectedKeys.map((column, index) => {
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

            setPlotData(traces);
            setLastUpdate(new Date());
            
        } catch (err) {
            console.error('Error generating plot data:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [labType, dateRange]);

    // Update plot when selected parameters or date range changes
    useEffect(() => {
        generatePlotData(selectedParameters);
    }, [selectedParameters, generatePlotData]);

    // Auto-refresh only for non-history plots or when no date range is set
    useEffect(() => {
        if (selectedParameters.size === 0) return;
        
        // Don't auto-refresh history plots with custom date ranges
        if (labType === 'history' && dateRange && dateRange.start && dateRange.end) {
            return;
        }

        const interval = setInterval(() => {
            generatePlotData(selectedParameters);
        }, 1000);

        return () => clearInterval(interval);
    }, [selectedParameters, generatePlotData, labType, dateRange]);

    // Determine current table for display
    const currentTable = selectedParameters.size > 0 ? determineTableFromKeys(Array.from(selectedParameters)) : '';

    // Plot layout configuration
    const layout = {
        title: {
            text: selectedParameters.size === 0 
                ? 'No Data Selected' 
                : selectedParameters.size === 1 
                    ? `${Array.from(selectedParameters)[0]} vs. Time (${currentTable})`
                    : `Multiple Signals vs. Time (${currentTable})`,
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
        margin: { r: 200, t: 60, b: 60, l: 80 },
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
                        onClick={() => generatePlotData(selectedParameters)}
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
                    style={{ width: '100%', height: '600px' }}
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
