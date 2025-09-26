import React, { useState, useCallback } from 'react';
import PlotGrid from '../components/PlotGrid';
import 'react-time-picker/dist/TimePicker.css';
import { AddPlotButton, RemovePlotButton } from '../components/Buttons';
import './LabPage.css';

function Lab42Page() {
    const [numPlots, setNumPlots] = useState(1);
    const [timeTravelInterval, setTimeTravelInterval] = useState("00:01:00");

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

    return (
        <div className="lab-page">
            <div className="lab-page-header">
                <div className="lab-page-header-content">
                <AddPlotButton onAddPlot={addPlot} />
                <RemovePlotButton onRemovePlot={removePlot} />
                </div>
            </div>
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} labType="lab42" timeTravelInterval={timeTravelInterval} />
            </div>
        </div>
    );
}

export default Lab42Page;
    
