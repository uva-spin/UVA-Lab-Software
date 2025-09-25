import React, { useState, useCallback } from 'react';
import PlotGrid from '../components/PlotGrid';
import DateTimePicker from '../components/DateTimePicker';
import { AddPlotButton, RemovePlotButton } from '../components/Buttons';
import './LabPage.css';

function Lab36Page() {
    const [numPlots, setNumPlots] = useState(1);
    const [dateRange, setDateRange] = useState({ start: null, end: null });

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

    const handleDateRangeChange = useCallback((startDate, endDate) => {
        setDateRange({ start: startDate, end: endDate });
    }, []);

    return (
        <div className="lab-page">
            <div className="lab-page-header">
                <AddPlotButton onAddPlot={addPlot} />
                <RemovePlotButton onRemovePlot={removePlot} />
                <DateTimePicker onDateRangeChange={handleDateRangeChange} />
            </div>
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} labType="lab36" dateRange={dateRange} />
            </div>
        </div>
    );
}

export default Lab36Page;

