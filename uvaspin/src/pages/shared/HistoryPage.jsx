import React, { useState } from 'react';
import FlexiblePlotlyContainer from '../../containers/FlexiblePlotlyContainer';
import DateTimePicker from '../../components/DateTimePicker';
import DataSelectionDropdown from '../../components/DataSelectionDropdown';
import usePageDataCache from '../../utils/usePageDataCache';
import { fetchDataFromDB } from '../../utils/Query';
import { createTracesFromData, getTimeSeriesPlotConfig } from '../../utils/plotUtils';
import { BASE_DATA_STRUCTURE, getQTOptions, processAllParams } from '../../constants/dataStructure';
import '../../assets/css/HistoryPage.css';

const LAB_LABELS = { lab42: 'Lab 042', lab36: 'Lab 036' };

export default function HistoryPage({ labType }) {
  const [dateRange, setDateRange] = useState({ start: null, end: null });
  const [selectedData, setSelectedData] = useState({
    qt: [], pressures: [], temperatures: [], flows: [], nmr: [],
  });

  const { data: historyData, isLoading, error, fetchData } = usePageDataCache(`${labType}-history`);
  const hasSelectedData = () => Object.values(selectedData).some((cat) => cat.length > 0);

  const fetchHistoryData = async () => {
    if (!dateRange.start || !dateRange.end) throw new Error('Please select a date range');
    if (!hasSelectedData()) throw new Error('Please select at least one parameter');

    const allParams = processAllParams(selectedData);

    const result = await fetchDataFromDB(allParams, dateRange.start, dateRange.end);
    if (!result.data?.length) throw new Error('No data found for the selected time range and parameters');

    return createTracesFromData(result.data, result.availableKeys, allParams);
  };

  const baseConfig = getTimeSeriesPlotConfig(`${LAB_LABELS[labType]} Historical Data`, `${labType}_history`);
  const plotConfig = {
    data: historyData || [],
    layout: baseConfig.layout,
    config: baseConfig.config,
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <h2>{LAB_LABELS[labType]} Historical Data</h2>
        <div className="history-controls">
          <DateTimePicker onDateRangeChange={(s, e) => setDateRange({ start: s, end: e })} />
          <button
            onClick={() => fetchData(fetchHistoryData)}
            disabled={isLoading || !dateRange.start || !dateRange.end || !hasSelectedData()}
            className="refresh-button"
          >
            {isLoading ? 'Loading...' : 'Load Historical Data'}
          </button>
          <div className="status-indicator">
            <span className={`status-dot ${isLoading ? 'loading' : 'active'}`} />
            {isLoading ? 'Loading' : 'Ready'}
          </div>
        </div>
      </div>

      <div className="control-grid">
        <div className="control-section">
          <h3>Data Selection</h3>
          <div className="data-selection-grid">
            <DataSelectionDropdown label="QT Parameters" options={getQTOptions()} selectedValues={selectedData.qt} onSelectionChange={(v) => setSelectedData((p) => ({ ...p, qt: v }))} placeholder="Select QT parameters..." />
            <DataSelectionDropdown label="Pressures" options={BASE_DATA_STRUCTURE.Pressures} selectedValues={selectedData.pressures} onSelectionChange={(v) => setSelectedData((p) => ({ ...p, pressures: v }))} placeholder="Select pressure sensors..." />
            <DataSelectionDropdown label="Temperatures" options={BASE_DATA_STRUCTURE.Temperatures} selectedValues={selectedData.temperatures} onSelectionChange={(v) => setSelectedData((p) => ({ ...p, temperatures: v }))} placeholder="Select temperature sensors..." />
            <DataSelectionDropdown label="Flows" options={BASE_DATA_STRUCTURE.Flows} selectedValues={selectedData.flows} onSelectionChange={(v) => setSelectedData((p) => ({ ...p, flows: v }))} placeholder="Select flow sensors..." />
            <DataSelectionDropdown label="NMR Parameters" options={BASE_DATA_STRUCTURE.NMR} selectedValues={selectedData.nmr} onSelectionChange={(v) => setSelectedData((p) => ({ ...p, nmr: v }))} placeholder="Select NMR parameters..." />
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => fetchData(fetchHistoryData)}>Retry</button>
        </div>
      )}

      <div className="history-plot-container">
        <FlexiblePlotlyContainer plotId={`${labType}-history-plot`} data={plotConfig.data} layout={plotConfig.layout} config={plotConfig.config} />
      </div>

      <div className="history-info">
        <h3>Historical Data Information</h3>
        <div className="info-grid">
          <div className="info-item"><label>Lab:</label><span>{LAB_LABELS[labType]}</span></div>
          <div className="info-item"><label>Data Points:</label><span>{historyData?.length ?? 0}</span></div>
          <div className="info-item"><label>Time Range:</label><span>{dateRange.start && dateRange.end && !Number.isNaN(dateRange.start.getTime()) && !Number.isNaN(dateRange.end.getTime()) ? `${dateRange.start.toLocaleDateString()} - ${dateRange.end.toLocaleDateString()}` : 'Not set'}</span></div>
          <div className="info-item"><label>Selected Parameters:</label><span>{Object.values(selectedData).reduce((t, c) => t + c.length, 0)}</span></div>
        </div>
      </div>
    </div>
  );
}
