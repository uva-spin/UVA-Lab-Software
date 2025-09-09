import React from 'react';
import '../../css/SidePanel.css';
import DataSelectionSidebar from './DataSelectionSidebar';
import { useDataSelection } from '../utils/useDataSelection';

function SidePanel({ isOpen, onToggle }) {
    const { 
        selectedParameters, 
        toggleParameter, 
        activePlotId,
        clearSelection 
    } = useDataSelection();

    return (
        <>
            <button 
                className={`sidebar-toggle ${isOpen ? 'active' : ''}`}
                onClick={onToggle}
                title="Toggle Data Selection"
            >
                Data
            </button>
            <div className={`data-sidebar ${isOpen ? 'active' : ''}`}>
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
                    selectedParameters={selectedParameters}
                />
            </div>
        </>
    );
}

export default SidePanel;
