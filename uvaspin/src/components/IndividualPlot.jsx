import React, { useState, useRef, useEffect } from 'react';
import { useDataSelection } from '../utils/useDataSelection';
import { Lab42Plot, Lab36Plot, HistoryPlot } from './Plots';
import TimeTravel from './TimeTravel';
import { useResizeDetector } from 'react-resize-detector';

function IndividualPlot({ plotId, plotNumber, labType, dateRange, timeTravelInterval}) {
    const { 
        getPlotParameters, 
        setActivePlot, 
        setActiveLabType,
        activePlotId, 
        clearPlot 
    } = useDataSelection();
    const [lastUpdate, setLastUpdate] = useState(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [localTimeTravelInterval, setLocalTimeTravelInterval] = useState(timeTravelInterval || '00:01:00');
    const selectedParameters = getPlotParameters(plotId, labType);
    const isActive = activePlotId === plotId;
    const plotRef = useRef(null);

    // Resize detection hook
    const { width, height } = useResizeDetector({
        targetRef: plotRef,
        onResize: (width, height) => {
            if (width && height) {
                setDimensions({ width, height });
                console.log(`Plot ${plotNumber} resized to: ${width}x${height}`);
            }
        },
        refreshMode: 'debounce',
        refreshRate: 100
    });

    const handlePlotClick = () => {
        setActivePlot(plotId);
        setActiveLabType(labType);
    };

    const handleClearPlot = (e) => {
        e.stopPropagation();
        clearPlot(plotId, labType);
    };

    const handleTimeTravelChange = (newTime) => {
        setLocalTimeTravelInterval(newTime);
    };

    const renderPlot = () => {
        if (selectedParameters.size === 0) {
            return (
                <div className="empty-plot">
                    <div className="empty-plot-content">
                        <i className="fas fa-chart-line"></i>
                        <p>Click to select data</p>
                    </div>
                </div>
            );
        }
        
        const plotProps = {
            selectedParameters,
            dateRange,
            timeTravelInterval: localTimeTravelInterval,
            dimensions,
            plotId
        };
        
        switch (labType) {
            case 'lab42':
                return <Lab42Plot {...plotProps} />;
            case 'lab36':
                return <Lab36Plot {...plotProps} />;
            case 'history':
                return <HistoryPlot {...plotProps} />;
            default:
                return <Lab42Plot {...plotProps} />;
        }
    };

    return (
        <div 
            ref={plotRef}
            className={`individual-plot ${isActive ? 'active' : ''}`}
            onClick={handlePlotClick}
        >
            <div className="plot-header">
                <div className="plot-title">
                    Plot {plotNumber}
                    {lastUpdate && (
                        <span className="last-update">
                            Last updated: {lastUpdate.toLocaleTimeString()}
                        </span>
                    )}
                    {dimensions.width > 0 && (
                        <span className="plot-dimensions">
                            {dimensions.width}×{dimensions.height}
                        </span>
                    )}
                </div>
                {selectedParameters.size > 0 && (
                    <div className="time-travel-container">
                        <span className="time-travel-label">Time Travel Interval:</span>
                        <TimeTravel 
                            value={localTimeTravelInterval}
                            onChange={handleTimeTravelChange}
                            maxHours={72}
                        />
                    </div>
                )}
                <div className="plot-controls">
                    {selectedParameters.size > 0 && (
                        <button 
                            className="clear-plot-button"
                            onClick={handleClearPlot}
                            title="Clear this plot"
                        >
                            <i className="fas fa-times"></i>
                        </button>
                    )}
                </div>
            </div>
            <div className="plot-content">
                {renderPlot()}
            </div>
        </div>
    );
}

export default IndividualPlot;
