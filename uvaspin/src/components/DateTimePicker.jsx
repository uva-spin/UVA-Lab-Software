import React, { useState, useEffect } from 'react';

function DateTimePicker({ onDateRangeChange, initialStartDate, initialEndDate }) {
    const [startDate, setStartDate] = useState(initialStartDate || '');
    const [startTime, setStartTime] = useState('00:00');
    const [endDate, setEndDate] = useState(initialEndDate || '');
    const [endTime, setEndTime] = useState('23:59');

    // Initialize with default values if not provided
    useEffect(() => {
        if (!startDate || !endDate) {
            const now = new Date();
            const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
            
            if (!startDate) {
                setStartDate(yesterday.toISOString().split('T')[0]);
            }
            if (!endDate) {
                setEndDate(now.toISOString().split('T')[0]);
            }
        }
    }, [startDate, endDate]);

    // Notify parent when dates change
    useEffect(() => {
        if (startDate && endDate && onDateRangeChange) {
            const startDateTime = new Date(`${startDate}T${startTime}`);
            const endDateTime = new Date(`${endDate}T${endTime}`);
            onDateRangeChange(startDateTime, endDateTime);
        }
    }, [startDate, startTime, endDate, endTime, onDateRangeChange]);

    const handleStartDateChange = (e) => {
        setStartDate(e.target.value);
    };

    const handleStartTimeChange = (e) => {
        setStartTime(e.target.value);
    };

    const handleEndDateChange = (e) => {
        setEndDate(e.target.value);
    };

    const handleEndTimeChange = (e) => {
        setEndTime(e.target.value);
    };

    const handleQuickSelect = (hours) => {
        const now = new Date();
        const startDateTime = new Date(now.getTime() - hours * 60 * 60 * 1000);
        
        setStartDate(startDateTime.toISOString().split('T')[0]);
        setStartTime(startDateTime.toTimeString().slice(0, 5));
        setEndDate(now.toISOString().split('T')[0]);
        setEndTime(now.toTimeString().slice(0, 5));
    };

    return (
        <div className="datetime-picker">
            <div className="datetime-picker-header">
                <h3>Select Time Range</h3>
                <div className="quick-select-buttons">
                    <button onClick={() => handleQuickSelect(1)} className="quick-select-btn">
                        Last Hour
                    </button>
                    <button onClick={() => handleQuickSelect(6)} className="quick-select-btn">
                        Last 6 Hours
                    </button>
                    <button onClick={() => handleQuickSelect(24)} className="quick-select-btn">
                        Last 24 Hours
                    </button>
                    <button onClick={() => handleQuickSelect(168)} className="quick-select-btn">
                        Last Week
                    </button>
                </div>
            </div>
            
            <div className="datetime-inputs">
                <div className="datetime-group">
                    <label>Start Date & Time</label>
                    <div className="datetime-row">
                        <input
                            type="date"
                            value={startDate}
                            onChange={handleStartDateChange}
                            className="date-input"
                        />
                        <input
                            type="time"
                            value={startTime}
                            onChange={handleStartTimeChange}
                            className="time-input"
                        />
                    </div>
                </div>
                
                <div className="datetime-group">
                    <label>End Date & Time</label>
                    <div className="datetime-row">
                        <input
                            type="date"
                            value={endDate}
                            onChange={handleEndDateChange}
                            className="date-input"
                        />
                        <input
                            type="time"
                            value={endTime}
                            onChange={handleEndTimeChange}
                            className="time-input"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default DateTimePicker;
