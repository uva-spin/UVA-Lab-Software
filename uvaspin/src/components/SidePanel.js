import {React, useState, useEffect} from 'react';
import styled from "styled-components";
import '../../css/SidePanel.css';

const Nav = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background-color: #f0f0f0;
`;

const NavButton = styled.button`
    background-color: #f0f0f0;
    border: none;
    padding: 1rem;
    cursor: pointer;
`;

const SidePanelNav = styled.nav`
    background: #15171c;
    width: 250px;
    height: 100vh;
    display: flex;
    justify-content: center;
    position: fixed;
    right: ${({ sidePanel }) => (sidePanel ? "0" : "-100%")};
    transition: 350ms;
    z-index: 10;
`;

const SidePanelContent = styled.div`
width: 100%
`;

function SidePanel() {
    const [sidePanelToggle, setSidePanelToggle] = useState(false);

    const showSidePanel = () => setSidePanelToggle(!sidePanelToggle);

    return (
        <>
        <Nav>
            <NavButton onClick={showSidePanel}>
            </NavButton>
        </Nav>
        <SidePanelNav className={`$(sidePanelToggled ? "visible" : "hidden")`} sidePanel={sidePanel}>
            <SidePanelContent className={`$(sidePanelToggled ? "visible" : "hidden")`}>
                <h1> Database Selection</h1>
            </SidePanelContent>
        </SidePanelNav>
        </>
        // <>
        // <button className="side-panel-button" id="side-panel-button" onClick={showSidePanel}>Show Sidepanel</button>
        // <div className={`side-panel ${sidePanel ? 'open' : ''}`}>
        //     <h1>Side Panel</h1>
        //     <button className="close-side-panel-button" id="close-side-panel-button" onClick={showSidePanel}>Close Sidepanel</button>
        // </div>
        // </>
    )
}

export default SidePanel;