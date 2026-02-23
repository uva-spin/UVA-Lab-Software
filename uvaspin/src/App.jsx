import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import { DataSelectionProvider } from './utils/useDataSelection';
import './assets/css/App.css';

const HomePage = lazy(() => import('./pages/home/HomePage'));
const Lab42Page = lazy(() => import('./pages/lab42/Lab42Page'));
const Lab36Page = lazy(() => import('./pages/lab36/Lab36Page'));
const LabSubpage = lazy(() => import('./pages/shared/LabSubpage'));

function App() {
  return (
    <Router>
      <DataSelectionProvider>
        <div className="App">
          <Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="lab42" element={<Lab42Page />} />
              <Route path="lab36" element={<Lab36Page />} />
              <Route path="lab42/*" element={<LabSubpage labType="lab42" />} />
              <Route path="lab36/*" element={<LabSubpage labType="lab36" />} />
            </Route>
          </Routes>
          </Suspense>
        </div>
      </DataSelectionProvider>
    </Router>
  );
}

export default App;