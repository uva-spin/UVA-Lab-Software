import React, { useState, useEffect } from 'react';
import FlexiblePlotlyContainer from '../../containers/FlexiblePlotlyContainer';
import usePageDataCache from '../../utils/usePageDataCache';
import { LAB_COLORS } from '../../utils/plotUtils';
import '../../assets/css/NMRDisplay.css';

const LAB_LABELS = { lab42: 'Lab 042', lab36: 'Lab 036' };

export default function NMRDisplay({ labType }) {
  const [nmrValues, setNmrValues] = useState({ polarization: '--', error: '--', snr: '--', currentRunNumber: '--' });
  const { data: nmrData, isLoading, error, fetchData } = usePageDataCache(`${labType}-nmr`);

  const fetchNMRData = async () => {
    const mockData = {
      frequency: Array.from({ length: 1000 }, (_, i) => i * 0.1),
      amplitude: Array.from({ length: 1000 }, (_, i) => Math.sin(i * 0.1) * Math.exp(-i * 0.01)),
    };
    await new Promise((r) => setTimeout(r, 1000));
    return mockData;
  };

  useEffect(() => {
    fetchData(fetchNMRData);
    const id = setInterval(() => fetchData(fetchNMRData), 5000);
    return () => clearInterval(id);
  }, [fetchData]);

  const plotConfig = {
    data: nmrData ? [{ x: nmrData.frequency, y: nmrData.amplitude, type: 'scatter', mode: 'lines', name: 'NMR Signal', line: { color: LAB_COLORS[labType], width: 2 } }] : [],
    layout: { title: `${LAB_LABELS[labType]} NMR Signal - Real Time`, xaxis: { title: 'Frequency (MHz)' }, yaxis: { title: 'Amplitude' }, showlegend: true, margin: { t: 50, r: 50, b: 50, l: 50 } },
    config: { displayModeBar: true, responsive: true },
  };

  return (
    <div className="nmr-display">
      <div className="nmr-header">
        <h2>{LAB_LABELS[labType]} NMR Display</h2>
        <div className="nmr-controls">
          <button onClick={() => fetchData(fetchNMRData)} disabled={isLoading} className="refresh-button">
            {isLoading ? 'Loading...' : 'Refresh Data'}
          </button>
          <div className="status-indicator">
            <span className={`status-dot ${isLoading ? 'loading' : 'active'}`} />
            {isLoading ? 'Loading' : 'Live'}
          </div>
        </div>
      </div>

      <div className="nmr-values-section">
        <div className="control-section">
          <h3>NMR Values</h3>
          <div className="nmr-values-grid">
            {['polarization', 'error', 'snr', 'currentRunNumber'].map((k) => (
              <div key={k} className="nmr-value-item">
                <div className="value-label">{k === 'currentRunNumber' ? 'Current Run Number' : k.charAt(0).toUpperCase() + k.slice(1)}</div>
                <div className="value-display">{nmrValues[k]}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => fetchData(fetchNMRData)}>Retry</button>
        </div>
      )}

      <div className="nmr-plot-container">
        <FlexiblePlotlyContainer plotId={`${labType}-nmr-plot`} data={plotConfig.data} layout={plotConfig.layout} config={plotConfig.config} />
      </div>

      <div className="nmr-info">
        <h3>NMR Signal Information</h3>
        <div className="info-grid">
          <div className="info-item"><label>Lab:</label><span>{LAB_LABELS[labType]}</span></div>
          <div className="info-item"><label>Update Frequency:</label><span>5 seconds</span></div>
          <div className="info-item"><label>Data Points:</label><span>{nmrData?.frequency?.length ?? 0}</span></div>
          <div className="info-item"><label>Last Update:</label><span>{new Date().toLocaleTimeString()}</span></div>
        </div>
      </div>
    </div>
  );
}
