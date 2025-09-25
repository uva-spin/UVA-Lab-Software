import React from 'react';
import IndividualPlot from './IndividualPlot';
import '../../css/plot.css';

function PlotGrid({ numPlots }) {
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
                    />
                ))}
            </div>
        // </div>
    );
}

export default PlotGrid;
