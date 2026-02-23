import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/home/HomePage';
import Lab42Page from './pages/lab42/Lab42Page';
import Lab36Page from './pages/lab36/Lab36Page';
import LabSubpage from './pages/shared/LabSubpage';
import { DataSelectionProvider } from './utils/useDataSelection';
import './assets/css/App.css';

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
              <Route path="lab42/*" element={<LabSubpage labType="lab42" />} />
              <Route path="lab36/*" element={<LabSubpage labType="lab36" />} />
            </Route>
          </Routes>
        </div>
      </DataSelectionProvider>
    </Router>
  );
}

export default App;