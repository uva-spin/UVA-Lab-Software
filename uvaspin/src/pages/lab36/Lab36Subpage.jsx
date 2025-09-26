import React, { useState } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import Lab36RealTime from './Lab36RealTime';
import Lab36History from './Lab36History';
import Lab36NMR from './Lab36NMR';
import Lab36Averaging from './Lab36Averaging';
import { AddPlotButton, RemovePlotButton } from '../../components/Buttons';
import '/src/pages/css/LabSubpage.css';
import '/src/pages/css/LabSubpageContent.css';

function Lab36Subpage() {
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
        { id: 'realtime', label: 'Real Time Data', path: '/lab36/realtime' },
        { id: 'history', label: 'History', path: '/lab36/history' },
        { id: 'nmr', label: 'NMR Display', path: '/lab36/nmr' },
        { id: 'averaging', label: 'Averaging', path: '/lab36/averaging' }
    ];

    return (
        <div className="lab-subpage">
            <div className="lab-subpage-header">
                <h1>Lab 036</h1>
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
                    <Route path="/realtime" element={<Lab36RealTime numPlots={numPlots} />} />
                    <Route path="/history" element={<Lab36History numPlots={numPlots} />} />
                    <Route path="/nmr" element={<Lab36NMR numPlots={numPlots} />} />
                    <Route path="/averaging" element={<Lab36Averaging numPlots={numPlots} />} />
                </Routes>
            </div>
        </div>
    );
}

export default Lab36Subpage;
