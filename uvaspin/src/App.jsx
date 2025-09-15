import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import Lab42Page from './pages/Lab42Page';
import Lab36Page from './pages/Lab36Page';
import HistoryPage from './pages/HistoryPage';
import { DataSelectionProvider } from './utils/useDataSelection';
import './App.css';

function App() {
    return (
        <Router>
            <DataSelectionProvider>
                <div className="App">
                    <Routes>
                        <Route path="/" element={<Layout />}>
                            <Route index element={<HomePage />} />
                            <Route path="lab42" element={<Lab42Page />} />
                            <Route path="lab36" element={<Lab36Page />} />
                            <Route path="history" element={<HistoryPage />} />
                        </Route>
                    </Routes>
                </div>
            </DataSelectionProvider>
        </Router>
    );
}

export default App;