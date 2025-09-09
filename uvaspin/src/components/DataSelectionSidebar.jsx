import React, { useState } from 'react';

function DataSelectionSidebar({ onParameterToggle, selectedParameters }) {
    const [expandedSections, setExpandedSections] = useState(new Set());
    const [expandedSubSections, setExpandedSubSections] = useState(new Set());

    // Data structure based on the HTML example
    const dataStructure = {
        'QT': {
            'Pressures': ['pt501_ai', 'pt502_ai', 'pt503_ai', 'pt504_ai'],
            'Flows': ['fc501_ai', 'fc501_out', 'fc502_ai', 'fc502_out'],
            'Temperatures': ['ait501_ai', 'ti501_ai', 'ti502_ai', 'ti503_ai', 'ti504_ai', 'ti505_ai', 'ti523_ai'],
            'Level Indicators': ['lit501_ai'],
            'Purity Meter': ['ait501_ai']
        },
        'Pressures': [
            'root_exhaust_pressure', 'buffer_pressure', 'magnet_pressure', 
            'purifier_inlet_pressure', 'fridge_vapor_pressure', 'maxigauge_pressure', 'ivc_pressure'
        ],
        'Temperatures': [
            'thermocouple', 'magnet_bottom_temperature', 'magnet_top_temperature',
            'fridge_target_top_up_temperature', 'fridge_target_top_up_center_temperature',
            'fridge_target_top_down_temperature', 'fridge_target_bottom_up_temperature',
            'fridge_target_bottom_up_center_temperature', 'fridge_target_bottom_down_temperature',
            'fridge_target_top_cernox_temperature', 'fridge_target_bottom_cernox_temperature',
            'magnet_channel_1', 'magnet_channel_2', 'magnet_channel_3', 'magnet_channel_4',
            'magnet_channel_5', 'magnet_channel_6', 'magnet_channel_7', 'magnet_channel_8'
        ],
        'Flows': [
            'separator_flow', 'magnet_flow', 'main_flow', 'microwave_flow', 'heat_exchanger_flow'
        ],
        'NMR': [
            'run_number', 'measurement_type', 'peak_amp', 'peak_center', 'beam_on', 'rf_level',
            'if_atten', 'he_temperature', 'he_pressure', 'nmr_channel', 'temperature',
            'calibration_constant', 'polarization', 'polarization_std', 'snr', 'step_width',
            'center_freq', 'freq_span', 'area', 'phase_voltage', 'tune_voltage'
        ]
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
                    onClick={() => toggleSubSection(subSectionId)}
                >
                    <i className={`fas fa-chevron-right ${isExpanded ? 'expanded' : ''}`}></i>
                    <span>{categoryName}</span>
                    <span className="section-count">{columns.length}</span>
                </div>
                <div className={`section-content sub-content ${isExpanded ? 'expanded' : ''}`}>
                    {columns.map(columnName => (
                        <div 
                            key={columnName}
                            className={`parameter-item ${selectedParameters.has(columnName) ? 'selected' : ''}`}
                            onClick={() => onParameterToggle(columnName)}
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
                            onClick={() => toggleMainSection(mainSectionId)}
                        >
                            <i className={`fas fa-chevron-right ${isExpanded ? 'expanded' : ''}`}></i>
                            <span>{mainCategory}</span>
                            <span className="section-count">{getTotalColumnCount(subCategories)}</span>
                        </div>
                        <div className={`section-content main-content ${isExpanded ? 'expanded' : ''}`}>
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
                                        className={`parameter-item ${selectedParameters.has(columnName) ? 'selected' : ''}`}
                                        onClick={() => onParameterToggle(columnName)}
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
