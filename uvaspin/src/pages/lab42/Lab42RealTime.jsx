import React, { useState } from 'react';
import PlotGrid from '../../components/PlotGrid';
import '/src/pages/css/LabPage.css';

function Lab42RealTime({ numPlots = 1 }) {
    const [timeTravelInterval, setTimeTravelInterval] = useState("00:01:00");

    return (
        <div className="lab-page">
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} labType="lab42" timeTravelInterval={timeTravelInterval} />
            </div>
        </div>
    );
}

export default Lab42RealTime;
