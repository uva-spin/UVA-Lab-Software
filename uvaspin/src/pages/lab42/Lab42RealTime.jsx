import React, { useState } from 'react';
import PlotGrid from '../../components/PlotGrid';
import '/src/pages/css/LabPage.css';

function Lab42RealTime({ numPlots = 1 }) {
    
    return (
        <div className="lab-page">
            <div className="lab-page-content">
                <PlotGrid numPlots={numPlots} labType="lab42" />
            </div>
        </div>
    );
}

export default Lab42RealTime;
