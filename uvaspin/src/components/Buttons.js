import React from 'react';
import { Link } from 'react-router-dom';


function lab42Button() {
    return (
        <button className="banner-link">
            <Link to="/lab42">Lab 042</Link>
        </button>
    );
}

function lab36Button() {
    return (
        <button className="banner-link">
            <Link to="/lab36">Lab 036</Link>
        </button>
    );
}

function sidePanelButton() {
    return (
        <button className="sidebar-toggle">
            <i className="fas fa-chevron-right"></i>
        </button>
    );
}

export { lab42Button, lab36Button, sidePanelButton };