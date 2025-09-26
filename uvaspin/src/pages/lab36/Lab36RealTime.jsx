import React, { useState } from 'react';
import PlotGrid from '../../components/PlotGrid';
import DateTimePicker from '../../components/DateTimePicker';
import '/src/pages/css/LabPage.css';

function Lab36RealTime({ numPlots = 1 }) {
    // const [timeTravelInterval, setTimeTravelInterval] = useState("01:00:00");

    return (
        <div className="lab-page">
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} labType="lab36" />
            </div>
        </div>
    );
}

export default Lab36RealTime;
