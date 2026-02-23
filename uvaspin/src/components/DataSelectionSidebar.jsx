import React, { useState } from 'react';
import { useDataSelection } from '../utils/useDataSelection';
import { getDataStructure } from '../constants/dataStructure';

function DataSelectionSidebar({ onParameterToggle, selectedParameters }) {
    const [expandedSections, setExpandedSections] = useState(new Set());
    const [expandedSubSections, setExpandedSubSections] = useState(new Set());
    const [animatingItems, setAnimatingItems] = useState(new Set());
    const { plotData, activeLabType } = useDataSelection();
    const dataStructure = getDataStructure(activeLabType, true);
    
    const isParameterSelectedInAnyPlot = (parameter) => {
        if (!activeLabType) return false;
        
        // Check all plots for this lab type
        return Object.keys(plotData).some(plotKey => {
            if (plotKey.startsWith(`${activeLabType}-`)) {
                return plotData[plotKey]?.has(parameter) || false;
            }
            return false;
        });
    };

    const handleParameterToggle = (parameter) => {
        
        setAnimatingItems(prev => new Set([...prev, parameter]));
        
        setTimeout(() => {
            setAnimatingItems(prev => {
                const newSet = new Set(prev);
                newSet.delete(parameter);
                return newSet;
            });
        }, 400);
        
        // Toggle the parameter
        onParameterToggle(parameter);
    };


    const toggleMainSection = (sectionId) => {
        setExpandedSections(prev => {
            const newSet = new Set(prev);
            if (newSet.has(sectionId)) {
                newSet.delete(sectionId);
            } else {
                newSet.add(sectionId);
            }
            return newSet;
        });
    };

    const toggleSubSection = (subSectionId) => {
        setExpandedSubSections(prev => {
            const newSet = new Set(prev);
            if (newSet.has(subSectionId)) {
                newSet.delete(subSectionId);
            } else {
                newSet.add(subSectionId);
            }
            return newSet;
        });
    };

    const getTotalColumnCount = (subCategories) => {
        if (Array.isArray(subCategories)) {
            return subCategories.length;
        }
        return Object.values(subCategories).reduce((total, items) => total + items.length, 0);
    };

    const createSubSection = (categoryName, columns, parentId) => {
        const subSectionId = `${parentId}-${categoryName.toLowerCase().replace(/\s+/g, '-')}`;
        const isExpanded = expandedSubSections.has(subSectionId);

        return (
            <div key={subSectionId} className="data-section sub-section">
                <div 
                    className="section-header sub-header"
                    onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        toggleSubSection(subSectionId);
                    }}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            e.stopPropagation();
                            toggleSubSection(subSectionId);
                        }
                    }}
                >
                    <i className={`fas fa-chevron-right ${isExpanded ? 'expanded' : ''}`}></i>
                    <span>{categoryName}</span>
                    <span className="section-count">{columns.length}</span>
                </div>
                <div className={`section-content sub-content ${isExpanded ? 'expanded' : ''}`}>
                    {columns.map(columnName => (
                        <div 
                            key={columnName}
                            className={`parameter-item ${isParameterSelectedInAnyPlot(columnName) ? 'selected' : ''} ${animatingItems.has(columnName) ? 'selecting' : ''}`}
                            onClick={() => handleParameterToggle(columnName)}
                        >
                            {columnName}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="data-selection-sidebar">
            <div className="sidebar-header">
                <h2>Database Selection</h2>
                <p>Select parameters to display on the plots</p>
            </div>
            
            {Object.entries(dataStructure).map(([mainCategory, subCategories]) => {
                const mainSectionId = `main-${mainCategory.toLowerCase().replace(/\s+/g, '-')}`;
                const isExpanded = expandedSections.has(mainSectionId);

                return (
                    <div key={mainSectionId} className={`data-section main-category ${isExpanded ? 'expanded' : ''}`}>
                        <div 
                            className="section-header main-header"
                            onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                toggleMainSection(mainSectionId);
                            }}
                            role="button"
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    toggleMainSection(mainSectionId);
                                }
                            }}
                        >
                            <i className={`fas fa-chevron-right ${isExpanded ? 'expanded' : ''}`}></i>
                            <span>{mainCategory}</span>
                            <span className="section-count">{getTotalColumnCount(subCategories)}</span>
                        </div>
                        <div 
                            className={`section-content main-content ${isExpanded ? 'expanded' : ''}`}
                        >
                            {mainCategory === 'QT' ? (
                                // QT has subcategories
                                Object.entries(subCategories).map(([subCategory, subItems]) => 
                                    subItems.length > 0 ? createSubSection(subCategory, subItems, mainSectionId) : null
                                )
                            ) : (
                                // Other main categories are direct arrays
                                subCategories.map(columnName => (
                                    <div 
                                        key={columnName}
                                        className={`parameter-item ${isParameterSelectedInAnyPlot(columnName) ? 'selected' : ''} ${animatingItems.has(columnName) ? 'selecting' : ''}`}
                                        onClick={() => handleParameterToggle(columnName)}
                                    >
                                        {columnName}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

export default DataSelectionSidebar;
