import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js-basic-dist';
import FlexiblePlotlyContainer from '../../containers/FlexiblePlotlyContainer';
import DateTimePicker from '../../components/DateTimePicker';
import DataSelectionDropdown from '../../components/DataSelectionDropdown';
import { useDataSelection } from '../../utils/useDataSelection';
import usePageDataCache from '../../utils/usePageDataCache';
import '/src/pages/css/AveragingPage.css';

function Lab42Averaging() {
    const { selectedParameters } = useDataSelection();
    const [nPoints, setNPoints] = useState(10);
    const [samplingFactor, setSamplingFactor] = useState(1);
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
    
    const handleDataSelectionChange = (category, selectedValues) => {
        setSelectedData(prev => ({
            ...prev,
            [category]: selectedValues
        }));
    };
    
    // Check if any data has been selected from the dropdowns
    const hasSelectedData = () => {
        return Object.values(selectedData).some(category => category.length > 0);
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
    
    const { 
        data: averagedData, 
        isLoading, 
        error, 
        fetchData, 
        clearCache 
    } = usePageDataCache('lab42-averaging');


    const handleDateRangeChange = (startDate, endDate) => {
        setDateRange({ start: startDate, end: endDate });
    };

    const calculateAveragedDataFunction = async () => {
        if (!hasSelectedData()) {
            throw new Error('Please select at least one parameter to average');
        }

        // TODO: Implement actual averaging calculation logic here
        // This is a template for you to add your averaging functionality
        
        // Get all selected parameters from all categories
        const allSelectedParams = [
            ...selectedData.qt,
            ...selectedData.pressures,
            ...selectedData.temperatures,
            ...selectedData.flows,
            ...selectedData.nmr
        ];
        
        // Example placeholder data
        const mockAveragedData = allSelectedParams.map((param, index) => ({
            name: param,
            x: Array.from({ length: 100 }, (_, i) => new Date(Date.now() - (100 - i) * 60000)),
            y: Array.from({ length: 100 }, (_, i) => 
                Math.sin(i * 0.1 + index) * (20 + Math.random() * 10) + 50
            ),
            type: 'scatter',
            mode: 'lines+markers',
            line: { 
                color: `hsl(${index * 360 / allSelectedParams.length}, 70%, 50%)`,
                width: 2 
            },
            marker: { size: 4 }
        }));

        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return mockAveragedData;
    };

    const plotConfig = {
        data: averagedData || [],
        layout: {
            title: `Lab 042 Averaged Data (N=${nPoints}, Sampling=${samplingFactor}x)`,
            xaxis: { 
                title: 'Time',
                type: 'date'
            },
            yaxis: { title: 'Value' },
            showlegend: true,
            margin: { t: 50, r: 50, b: 50, l: 50 },
            hovermode: 'closest'
        },
        config: {
            displayModeBar: true,
            responsive: true
        }
    };

    return (
        <div className="averaging-page">
            <div className="averaging-header">
                <h2>Lab 042 Data Averaging</h2>
            </div>

            <div className="averaging-controls">
                <div className="control-section">
                    <h3>Averaging Parameters</h3>
                    <div className="parameter-controls">
                        <div className="parameter-group">
                            <label htmlFor="nPoints">N Points:</label>
                            <input
                                id="nPoints"
                                type="number"
                                min="1"
                                max="1000"
                                defaultValue={nPoints}
                                onBlur={(e) => {
                                    const value = parseInt(e.target.value);
                                    if (!isNaN(value) && value >= 1 && value <= 1000) {
                                        setNPoints(value);
                                    } else {
                                        e.target.value = nPoints; // Reset to current value if invalid
                                    }
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        const value = parseInt(e.target.value);
                                        if (!isNaN(value) && value >= 1 && value <= 1000) {
                                            setNPoints(value);
                                        } else {
                                            e.target.value = nPoints; // Reset to current value if invalid
                                        }
                                        e.target.blur(); // Remove focus
                                    }
                                }}
                            />
                        </div>
                        <div className="parameter-group">
                            <label htmlFor="samplingFactor">Sampling Factor:</label>
                            <input
                                id="samplingFactor"
                                type="number"
                                min="1"
                                max="100"
                                defaultValue={samplingFactor}
                                onBlur={(e) => {
                                    const value = parseInt(e.target.value);
                                    if (!isNaN(value) && value >= 1 && value <= 100) {
                                        setSamplingFactor(value);
                                    } else {
                                        e.target.value = samplingFactor; // Reset to current value if invalid
                                    }
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        const value = parseInt(e.target.value);
                                        if (!isNaN(value) && value >= 1 && value <= 100) {
                                            setSamplingFactor(value);
                                        } else {
                                            e.target.value = samplingFactor; // Reset to current value if invalid
                                        }
                                        e.target.blur(); // Remove focus
                                    }
                                }}
                            />
                        </div>
                    </div>
                </div>

                <div className="control-section">
                    <h3>Time Range</h3>
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


                <div className="control-section">
                    <button 
                        onClick={() => fetchData(calculateAveragedDataFunction)}
                        disabled={isLoading || !hasSelectedData()}
                        className="calculate-button"
                    >
                        {isLoading ? 'Calculating...' : 'Calculate Averaged Data'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <p>{error}</p>
                </div>
            )}

            <div className="averaging-plot-container">
                <FlexiblePlotlyContainer 
                    plotId="lab42-averaging-plot"
                    data={plotConfig.data}
                    layout={plotConfig.layout}
                    config={plotConfig.config}
                />
            </div>

            <div className="averaging-info">
                <h3>Averaging Information</h3>
                <div className="info-grid">
                    <div className="info-item">
                        <label>Lab:</label>
                        <span>Lab 042</span>
                    </div>
                    <div className="info-item">
                        <label>N Points:</label>
                        <span>{nPoints}</span>
                    </div>
                    <div className="info-item">
                        <label>Sampling Factor:</label>
                        <span>{samplingFactor}x</span>
                    </div>
                    <div className="info-item">
                        <label>Selected Parameters:</label>
                        <span>{Object.values(selectedData).reduce((total, category) => total + category.length, 0)}</span>
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
                </div>
            </div>
        </div>
    );
}

export default Lab42Averaging;
