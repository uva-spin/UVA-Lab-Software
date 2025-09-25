import React from 'react';
import IndividualPlot from './IndividualPlot';
import '../../css/plot.css';

function PlotGrid({ numPlots, labType = 'lab42', dateRange }) {
    // Allow user to add more or less plots with a button in the top right corner
    console.log(numPlots);
    const plotIds = Array.from({ length: numPlots }, (_, index) => `plot-${index + 1}`);

    return (
        // <div className="plot-grid-container">
            <div className="plot-grid">
                {plotIds.map((plotId, index) => (
                    <IndividualPlot 
                        key={plotId}
                        plotId={plotId}
                        plotNumber={index + 1}
                        labType={labType}
                        dateRange={dateRange}
                    />
                ))}
            </div>
        // </div>
    );
}

export default PlotGrid;
