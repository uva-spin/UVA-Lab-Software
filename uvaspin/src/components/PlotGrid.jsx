import React, { useState, useEffect } from 'react';
import IndividualPlot from './IndividualPlot';
import { useResizeDetector } from 'react-resize-detector';
import '../assets/css/plot.css';

function PlotGrid({ numPlots, labType = 'lab42', dateRange, timeTravelInterval }) {
    const [gridDimensions, setGridDimensions] = useState({ width: 0, height: 0 });
    const [responsiveLayout, setResponsiveLayout] = useState('auto');
    
    // Allow user to add more or less plots with a button in the top right corner
    console.log(numPlots);
    const plotIds = Array.from({ length: numPlots }, (_, index) => `plot-${index + 1}`);



    return (
        <div className={`plot-grid-container responsive-${responsiveLayout}`}>
            <div className="plot-grid" style={{
                gridTemplateColumns: responsiveLayout === 'mobile' ? '1fr' : 
                                   responsiveLayout === 'tablet' ? 'repeat(2, 1fr)' : 
                                   'repeat(auto-fit, minmax(400px, 1fr))',
                gap: '20px'
            }}>
                {plotIds.map((plotId, index) => (
                    <IndividualPlot 
                        key={plotId}
                        plotId={plotId}
                        plotNumber={index + 1}
                        labType={labType}
                        dateRange={dateRange}
                        timeTravelInterval={timeTravelInterval}
                        gridDimensions={gridDimensions}
                        responsiveLayout={responsiveLayout}
                    />
                ))}
            </div>
        </div>
    );
}

export default PlotGrid;
