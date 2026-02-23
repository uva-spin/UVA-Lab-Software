import React, { useState } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { AddPlotButton, RemovePlotButton } from '../../components/ui/Buttons';
import LabRealTime from './LabRealTime';
import HistoryPage from './HistoryPage';
import NMRDisplay from './NMRDisplay';
import AveragingPage from './AveragingPage';
import '../../assets/css/LabSubpage.css';
import '../../assets/css/LabSubpageContent.css';

const LAB_LABELS = { lab42: 'Lab 042', lab36: 'Lab 036' };

export default function LabSubpage({ labType }) {
  const location = useLocation();
  const [numPlots, setNumPlots] = useState(1);

  const tabs = [
    { id: 'realtime', label: 'Real Time Data', path: `/${labType}/realtime` },
    { id: 'history', label: 'History', path: `/${labType}/history` },
    { id: 'nmr', label: 'NMR Display', path: `/${labType}/nmr` },
    { id: 'averaging', label: 'Averaging', path: `/${labType}/averaging` },
  ];

  return (
    <div className="lab-subpage">
      <div className="lab-subpage-header">
        <h1>{LAB_LABELS[labType]}</h1>
        <div className="lab-header-controls">
          <nav className="lab-tabs">
            {tabs.map((tab) => (
              <Link
                key={tab.id}
                to={tab.path}
                className={`lab-tab ${location.pathname === tab.path ? 'active' : ''}`}
              >
                {tab.label}
              </Link>
            ))}
          </nav>
          <div className="plot-controls">
            <AddPlotButton onAddPlot={() => numPlots < 6 && setNumPlots((n) => n + 1)} />
            <RemovePlotButton onRemovePlot={() => numPlots > 1 && setNumPlots((n) => n - 1)} />
          </div>
        </div>
      </div>
      <div className="lab-subpage-content">
        <Routes>
          <Route path="/realtime" element={<LabRealTime numPlots={numPlots} labType={labType} />} />
          <Route path="/history" element={<HistoryPage labType={labType} />} />
          <Route path="/nmr" element={<NMRDisplay labType={labType} />} />
          <Route path="/averaging" element={<AveragingPage labType={labType} />} />
        </Routes>
      </div>
    </div>
  );
}
