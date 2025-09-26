import React, { useState } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import Lab42RealTime from './Lab42RealTime';
import Lab42History from './Lab42History';
import Lab42NMR from './Lab42NMR';
import Lab42Averaging from './Lab42Averaging';
import { AddPlotButton, RemovePlotButton } from '../../components/Buttons';
import '/src/pages/css/LabSubpage.css';
import '/src/pages/css/LabSubpageContent.css';

function Lab42Subpage() {
    const location = useLocation();
    const [activeTab, setActiveTab] = useState('realtime');
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

    const tabs = [
        { id: 'realtime', label: 'Real Time Data', path: '/lab42/realtime' },
        { id: 'history', label: 'History', path: '/lab42/history' },
        { id: 'nmr', label: 'NMR Display', path: '/lab42/nmr' },
        { id: 'averaging', label: 'Averaging', path: '/lab42/averaging' }
    ];

    return (
        <div className="lab-subpage">
            <div className="lab-subpage-header">
                <h1>Lab 042</h1>
                <div className="lab-header-controls">
                    <nav className="lab-tabs">
                        {tabs.map(tab => (
                            <Link
                                key={tab.id}
                                to={tab.path}
                                className={`lab-tab ${location.pathname === tab.path ? 'active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                {tab.label}
                            </Link>
                        ))}
                    </nav>
                    <div className="plot-controls">
                        <AddPlotButton onAddPlot={addPlot} />
                        <RemovePlotButton onRemovePlot={removePlot} />
                    </div>
                </div>
            </div>
            <div className="lab-subpage-content">
                <Routes>
                    <Route path="/realtime" element={<Lab42RealTime numPlots={numPlots} />} />
                    <Route path="/history" element={<Lab42History numPlots={numPlots} />} />
                    <Route path="/nmr" element={<Lab42NMR numPlots={numPlots} />} />
                    <Route path="/averaging" element={<Lab42Averaging numPlots={numPlots} />} />
                </Routes>
            </div>
        </div>
    );
}

export default Lab42Subpage;
