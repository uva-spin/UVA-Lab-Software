import React from 'react';
import PlotGrid from '../../components/PlotGrid';
import '../../assets/css/LabPage.css';

export default function LabRealTime({ numPlots = 1, labType }) {
  return (
    <div className="lab-page">
      <div className="lab-page-content">
        <PlotGrid numPlots={numPlots} labType={labType} />
      </div>
    </div>
  );
}
