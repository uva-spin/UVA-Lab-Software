import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js-basic-dist';
import FlexiblePlotlyContainer from '../../containers/FlexiblePlotlyContainer';
import usePageDataCache from '../../utils/usePageDataCache';
import '/src/pages/css/NMRDisplay.css';

function Lab36NMR() {
    const { 
        data: nmrData, 
        isLoading, 
        error, 
        fetchData, 
        clearCache, 
        setDataManually 
    } = usePageDataCache('lab36-nmr');
    
    // Placeholder NMR values - these will be populated from database in the future
    const [nmrValues, setNmrValues] = useState({
        polarization: '--',
        error: '--',
        snr: '--',
        currentRunNumber: '--'
    });

    // Template function for fetching NMR data
    const fetchNMRDataFunction = async () => {
        // TODO: Implement actual NMR data fetching logic here
        // This is a template for you to add your NMR-specific functionality
        
        // Example placeholder data structure
        const mockData = {
            frequency: Array.from({ length: 1000 }, (_, i) => i * 0.1),
            amplitude: Array.from({ length: 1000 }, (_, i) => Math.sin(i * 0.1) * Math.exp(-i * 0.01))
        };
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return mockData;
    };

    // Auto-refresh NMR data every 5 seconds
    useEffect(() => {
        fetchData(fetchNMRDataFunction);
        const interval = setInterval(() => fetchData(fetchNMRDataFunction), 5000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const plotConfig = {
        data: nmrData ? [{
            x: nmrData.frequency,
            y: nmrData.amplitude,
            type: 'scatter',
            mode: 'lines',
            name: 'NMR Signal',
            line: { color: '#764ba2', width: 2 }
        }] : [],
        layout: {
            title: 'Lab 036 NMR Signal - Real Time',
            xaxis: { title: 'Frequency (MHz)' },
            yaxis: { title: 'Amplitude' },
            showlegend: true,
            margin: { t: 50, r: 50, b: 50, l: 50 }
        },
        config: {
            displayModeBar: true,
            responsive: true
        }
    };

    return (
        <div className="nmr-display">
            <div className="nmr-header">
                <h2>Lab 036 NMR Display</h2>
                <div className="nmr-controls">
                    <button 
                        onClick={() => fetchData(fetchNMRDataFunction)} 
                        disabled={isLoading}
                        className="refresh-button"
                    >
                        {isLoading ? 'Loading...' : 'Refresh Data'}
                    </button>
                    <div className="status-indicator">
                        <span className={`status-dot ${isLoading ? 'loading' : 'active'}`}></span>
                        {isLoading ? 'Loading' : 'Live'}
                    </div>
                </div>
            </div>
            
            <div className="nmr-values-section">
                <div className="control-section">
                    <h3>NMR Values</h3>
                    <div className="nmr-values-grid">
                        <div className="nmr-value-item">
                            <div className="value-label">Polarization</div>
                            <div className="value-display">{nmrValues.polarization}</div>
                        </div>
                        <div className="nmr-value-item">
                            <div className="value-label">Error</div>
                            <div className="value-display">{nmrValues.error}</div>
                        </div>
                        <div className="nmr-value-item">
                            <div className="value-label">SNR</div>
                            <div className="value-display">{nmrValues.snr}</div>
                        </div>
                        <div className="nmr-value-item">
                            <div className="value-label">Current Run Number</div>
                            <div className="value-display">{nmrValues.currentRunNumber}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            {error && (
                <div className="error-message">
                    <p>{error}</p>
                    <button onClick={() => fetchData(fetchNMRDataFunction)}>Retry</button>
                </div>
            )}
            
            <div className="nmr-plot-container">
                <FlexiblePlotlyContainer 
                    plotId="lab36-nmr-plot"
                    data={plotConfig.data}
                    layout={plotConfig.layout}
                    config={plotConfig.config}
                />
            </div>
            
            <div className="nmr-info">
                <h3>NMR Signal Information</h3>
                <div className="info-grid">
                    <div className="info-item">
                        <label>Lab:</label>
                        <span>Lab 036</span>
                    </div>
                    <div className="info-item">
                        <label>Update Frequency:</label>
                        <span>5 seconds</span>
                    </div>
                    <div className="info-item">
                        <label>Data Points:</label>
                        <span>{nmrData ? nmrData.frequency.length : 0}</span>
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

export default Lab36NMR;
