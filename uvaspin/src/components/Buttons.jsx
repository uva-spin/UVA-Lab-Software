import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Lab42Button() {
    const location = useLocation();
    const isActive = location.pathname === '/lab42';
    
    return (
        <Link 
            to="/lab42" 
            className={`banner-link ${isActive ? 'active' : ''}`}
        >
            Lab 042
        </Link>
    );
}

function Lab36Button() {
    const location = useLocation();
    const isActive = location.pathname === '/lab36';
    
    return (
        <Link 
            to="/lab36" 
            className={`banner-link ${isActive ? 'active' : ''}`}
        >
            Lab 036
        </Link>
    );
}

function HistoryButton() {
    const location = useLocation();
    const isActive = location.pathname === '/history';
    
    return (
        <Link 
            to="/history" 
            className={`banner-link ${isActive ? 'active' : ''}`}
        >
            History
        </Link>
    );
}

function HomeButton() {
    const location = useLocation();
    const isActive = location.pathname === '/';
    
    return (
        <Link 
            to="/" 
            className={`banner-link ${isActive ? 'active' : ''}`}
        >
            <i className="fas fa-home"></i> Home
        </Link>
    );
}

function SidePanelButton({ onClick, isActive = false }) {
    return (
        <button 
            className={`sidebar-toggle ${isActive ? 'active' : ''}`}
            onClick={onClick}
            title="Toggle Data Selection"
        >
            <i className="fas fa-chevron-right"></i>
        </button>
    );
}

export { Lab42Button, Lab36Button, HistoryButton, HomeButton, SidePanelButton };
