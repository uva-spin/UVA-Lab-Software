import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

function HomePage() {
    return (
        <div className="home-page">
            <div className="home-content">
                <h1>UVA Polarized Target Group Labs System Panel</h1>
                <p>Select a lab to view real-time data and monitoring</p>
                <div className="lab-selection">
                    <Link to="/lab42" className="lab-card">
                        <div className="lab-icon">
                            <i className="fas fa-flask"></i>
                        </div>
                        <h3>Lab 042</h3>
                        <p>Add description here</p>
                    </Link>
                    <Link to="/lab36" className="lab-card">
                        <div className="lab-icon">
                            <i className="fas fa-microscope"></i>
                        </div>
                        <h3>Lab 036</h3>
                        <p>Add description here</p>
                    </Link>
                    <Link to="/history" className="lab-card">
                        <div className="lab-icon">
                            <i className="fas fa-history"></i>
                        </div>
                        <h3>History</h3>
                        <p>Add description here</p>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default HomePage;
