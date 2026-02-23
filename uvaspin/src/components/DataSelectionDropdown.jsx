import React, { useState, useEffect, useRef } from 'react';
import '../assets/css/DataSelectionDropdown.css';

function DataSelectionDropdown({ 
    label, 
    options, 
    selectedValues, 
    onSelectionChange, 
    multiple = true,
    placeholder = "Select options..."
}) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Handle clicks outside the dropdown to close it
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

    const handleToggle = () => {
        setIsOpen(!isOpen);
    };
    
    const handleOptionClick = (option) => {
        if (multiple) {
            const newSelection = selectedValues.includes(option)
                ? selectedValues.filter(val => val !== option)
                : [...selectedValues, option];
            onSelectionChange(newSelection);
        } else {
            onSelectionChange([option]);
            setIsOpen(false);
        }
    };

    const handleSelectAll = () => {
        if (multiple) {
            onSelectionChange(options);
        }
    };

    const handleClearAll = () => {
        onSelectionChange([]);
    };

    const getDisplayText = () => {
        if (selectedValues.length === 0) {
            return placeholder;
        }
        if (selectedValues.length === 1) {
            return selectedValues[0];
        }
        if (selectedValues.length === options.length) {
            return `All ${label.toLowerCase()} (${selectedValues.length})`;
        }
        return `${label} (${selectedValues.length} selected)`;
    };

    return (
        <div className="data-selection-dropdown" ref={dropdownRef}>
            <label className="dropdown-label">{label}:</label>
            <div className="dropdown-container">
                <button 
                    className={`dropdown-button ${isOpen ? 'open' : ''}`}
                    onClick={handleToggle}
                >
                    <span className="dropdown-text">{getDisplayText()}</span>
                    <i className={`fas fa-chevron-down ${isOpen ? 'rotated' : ''}`}></i>
                </button>
                
                <div className={`dropdown-menu ${isOpen ? 'open' : ''}`}>
                    {multiple && (
                        <div className="dropdown-actions">
                            <button 
                                className="action-button select-all"
                                onClick={handleSelectAll}
                            >
                                Select All
                            </button>
                            <button 
                                className="action-button clear-all"
                                onClick={handleClearAll}
                            >
                                Clear All
                            </button>
                        </div>
                    )}
                    <div className="dropdown-options">
                        {options.map(option => (
                            <div 
                                key={option}
                                className={`dropdown-option ${selectedValues.includes(option) ? 'selected' : ''}`}
                                onClick={() => handleOptionClick(option)}
                            >
                                {multiple && (
                                    <input 
                                        type="checkbox" 
                                        checked={selectedValues.includes(option)}
                                        readOnly
                                    />
                                )}
                                <span>{option}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default DataSelectionDropdown;
