import React, { useState } from 'react';
import FlexiblePlotlyContainer from '../../containers/FlexiblePlotlyContainer';
import DateTimePicker from '../../components/DateTimePicker';
import DataSelectionDropdown from '../../components/DataSelectionDropdown';
import usePageDataCache from '../../utils/usePageDataCache';
import { fetchDataFromDB } from '../../utils/Query';
import { createTracesFromData } from '../../utils/plotUtils';
import '/src/pages/css/HistoryPage.css';

function Lab42History() {
    const [dateRange, setDateRange] = useState({ start: null, end: null });
    
    // Data structure for dropdowns
    const dataStructure = {
        'QT': {
            'Pressures': ['pt501_ai', 'pt502_ai', 'pt503_ai', 'pt504_ai'],
            'Flows': ['fc501_ai', 'fc501_out', 'fc502_ai', 'fc502_out'],
            'Temperatures': ['ait501_ai', 'ti501_ai', 'ti502_ai', 'ti503_ai', 'ti504_ai', 'ti505_ai', 'ti523_ai'],
            'Level Indicators': ['lit501_ai'],
            'Purity Meter': ['ait501_ai']
        },
        'Pressures': [
            'root_exhaust_pressure', 'buffer_pressure', 'magnet_pressure', 
            'purifier_inlet_pressure', 'fridge_vapor_pressure', 'maxigauge_pressure', 'ivc_pressure'
        ],
        'Temperatures': [
            'thermocouple', 'magnet_bottom_temperature', 'magnet_top_temperature',
            'fridge_target_top_up_temperature', 'fridge_target_top_up_center_temperature',
            'fridge_target_top_down_temperature', 'fridge_target_bottom_up_temperature',
            'fridge_target_bottom_up_center_temperature', 'fridge_target_bottom_down_temperature',
            'fridge_target_top_cernox_temperature', 'fridge_target_bottom_cernox_temperature',
            'magnet_channel_1', 'magnet_channel_2', 'magnet_channel_3', 'magnet_channel_4',
            'magnet_channel_5', 'magnet_channel_6', 'magnet_channel_7', 'magnet_channel_8'
        ],
        'Flows': [
            'separator_flow', 'magnet_flow', 'main_flow', 'microwave_flow', 'heat_exchanger_flow'
        ],
        'NMR': [
            'run_number', 'measurement_type', 'peak_amp', 'peak_center', 'beam_on', 'rf_level',
            'if_atten', 'he_temperature', 'he_pressure', 'nmr_channel', 'temperature',
            'calibration_constant', 'polarization', 'polarization_std', 'snr', 'step_width',
            'center_freq', 'freq_span', 'area', 'phase_voltage', 'tune_voltage'
        ]
    };
    
    // State for selected parameters in each category
    const [selectedData, setSelectedData] = useState({
        qt: [],
        pressures: [],
        temperatures: [],
        flows: [],
        nmr: []
    });
    
    const { 
        data: historyData, 
        isLoading, 
        error, 
        fetchData 
    } = usePageDataCache('lab42-history');
    
    const handleDateRangeChange = (startDate, endDate) => {
        setDateRange({ start: startDate, end: endDate });
    };

    const handleDataSelectionChange = (category, selectedValues) => {
        setSelectedData(prev => ({
            ...prev,
            [category]: selectedValues
        }));
    };
    
    // Get all QT subcategory options flattened
    const getQTOptions = () => {
        const qtOptions = [];
        Object.entries(dataStructure.QT).forEach(([subCategory, items]) => {
            items.forEach(item => {
                qtOptions.push(`${subCategory}: ${item}`);
            });
        });
        return qtOptions;
    };

    // Helper function to check if any data is selected
    const hasSelectedData = () => {
        return Object.values(selectedData).some(category => category.length > 0);
    };

    const fetchHistoryDataFunction = async () => {
        if (!dateRange.start || !dateRange.end) {
            throw new Error('Please select a date range to view historical data');
        }

        if (!hasSelectedData()) {
            throw new Error('Please select at least one parameter to view historical data');
        }

        // Process QT parameters to remove category prefix
        const processedQTParams = selectedData.qt.map(param => {
            // Extract the actual parameter name after the colon
            const match = param.match(/^[^:]+:\s*(.+)$/);
            return match ? match[1].trim() : param;
        });

        // Get all selected parameters from all categories
        const allSelectedParams = [
            ...processedQTParams,
            ...selectedData.pressures,
            ...selectedData.temperatures,
            ...selectedData.flows,
            ...selectedData.nmr
        ];

        console.log('Fetching historical data:', {
            parameters: allSelectedParams,
            timeRange: {
                start: dateRange.start.toLocaleString(),
                end: dateRange.end.toLocaleString()
            }
        });
        
        try {
            const result = await fetchDataFromDB(allSelectedParams, dateRange.start, dateRange.end);
            
            if (!result.data || result.data.length === 0) {
                console.warn('No data returned from database:', {
                    result,
                    parameters: allSelectedParams,
                    timeRange: {
                        start: dateRange.start.toLocaleString(),
                        end: dateRange.end.toLocaleString()
                    }
                });
                throw new Error('No data found for the selected time range and parameters. Please try a different time range or parameters.');
            }

            console.log('Data received:', {
                points: result.data.length,
                availableKeys: result.availableKeys,
                missingKeys: result.missingKeys
            });

            const traces = createTracesFromData(result.data, result.availableKeys, allSelectedParams);
            return traces;
            
        } catch (error) {
            console.error('Error fetching historical data:', error);
            throw error; // Preserve the original error message
        }
    };

    const handleRefreshData = () => {
        if (dateRange.start && dateRange.end && hasSelectedData()) {
            fetchData(fetchHistoryDataFunction);
        }
    };

    const plotConfig = {
        data: historyData || [],
        layout: {
            title: 'Lab 042 Historical Data',
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
            showlegend: true,
            margin: { r: 150, t: 50, b: 50, l: 60 },
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            font: { family: 'Arial, sans-serif' },
            hovermode: 'closest'
        },
        config: {
            displayModeBar: true,
            responsive: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: `lab42_history_${new Date().toLocaleDateString()}`,
                height: 600,
                width: 1000,
                scale: 2
            }
        }
    };

    return (
        <div className="history-page">
            <div className="history-header">
                <h2>Lab 042 Historical Data</h2>
                <div className="history-controls">
                    <DateTimePicker 
                        onDateRangeChange={handleDateRangeChange}
                    />
                    <button 
                        onClick={handleRefreshData} 
                        disabled={isLoading || !dateRange.start || !dateRange.end || !hasSelectedData()}
                        className="refresh-button"
                    >
                        {isLoading ? 'Loading...' : 'Load Historical Data'}
                    </button>
                    <div className="status-indicator">
                        <span className={`status-dot ${isLoading ? 'loading' : 'active'}`}></span>
                        {isLoading ? 'Loading' : 'Ready'}
                    </div>
                </div>
            </div>

            <div className="control-grid">
                <div className="control-section">
                    <h3>Data Selection</h3>
                    <div className="data-selection-grid">
                        <DataSelectionDropdown
                            label="QT Parameters"
                            options={getQTOptions()}
                            selectedValues={selectedData.qt}
                            onSelectionChange={(values) => handleDataSelectionChange('qt', values)}
                            placeholder="Select QT parameters..."
                        />
                        <DataSelectionDropdown
                            label="Pressures"
                            options={dataStructure.Pressures}
                            selectedValues={selectedData.pressures}
                            onSelectionChange={(values) => handleDataSelectionChange('pressures', values)}
                            placeholder="Select pressure sensors..."
                        />
                        <DataSelectionDropdown
                            label="Temperatures"
                            options={dataStructure.Temperatures}
                            selectedValues={selectedData.temperatures}
                            onSelectionChange={(values) => handleDataSelectionChange('temperatures', values)}
                            placeholder="Select temperature sensors..."
                        />
                        <DataSelectionDropdown
                            label="Flows"
                            options={dataStructure.Flows}
                            selectedValues={selectedData.flows}
                            onSelectionChange={(values) => handleDataSelectionChange('flows', values)}
                            placeholder="Select flow sensors..."
                        />
                        <DataSelectionDropdown
                            label="NMR Parameters"
                            options={dataStructure.NMR}
                            selectedValues={selectedData.nmr}
                            onSelectionChange={(values) => handleDataSelectionChange('nmr', values)}
                            placeholder="Select NMR parameters..."
                        />
                    </div>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <p>{error}</p>
                    <button onClick={handleRefreshData}>Retry</button>
                </div>
            )}
            
            <div className="history-plot-container">
                <FlexiblePlotlyContainer 
                    plotId="lab42-history-plot"
                    data={plotConfig.data}
                    layout={plotConfig.layout}
                    config={plotConfig.config}
                />
            </div>
            
            <div className="history-info">
                <h3>Historical Data Information</h3>
                <div className="info-grid">
                    <div className="info-item">
                        <label>Lab:</label>
                        <span>Lab 042</span>
                    </div>
                    <div className="info-item">
                        <label>Data Points:</label>
                        <span>{historyData ? historyData.length : 0}</span>
                    </div>
                    <div className="info-item">
                        <label>Time Range:</label>
                        <span>
                            {dateRange.start && dateRange.end 
                                ? `${dateRange.start.toLocaleDateString()} - ${dateRange.end.toLocaleDateString()}`
                                : 'Not set'
                            }
                        </span>
                    </div>
                    <div className="info-item">
                        <label>Selected Parameters:</label>
                        <span>{Object.values(selectedData).reduce((total, category) => total + category.length, 0)}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Lab42History;