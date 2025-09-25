import React from 'react';
import Plot from 'react-plotly.js';
import { useDataSelection } from '../utils/useDataSelection';
import { 
    createTracesFromData, 
    extendTracesWithData, 
    getPlotLayout,  
    getPlotConfig,
    shouldComponentUpdate
} from '../utils/plotUtils';
import { generatePlotData as generatePlotDataUtil } from '../utils/dataProcessor';
import { fetchDataFromDB } from '../utils/Query';



// Main plotting component 
class DataPlot extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            layout: getPlotLayout(props.selectedParameters),
            config: getPlotConfig(props.labType),
            frames: [],
            loading: false,
            error: null,
            lastUpdate: null,
            cachedData: new Map(),
            lastTimestamp: null
        };
        this.plotRef = React.createRef();
        this.isInitialized = false;
        this.intervalId = null;
    }

    // Function to update plot data without recreation
    updatePlotData = (newData, availableKeys, selectedKeys, isIncremental = false) => {
        if (!newData || newData.length === 0) return;
        
        if (isIncremental && this.isInitialized && this.plotRef.current && this.state.data.length > 0) {
            // Use extendTraces for incremental updates
            console.log('Using Plotly.extendTraces for incremental update with', newData.length, 'new data points');
            extendTracesWithData(this.plotRef, newData, availableKeys, selectedKeys);
        } else {
            // Create new traces for initial load or parameter changes
            console.log('Creating new traces for', isIncremental ? 'incremental' : 'initial', 'update with', newData.length, 'data points');
            const traces = createTracesFromData(newData, availableKeys, selectedKeys);
            const layout = getPlotLayout(this.props.selectedParameters, newData);
            this.setState({ 
                data: traces,
                layout: layout
            });
            this.isInitialized = true;
        }
    };

    // Generate plot data from selected parameters
    generatePlotData = async (selectedParams, isIncremental = false) => {
        const { labType, dateRange } = this.props;
        const { lastTimestamp, cachedData } = this.state;
        
        await generatePlotDataUtil(
            selectedParams, 
            isIncremental, 
            labType, 
            dateRange, 
            lastTimestamp, 
            cachedData, 
            this.setState.bind(this)
        );
    };

    // Lifecycle methods
    componentDidMount() {
        this.generatePlotData(this.props.selectedParameters, false);
        this.startAutoRefresh();
    }

    componentDidUpdate(prevProps) {
        // Update plot when selected parameters or date range changes
        if (prevProps.selectedParameters !== this.props.selectedParameters) {
            // Clear cache when parameters change to ensure fresh data
            this.setState({
                cachedData: new Map(),
                lastTimestamp: null,
                data: []
            });
            this.isInitialized = false; // Reset initialization flag for parameter changes
            this.generatePlotData(this.props.selectedParameters, false); // Full refresh for parameter changes
        }
        
        // Restart auto-refresh if labType or dateRange changes
        if (prevProps.labType !== this.props.labType || 
            prevProps.dateRange !== this.props.dateRange) {
            this.stopAutoRefresh();
            this.startAutoRefresh();
        }
    }

    componentWillUnmount() {
        this.stopAutoRefresh();
    }

    startAutoRefresh = () => {
        if (this.props.selectedParameters.size === 0) return;
        
        // Don't auto-refresh history plots with custom date ranges
        if (this.props.labType === 'history' && 
            this.props.dateRange && 
            this.props.dateRange.start && 
            this.props.dateRange.end) {
            return;
        }

        this.intervalId = setInterval(() => {
            this.generatePlotData(this.props.selectedParameters, true); // Use incremental updates
        }, 1000);
    }

    stopAutoRefresh = () => {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    render() {
        const { loading, error, lastUpdate } = this.state;
        const { selectedParameters } = this.props;

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
                            onClick={() => this.generatePlotData(selectedParameters)}
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
                            onClick={() => this.generatePlotData(selectedParameters, true)}
                            title="Refresh Data"
                        >
                            <i className="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
                
                <div className="plot-wrapper">
                    <Plot
                        ref={this.plotRef}
                        data={this.state.data}
                        layout={this.state.layout}
                        config={this.state.config}
                        shouldComponentUpdate={(nextProps) => shouldComponentUpdate(nextProps, this.props)}
                        style={{ width: '100%', height: '100%', minHeight: '600px' }}
                        onInitialized={(figure) => this.setState(figure)}
                        onUpdate={(figure) => this.setState(figure)}
                    />
                </div>
            </div>
        );
    }
}


// Lab-specific plot components
function Lab42Plot({ selectedParameters, dateRange }) {
    return <DataPlot selectedParameters={selectedParameters} labType="lab42" dateRange={dateRange} />;
}

function Lab36Plot({ selectedParameters, dateRange }) {
    return <DataPlot selectedParameters={selectedParameters} labType="lab36" dateRange={dateRange} />;
}

function HistoryPlot({ selectedParameters, dateRange }) {
    return <DataPlot selectedParameters={selectedParameters} labType="history" dateRange={dateRange} />;
}

export { Lab42Plot, Lab36Plot, HistoryPlot, DataPlot };

