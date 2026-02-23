import React, { useState } from 'react';
import PlotGrid from '../../components/PlotGrid';
import '../../assets/css/LabPage.css';

function Lab36Page() {
    const [numPlots, setNumPlots] = useState(1);
    const [timeTravelInterval, setTimeTravelInterval] = useState("01:00:00");

    return (
        <div className="lab-page">
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} labType="lab36" timeTravelInterval={timeTravelInterval} />
            </div>
        </div>
    );
}

export default Lab36Page;

