import React from 'react';
import { useDataSelection } from '../utils/useDataSelection';
import { Lab42Plot, Lab36Plot, HistoryPlot } from './Plots';

function IndividualPlot({ plotId, plotNumber, labType = 'lab42', dateRange }) {
    const { 
        getPlotParameters, 
        setActivePlot, 
        activePlotId, 
        clearPlot 
    } = useDataSelection();
    
    const selectedParameters = getPlotParameters(plotId);
    const isActive = activePlotId === plotId;

    const handlePlotClick = () => {
        setActivePlot(plotId);
    };

    const handleClearPlot = (e) => {
        e.stopPropagation();
        clearPlot(plotId);
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
        switch (labType) {
            case 'lab42':
                return <Lab42Plot selectedParameters={selectedParameters} />;
            case 'lab36':
                return <Lab36Plot selectedParameters={selectedParameters} />;
            case 'history':
                return <HistoryPlot selectedParameters={selectedParameters} dateRange={dateRange} />;
            default:
                return <Lab42Plot selectedParameters={selectedParameters} />;
        }
    };

    return (
        <div 
            className={`individual-plot ${isActive ? 'active' : ''}`}
            onClick={handlePlotClick}
        >
            <div className="plot-header">
                <div className="plot-title">
                    Plot {plotNumber}
                </div>
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
