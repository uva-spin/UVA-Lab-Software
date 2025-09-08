import {React, } from 'react';
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

function toggleSidePanelMenu() {
    const fabMenu = document.querySelector('.fab-menu');
    const fab = document.querySelector('.fab');
    fabMenu.classList.toggle('active');
    fab.classList.toggle('active');
}

function sidePanelButton() {
    return (
        <button className="sidebar-toggle" onClick={toggleSidePanelMenu}>
            <i className="fas fa-chevron-right"></i>
        </button>
    );
}

function toggleSidePanel() {
    const sidebar = document.querySelector('.side-panel');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    const dimmingOverlay = document.getElementById('dimming-overlay');
    
    sidebar.classList.toggle('active');
    toggleBtn.classList.toggle('active');
    dimmingOverlay.classList.toggle('active');
}

export { lab42Button, lab36Button, sidePanelButton, toggleSidePanel };