import React, { useState, useEffect } from 'react';
import { Lab42Plot, Lab36Plot, HistoryPlot } from '../components/Plots.jsx';
import { useDataSelection } from '../utils/useDataSelection';
import '../../css/plot.css';

function PlotlyContainer({ labType = 'lab42' }) {
    const { selectedParameters } = useDataSelection();
    const [currentLabType, setCurrentLabType] = useState(labType);

    useEffect(() => {
        setCurrentLabType(labType);
    }, [labType]);

    const renderPlot = () => {
        switch (currentLabType) {
            case 'lab42':
                return <Lab42Plot selectedParameters={selectedParameters} />;
            case 'lab36':
                return <Lab36Plot selectedParameters={selectedParameters} />;
            case 'history':
                return <HistoryPlot selectedParameters={selectedParameters} />;
            default:
                return <Lab42Plot selectedParameters={selectedParameters} />;
        }
    };

    return (
        <div className="plotly-container">
            {renderPlot()}
        </div>
    );
}

export default PlotlyContainer;

