import React, { useState } from 'react';
import PlotGrid from '../components/PlotGrid';
import TimePicker from 'react-time-picker';
import { AddPlotButton, RemovePlotButton } from '../components/Buttons';
import './LabPage.css';

function Lab42Page() {
    const [numPlots, setNumPlots] = useState(1);

    const addPlot = () => {
        if (numPlots < 6) {
            setNumPlots(numPlots + 1);
        }
    };

    const removePlot = () => {
        if (numPlots > 1) {
            setNumPlots(numPlots - 1);
        }
    };

    const handleTimeChange = (time) => {
        console.log(time);
    };

    return (
        <div className="lab-page">
            <div className="lab-page-header">
                <AddPlotButton onAddPlot={addPlot} />
                <RemovePlotButton onRemovePlot={removePlot} />
            </div>
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} />
            </div>
        </div>
    );
}

export default Lab42Page;
    
