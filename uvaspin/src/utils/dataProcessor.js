// Data processing utilities for plot data management
import { fetchDataFromDB } from './Query';
import { 
    createTracesFromData, 
    extendTracesWithData, 
    mergeDataWithCache,
    getPlotLayout
} from './plotUtils';

// Function to update plot data without recreation
export const updatePlotData = (newData, availableKeys, selectedKeys, isIncremental, plotRef, isInitialized, setState) => {
    if (!newData || newData.length === 0) return;
    
    if (isIncremental && isInitialized && plotRef.current) {
        // Use extendTraces for incremental updates
        console.log('Using Plotly.extendTraces for incremental update with', newData.length, 'new data points');
        extendTracesWithData(plotRef, newData, availableKeys, selectedKeys);
    } else {
        // Create new traces for initial load or parameter changes
        console.log('Creating new traces for', isIncremental ? 'incremental' : 'initial', 'update with', newData.length, 'data points');
        const traces = createTracesFromData(newData, availableKeys, selectedKeys);
        setState({ data: traces });
    }
};

// Generate plot data from selected parameters
export const generatePlotData = async (selectedParams, isIncremental, labType, dateRange, lastTimestamp, cachedData, setState) => {
    if (selectedParams.size === 0) {
        setState({
            data: [],
            error: null,
            cachedData: new Map(),
            lastTimestamp: null
        });
        return;
    }

    // Only show loading for initial load, not incremental updates
    if (!isIncremental) {
        setState({ loading: true });
    }
    setState({ error: null });

    try {
        const selectedKeys = Array.from(selectedParams);
        
        // Use dateRange when provided (any lab), default behavior otherwise
        let startTime = null;
        let endTime = null;
        
        if (dateRange && (dateRange.start || dateRange.end)) {
            startTime = dateRange.start || null;
            endTime = dateRange.end || new Date();
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
                setState({
                    data: [],
                    error: 'No data available for selected parameters'
                });
            }
            return;
        }

        let finalData = data;
        let finalLastTimestamp = data[data.length - 1][0];
        
        if (isIncremental) {
            // Merge with cached data for incremental updates
            const merged = mergeDataWithCache(data, selectedKeys, availableKeys, cachedData);
            finalData = merged.data;
            finalLastTimestamp = merged.lastTimestamp;
            setState({ 
                cachedData: merged.cachedData,
                lastTimestamp: merged.lastTimestamp
            });
        } else {
            // For initial load, cache the data
            const merged = mergeDataWithCache(data, selectedKeys, availableKeys, cachedData);
            finalData = merged.data;
            finalLastTimestamp = merged.lastTimestamp;
            setState({ 
                cachedData: merged.cachedData,
                lastTimestamp: merged.lastTimestamp
            });
        }

        // Update plot data using the new method
        const traces = createTracesFromData(finalData, availableKeys, selectedKeys);
        const layout = getPlotLayout(new Set(selectedKeys), finalData);
        setState({ 
            data: traces,
            layout: layout,
            lastUpdate: new Date()
        });
        
    } catch (err) {
        console.error('Error generating plot data:', err);
        if (!isIncremental) {
            setState({ error: err.message });
        }
    } finally {
        if (!isIncremental) {
            setState({ loading: false });
        }
    }
};
