import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import '../assets/css/plot.css';

function FlexiblePlotlyContainer({ plotId, data, layout, config }) {
    const plotData = Array.isArray(data) ? data : [];
    const mergedLayout = useMemo(() => (layout ? { ...layout, autosize: true } : { autosize: true }), [layout]);
    const mergedConfig = useMemo(() => (config ? { ...config, responsive: true } : { responsive: true }), [config]);
    const revision = plotData.length;

    return (
        <div className="flexible-plotly-wrapper">
            <Plot
                divId={plotId}
                data={plotData}
                layout={mergedLayout}
                config={mergedConfig}
                revision={revision}
                style={{ width: '100%', height: 450, minHeight: 450 }}
                useResizeHandler
            />
        </div>
    );
}

export default FlexiblePlotlyContainer;
