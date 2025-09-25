import React, { useState, useCallback } from 'react';
import PlotGrid from '../components/PlotGrid';
import TimePicker from 'react-time-picker';
import { AddPlotButton, RemovePlotButton } from '../components/Buttons';
import './LabPage.css';

function Lab42Page() {
    const [numPlots, setNumPlots] = useState(1);
    const [updateTime, setUpdateTime] = useState(new Date());

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
                <TimePicker
                ampm = {true}
                closeOnSelect={true}
                defaultValue={new Date()}
                onChange={(e) => setUpdateTime(e)}
                actionbarDisplayMode="compact"
                clockIcon="refresh"
                clockIconColor="white"
                clockIconSize="24"
                clockIconPosition="left"
                clockIconStyle={{ marginRight: '10px' }}
                clockIconClassName="refresh-icon"
                />
                </div>
            </div>
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} labType="lab42" updateTime={updateTime} />
            </div>
        </div>
    );
}

export default Lab42Page;
    
