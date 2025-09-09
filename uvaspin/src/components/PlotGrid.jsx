import React from 'react';
import IndividualPlot from './IndividualPlot';
import '../../css/plot.css';

function PlotGrid() {
    // Allow user to add more or less plots with a button in
    const plotIds = ['plot-1', 'plot-2', 'plot-3', 'plot-4', 'plot-5', 'plot-6'];

    return (
        <div className="plot-grid-container">
            <div className="plot-grid">
                {plotIds.map((plotId, index) => (
                    <IndividualPlot 
                        key={plotId}
                        plotId={plotId}
                        plotNumber={index + 1}
                    />
                ))}
            </div>
        </div>
    );
}

export default PlotGrid;
