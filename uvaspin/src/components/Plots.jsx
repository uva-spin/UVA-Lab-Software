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
import TimeTravel from './TimeTravel';
import {useResizeDetector} from 'react-resize-detector';



// Main plotting component 
class DataPlot extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            layout: getPlotLayout(props.selectedParameters, null, props.dimensions),
            config: {...getPlotConfig(props.labType), 
                scrollZoom: true,
                responsive: true
            },
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
        this.timeTravelInterval = null;
        this.lastDimensions = { width: 0, height: 0 };
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
            const layout = getPlotLayout(this.props.selectedParameters, newData, this.props.dimensions);
            this.setState({ 
                data: traces,
                layout: layout
            });
            this.isInitialized = true;
        }
    };

    // Generate plot data from selected parameters
    generatePlotData = async (selectedParams, isIncremental = false) => {
        const { labType, dateRange, timeTravelInterval } = this.props;
        const { lastTimestamp, cachedData } = this.state;
        
        await generatePlotDataUtil(
            selectedParams, 
            isIncremental, 
            labType, 
            dateRange, 
            lastTimestamp, 
            cachedData, 
            timeTravelInterval,
            this.setState.bind(this)
        );
    };

    // Handle plot resize
    handleResize = () => {
        if (this.plotRef.current && this.isInitialized) {
            const { dimensions } = this.props;
            if (dimensions && dimensions.width > 0 && dimensions.height > 0) {
                // Check if dimensions actually changed
                if (this.lastDimensions.width !== dimensions.width || 
                    this.lastDimensions.height !== dimensions.height) {
                    
                    console.log(`Resizing plot to ${dimensions.width}x${dimensions.height}`);
                    
                    // Calculate available space for the plot (accounting for header and margins)
                    const plotWidth = Math.max(300, dimensions.width - 20); // Account for container padding
                    const plotHeight = Math.max(400, dimensions.height - 120); // Account for header (~60px) and margins
                    
                    // Update layout with new dimensions
                    const updatedLayout = {
                        ...this.state.layout,
                        width: plotWidth,
                        height: plotHeight,
                        margin: { 
                            r: 150, 
                            t: 50, 
                            b: 50, 
                            l: 60 
                        }
                    };
                    
                    this.setState({ layout: updatedLayout });
                    
                    // Use Plotly.relayout for smoother resizing
                    Plotly.relayout(this.plotRef.current, {
                        width: plotWidth,
                        height: plotHeight
                    });
                    
                    this.lastDimensions = { ...dimensions };
                }
            }
        }
    };

    // Lifecycle methods
    componentDidMount() {
        this.generatePlotData(this.props.selectedParameters, false);
        this.startAutoRefresh();
        
        // Handle initial resize if dimensions are available
        if (this.props.dimensions && this.props.dimensions.width > 0 && this.props.dimensions.height > 0) {
            // Use setTimeout to ensure the plot is fully initialized
            setTimeout(() => {
                this.handleResize();
            }, 100);
        }
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
        
        // Handle dimension changes
        if (prevProps.dimensions !== this.props.dimensions) {
            this.handleResize();
        }
        
        // Restart auto-refresh if labType, dateRange, or timeTravelInterval changes
        if (prevProps.labType !== this.props.labType || 
            prevProps.dateRange !== this.props.dateRange ||
            prevProps.timeTravelInterval !== this.props.timeTravelInterval) {
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


        // don't auto-refresh if timeTravelInterval is set
        if (this.props.timeTravelInterval) {
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
                <div className="plot-wrapper">
                    <Plot
                        ref={this.plotRef}
                        data={this.state.data}
                        layout={this.state.layout}
                        config={this.state.config}
                        shouldComponentUpdate={(nextProps) => shouldComponentUpdate(nextProps, this.props)}
                        style={{ width: '100%', height: '100%', minHeight: '400px' }}
                        onInitialized={(figure) => this.setState(figure)}
                        onUpdate={(figure) => this.setState(figure)}
                        showlegend={true}
                        useResizeHandler={true}
                    />
                </div>
            </div>
        );
    }
}


// Lab-specific plot components
function Lab42Plot({ selectedParameters, dateRange, timeTravelInterval, dimensions, plotId }) {
    return <DataPlot 
        selectedParameters={selectedParameters} 
        labType="lab42" 
        dateRange={dateRange} 
        timeTravelInterval={timeTravelInterval}
        dimensions={dimensions}
        plotId={plotId}
    />;
}

function Lab36Plot({ selectedParameters, dateRange, timeTravelInterval, dimensions, plotId }) {
    return <DataPlot 
        selectedParameters={selectedParameters} 
        labType="lab36" 
        dateRange={dateRange} 
        timeTravelInterval={timeTravelInterval}
        dimensions={dimensions}
        plotId={plotId}
    />;
}

function HistoryPlot({ selectedParameters, dateRange, timeTravelInterval, dimensions, plotId }) {
    return <DataPlot 
        selectedParameters={selectedParameters} 
        labType="history" 
        dateRange={dateRange} 
        timeTravelInterval={timeTravelInterval}
        dimensions={dimensions}
        plotId={plotId}
    />;
}

export { Lab42Plot, Lab36Plot, HistoryPlot, DataPlot };

