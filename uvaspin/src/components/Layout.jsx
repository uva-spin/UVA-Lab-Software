import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Banner from './Banner';
import { Lab42Button, Lab36Button, HomeButton, SidePanelButton } from './Buttons';
import SidePanel from './SidePanel';

function Layout() {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const location = useLocation();

    const handleSidebarToggle = () => {
        setSidebarOpen(!sidebarOpen);
    };

    // Don't show sidebar on home page or non-realtime tabs
    const showSidebar = location.pathname !== '/' && 
                       !location.pathname.includes('/history') && 
                       !location.pathname.includes('/nmr') && 
                       !location.pathname.includes('/averaging');

    return (
        <div className="app-layout">
            <Banner 
                title="UVA Polarized Target Group Labs System Panel" 
                homeButton={<HomeButton />}
                lab42Button={<Lab42Button />}
                lab36Button={<Lab36Button />}
                sidePanelButton={showSidebar ? <SidePanelButton onClick={handleSidebarToggle} isActive={sidebarOpen} /> : null}
            />
            <main>
                <Outlet />
            </main>
            {showSidebar && (
                <SidePanel 
                    isOpen={sidebarOpen} 
                    onToggle={handleSidebarToggle} 
                />
            )}
        </div>
    );
}

export default Layout;
