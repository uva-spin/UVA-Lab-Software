import React from 'react';
import Plot from 'react-plotly.js';

function lab42Plot(data) {
    return (
        <Plot data={{
            data,
            mode: 'markers',
            type: 'scatter'
        }} 
        layout={{
            title: element,
            xaxis: {title:"Time (EST)"},
            yaxis: {title:"Value"},
            legend: {
                position: 'ne',
                backgroundOpacity: 0,
                labelBoxBorderColor: 'transparent',
                show: true,
            }
        }} />
    );
}

function lab36Plot(data) {
    return (
        <Plot data={{
            data,
            mode: 'markers',
            type: 'scatter'
        }} 
        layout={{
            title: element,
            xaxis: {title:"Time (EST)"},
            yaxis: {title:"Value"},
            legend: {
                position: 'ne',
                backgroundOpacity: 0,
                labelBoxBorderColor: 'transparent',
                show: true,
            }
        }} />
    );
}

export { lab42Plot, lab36Plot };
