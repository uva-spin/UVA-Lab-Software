import React from 'react';

const Banner = ({ title, homeButton, lab42Button, lab36Button, historyButton, sidePanelButton }) => {
    return (
        <header className="header-banner">
            <div className="banner-content">
                <div className="banner-title">
                    <span>{title}</span>
                </div>
                <div className="banner-links">
                    {homeButton}
                    {lab42Button}
                    {lab36Button}   
                    {historyButton}
                </div>
                <div className="banner-controls">
                    {sidePanelButton}
                </div>
            </div>
        </header>
    );
};

export default Banner;
