import React, { useState, useEffect } from 'react';
import IndividualPlot from './IndividualPlot';
import { useResizeDetector } from 'react-resize-detector';
import './plot.css';

function PlotGrid({ numPlots, labType = 'lab42', dateRange, timeTravelInterval }) {
    const [gridDimensions, setGridDimensions] = useState({ width: 0, height: 0 });
    const [responsiveLayout, setResponsiveLayout] = useState('auto');
    
    // Allow user to add more or less plots with a button in the top right corner
    console.log(numPlots);
    const plotIds = Array.from({ length: numPlots }, (_, index) => `plot-${index + 1}`);

    // Resize detection for the entire grid
    const { width, height } = useResizeDetector({
        onResize: (width, height) => {
            if (width && height) {
                setGridDimensions({ width, height });
                console.log(`PlotGrid resized to: ${width}x${height}`);
                
                // Determine responsive layout based on grid size
                if (width < 768) {
                    setResponsiveLayout('mobile'); // Single column on mobile
                } else if (width < 1200) {
                    setResponsiveLayout('tablet'); // Two columns on tablet
                } else {
                    setResponsiveLayout('desktop'); // Multiple columns on desktop
                }
            }
        },
        refreshMode: 'debounce',
        refreshRate: 150
    });

    // Calculate optimal plot dimensions based on grid size and number of plots
    const calculatePlotDimensions = () => {
        if (gridDimensions.width === 0 || gridDimensions.height === 0) {
            return { width: 'auto', height: 'auto' };
        }

        let cols, rows;
        switch (responsiveLayout) {
            case 'mobile':
                cols = 1;
                rows = numPlots;
                break;
            case 'tablet':
                cols = Math.min(2, numPlots);
                rows = Math.ceil(numPlots / cols);
                break;
            case 'desktop':
            default:
                cols = Math.min(3, numPlots);
                rows = Math.ceil(numPlots / cols);
                break;
        }

        const plotWidth = Math.floor(gridDimensions.width / cols) - 20; // Account for gaps
        const plotHeight = Math.floor(gridDimensions.height / rows) - 20;

        return {
            width: Math.max(300, plotWidth),
            height: Math.max(400, plotHeight)
        };
    };

    const plotDimensions = calculatePlotDimensions();

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
