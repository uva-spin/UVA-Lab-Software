import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-basic-dist';

function FlexiblePlotlyContainer({ plotId, data, layout, config }) {
    const plotRef = useRef(null);

    useEffect(() => {
        if (plotRef.current && data && layout) {
            Plotly.newPlot(plotRef.current, data, layout, config || {});
        }
    }, [data, layout, config]);

    useEffect(() => {
        return () => {
            if (plotRef.current) {
                Plotly.purge(plotRef.current);
            }
        };
    }, []);

    return (
        <div 
            ref={plotRef} 
            id={plotId}
            style={{ width: '100%', height: '100%' }}
        />
    );
}

export default FlexiblePlotlyContainer;
