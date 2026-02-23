import React, { useState } from 'react';
import FlexiblePlotlyContainer from '../../containers/FlexiblePlotlyContainer';
import DateTimePicker from '../../components/DateTimePicker';
import DataSelectionDropdown from '../../components/DataSelectionDropdown';
import usePageDataCache from '../../utils/usePageDataCache';
import { fetchDataFromDB } from '../../utils/Query';
import { createTracesFromData, getTimeSeriesPlotConfig, getObjVal } from '../../utils/plotUtils';
import { BASE_DATA_STRUCTURE, getQTOptions, processAllParams } from '../../constants/dataStructure';
import '../../assets/css/AveragingPage.css';

const LAB_LABELS = { lab42: 'Lab 042', lab36: 'Lab 036' };

function applyAveraging(rawData, availableKeys, selectedKeys, nPoints, samplingFactor) {
  if (!rawData?.length) return [];
  const sampled = rawData.filter((_, i) => i % samplingFactor === 0);
  if (sampled.length < nPoints) return sampled;

  const result = [];
  for (let i = nPoints - 1; i < sampled.length; i++) {
    const avgPoint = { timestamp: getObjVal(sampled[i], 'timestamp') };
    selectedKeys.forEach((key) => {
      if (availableKeys.includes(key)) {
        let sum = 0, count = 0;
        for (let j = i - nPoints + 1; j <= i; j++) {
          const v = getObjVal(sampled[j], key);
          if (v != null && !isNaN(v)) { sum += v; count++; }
        }
        avgPoint[key] = count ? sum / count : null;
      }
    });
    result.push(avgPoint);
  }
  return result;
}

export default function AveragingPage({ labType }) {
  const [nPoints, setNPoints] = useState(10);
  const [samplingFactor, setSamplingFactor] = useState(1);
  const [dateRange, setDateRange] = useState({ start: null, end: null });
  const [selectedData, setSelectedData] = useState({
    qt: [], pressures: [], temperatures: [], flows: [], nmr: [],
  });

  const { data: averagedData, isLoading, error, fetchData } = usePageDataCache(`${labType}-averaging`);
  const hasSelectedData = () => Object.values(selectedData).some((c) => c.length > 0);

  const calculateAveraged = async () => {
    if (!hasSelectedData()) throw new Error('Please select at least one parameter');
    const allParams = processAllParams(selectedData);
    const endTime = dateRange.end || new Date();
    const startTime = dateRange.start || new Date(endTime.getTime() - 24 * 60 * 60 * 1000);

    const result = await fetchDataFromDB(allParams, startTime, endTime);
    if (!result.data?.length) throw new Error('No data found for the selected time range and parameters');

    const averaged = applyAveraging(result.data, result.availableKeys, allParams, nPoints, samplingFactor);
    return createTracesFromData(averaged, result.availableKeys, allParams);
  };

  const baseConfig = getTimeSeriesPlotConfig(`${LAB_LABELS[labType]} Averaged Data (N=${nPoints}, Sampling=${samplingFactor}x)`, `${labType}_averaging`);
  const plotConfig = {
    data: averagedData || [],
    layout: baseConfig.layout,
    config: baseConfig.config,
  };

  const handleNPointsBlur = (e) => {
    const v = parseInt(e.target.value, 10);
    if (!isNaN(v) && v >= 1 && v <= 1000) setNPoints(v);
    else e.target.value = nPoints;
  };
  const handleSamplingBlur = (e) => {
    const v = parseInt(e.target.value, 10);
    if (!isNaN(v) && v >= 1 && v <= 100) setSamplingFactor(v);
    else e.target.value = samplingFactor;
  };

  return (
    <div className="averaging-page">
      <div className="averaging-header"><h2>{LAB_LABELS[labType]} Data Averaging</h2></div>

      <div className="averaging-controls">
        <div className="control-section">
          <h3>Averaging Parameters</h3>
          <div className="parameter-controls">
            <div className="parameter-group">
              <label htmlFor="nPoints">N Points:</label>
              <input id="nPoints" type="number" min="1" max="1000" defaultValue={nPoints} onBlur={handleNPointsBlur} onKeyDown={(e) => e.key === 'Enter' && e.target.blur()} />
            </div>
            <div className="parameter-group">
              <label htmlFor="samplingFactor">Sampling Factor:</label>
              <input id="samplingFactor" type="number" min="1" max="100" defaultValue={samplingFactor} onBlur={handleSamplingBlur} onKeyDown={(e) => e.key === 'Enter' && e.target.blur()} />
            </div>
          </div>
        </div>

        <div className="control-section">
          <h3>Time Range</h3>
          <DateTimePicker onDateRangeChange={(s, e) => setDateRange({ start: s, end: e })} />
        </div>

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

        <div className="control-section">
          <button onClick={() => fetchData(calculateAveraged)} disabled={isLoading || !hasSelectedData()} className="calculate-button">
            {isLoading ? 'Calculating...' : 'Calculate Averaged Data'}
          </button>
        </div>
      </div>

      {error && <div className="error-message"><p>{error}</p></div>}

      <div className="averaging-plot-container">
        <FlexiblePlotlyContainer plotId={`${labType}-averaging-plot`} data={plotConfig.data} layout={plotConfig.layout} config={plotConfig.config} />
      </div>

      <div className="averaging-info">
        <h3>Averaging Information</h3>
        <div className="info-grid">
          <div className="info-item"><label>Lab:</label><span>{LAB_LABELS[labType]}</span></div>
          <div className="info-item"><label>N Points:</label><span>{nPoints}</span></div>
          <div className="info-item"><label>Sampling Factor:</label><span>{samplingFactor}x</span></div>
          <div className="info-item"><label>Selected Parameters:</label><span>{Object.values(selectedData).reduce((t, c) => t + c.length, 0)}</span></div>
          <div className="info-item"><label>Time Range:</label><span>{dateRange.start && dateRange.end && !Number.isNaN(dateRange.start.getTime()) && !Number.isNaN(dateRange.end.getTime()) ? `${dateRange.start.toLocaleDateString()} - ${dateRange.end.toLocaleDateString()}` : 'Not set'}</span></div>
        </div>
      </div>
    </div>
  );
}
