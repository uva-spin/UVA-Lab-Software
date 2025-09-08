import React from 'react';
import { lab42Button, lab36Button } from './Buttons';

const Banner = (title, lab42Button=null, lab36Button=null) => {
    return (
        <header class="header-banner">
            <div class="banner-content">
                <div class="banner-title">
                    <span>{title}</span>
                </div>
                <div class="banner-links">
                    lab42Button ? lab42Button() : null
                    lab36Button ? lab36Button() : null
                </div>
            </div>
        </header>
    );
};

export default Banner;