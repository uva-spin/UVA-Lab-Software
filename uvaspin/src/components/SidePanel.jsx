import React, { useEffect, useRef } from 'react';
import './SidePanel.css';
import DataSelectionSidebar from './DataSelectionSidebar';
import { useDataSelection } from '../utils/useDataSelection';

function SidePanel({ isOpen, onToggle }) {
    const sidebarRef = useRef(null);
    const { 
        selectedParameters, 
        toggleParameter, 
        activePlotId,
        activeLabType,
        getPlotParameters,
        clearSelection 
    } = useDataSelection();
    
    // Get parameters for the active plot if one is selected
    const currentPlotParameters = activePlotId && activeLabType 
        ? getPlotParameters(activePlotId, activeLabType)
        : selectedParameters;

    // Handle clicking outside the sidebar to close it
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (isOpen && sidebarRef.current && !sidebarRef.current.contains(event.target)) {
                // Check if the click is not on the sidebar toggle button
                const toggleButton = document.querySelector('.sidebar-toggle');
                if (toggleButton && !toggleButton.contains(event.target)) {
                    onToggle();
                }
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen, onToggle]);

    return (
        <>
            <button 
                className={`sidebar-toggle ${isOpen ? 'active' : ''}`}
                onClick={onToggle}
                title="Toggle Data Selection"
            >
                Data
            </button>
            <div ref={sidebarRef} className={`data-sidebar ${isOpen ? 'active' : ''}`}>
                <div className="sidebar-header">
                    <h2>Database Selection</h2>
                    <p>
                        {activePlotId 
                            ? `Selecting for ${activePlotId.replace('plot-', 'Plot ')}` 
                            : 'Click on a plot to select data'
                        }
                    </p>
                    {activePlotId && (
                        <button 
                            className="clear-all-button"
                            onClick={clearSelection}
                            title="Clear current plot selection"
                        >
                            <i className="fas fa-trash"></i> Clear Selection
                        </button>
                    )}
                </div>
                <DataSelectionSidebar 
                    onParameterToggle={toggleParameter}
                    selectedParameters={currentPlotParameters}
                />
            </div>
        </>
    );
}

export default SidePanel;
