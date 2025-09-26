import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js-basic-dist';
import FlexiblePlotlyContainer from '../../containers/FlexiblePlotlyContainer';
import DateTimePicker from '../../components/DateTimePicker';
import DataSelectionDropdown from '../../components/DataSelectionDropdown';
import { useDataSelection } from '../../utils/useDataSelection';
import usePageDataCache from '../../utils/usePageDataCache';
import '/src/pages/css/HistoryPage.css';

function Lab36History() {
    const { selectedParameters } = useDataSelection();
    const [dateRange, setDateRange] = useState({ start: null, end: null });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // Data structure for dropdowns (matching the sidebar structure)
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
        isLoading: cacheLoading, 
        error: cacheError, 
        fetchData, 
        clearCache 
    } = usePageDataCache('lab36-history');
    
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

    const fetchHistoryDataFunction = async () => {
        if (!dateRange.start || !dateRange.end) {
            throw new Error('Please select a date range to view historical data');
        }

        // TODO: Implement actual historical data fetching logic here
        // This is a template for you to add your history-specific functionality
        
        // Example placeholder data structure
        const mockData = {
            time: Array.from({ length: 200 }, (_, i) => 
                new Date(dateRange.start.getTime() + (i / 200) * (dateRange.end.getTime() - dateRange.start.getTime()))
            ),
            temperature: Array.from({ length: 200 }, (_, i) => 
                18 + Math.sin(i * 0.12) * 4 + Math.random() * 1.5
            ),
            pressure: Array.from({ length: 200 }, (_, i) => 
                1008 + Math.cos(i * 0.18) * 8 + Math.random() * 2.5
            ),
            magneticField: Array.from({ length: 200 }, (_, i) => 
                1.2 + Math.sin(i * 0.09) * 0.15 + Math.random() * 0.08
            )
        };
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        return mockData;
    };

    const handleRefreshData = () => {
        if (dateRange.start && dateRange.end) {
            fetchData(fetchHistoryDataFunction);
        }
    };

    const plotConfig = {
        data: historyData ? [
            {
                x: historyData.time,
                y: historyData.temperature,
                type: 'scatter',
                mode: 'lines',
                name: 'Temperature (°C)',
                line: { color: '#e74c3c', width: 2 }
            },
            {
                x: historyData.time,
                y: historyData.pressure,
                type: 'scatter',
                mode: 'lines',
                name: 'Pressure (mbar)',
                line: { color: '#3498db', width: 2 },
                yaxis: 'y2'
            },
            {
                x: historyData.time,
                y: historyData.magneticField,
                type: 'scatter',
                mode: 'lines',
                name: 'Magnetic Field (T)',
                line: { color: '#2ecc71', width: 2 },
                yaxis: 'y3'
            }
        ] : [],
        layout: {
            title: 'Lab 036 Historical Data',
            xaxis: { 
                title: 'Time',
                type: 'date'
            },
            yaxis: { 
                title: 'Temperature (°C)',
                side: 'left',
                color: '#e74c3c'
            },
            yaxis2: {
                title: 'Pressure (mbar)',
                side: 'right',
                overlaying: 'y',
                color: '#3498db'
            },
            yaxis3: {
                title: 'Magnetic Field (T)',
                side: 'right',
                overlaying: 'y',
                position: 0.85,
                color: '#2ecc71'
            },
            showlegend: true,
            margin: { t: 50, r: 100, b: 50, l: 50 },
            hovermode: 'closest'
        },
        config: {
            displayModeBar: true,
            responsive: true
        }
    };

    return (
        <div className="history-page">
            <div className="history-header">
                <h2>Lab 036 Historical Data</h2>
                <div className="history-controls">
                    <button 
                        onClick={handleRefreshData} 
                        disabled={cacheLoading || !dateRange.start || !dateRange.end}
                        className="refresh-button"
                    >
                        {cacheLoading ? 'Loading...' : 'Load Historical Data'}
                    </button>
                    <div className="status-indicator">
                        <span className={`status-dot ${cacheLoading ? 'loading' : 'active'}`}></span>
                        {cacheLoading ? 'Loading' : 'Ready'}
                    </div>
                </div>
            </div>

            <div className="control-grid">
                <div className="control-section">
                    <h3>Time Range Selection</h3>
                    <DateTimePicker 
                        onDateRangeChange={handleDateRangeChange}
                    />
                </div>
                
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

            {cacheError && (
                <div className="error-message">
                    <p>{cacheError}</p>
                    <button onClick={handleRefreshData}>Retry</button>
                </div>
            )}
            
            <div className="history-plot-container">
                <FlexiblePlotlyContainer 
                    plotId="lab36-history-plot"
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
                        <span>Lab 036</span>
                    </div>
                    <div className="info-item">
                        <label>Data Points:</label>
                        <span>{historyData ? historyData.time.length : 0}</span>
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
                        <label>Last Update:</label>
                        <span>{new Date().toLocaleTimeString()}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Lab36History;
