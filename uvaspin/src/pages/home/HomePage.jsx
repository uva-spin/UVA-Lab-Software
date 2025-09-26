import React from 'react';
import { Link } from 'react-router-dom';
import '/src/pages/css/HomePage.css';

function HomePage() {
    return (
        <div className="home-page">
            <div className="home-content">
                <h1>UVA Polarized Target Group Labs System Panel</h1>
                <p>Select a lab to view real-time data and monitoring</p>
                <div className="lab-selection">
                    <Link to="/lab42/realtime" className="lab-card">
                        <div className="lab-icon">
                            <i className="fas fa-flask"></i>
                        </div>
                        <h3>Lab 042</h3>
                        <p>Real-time data, history, NMR display, and averaging</p>
                    </Link>
                    <Link to="/lab36/realtime" className="lab-card">
                        <div className="lab-icon">
                            <i className="fas fa-microscope"></i>
                        </div>
                        <h3>Lab 036</h3>
                        <p>Real-time data, history, NMR display, and averaging</p>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default HomePage;
