import React, { useState, useEffect } from 'react';
import TimePicker from 'react-time-picker';
import 'react-time-picker/dist/TimePicker.css';

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
                setStartDate(yesterday.toLocaleDateString());
            }
            if (!endDate) {
                setEndDate(now.toLocaleDateString());
            }
        }
    }, [startDate, endDate]);

    // Notify parent when dates change
    useEffect(() => {
        if (startDate && endDate && startTime && endTime && onDateRangeChange) {
            // Ensure time is in HH:mm format
            const formatTime = (time) => {
                if (!time) return '00:00';
                // If time is already in HH:mm format, use it directly
                if (typeof time === 'string' && time.match(/^\d{2}:\d{2}$/)) {
                    return time;
                }
                // If time is in HH:mm:ss format, truncate to HH:mm
                if (typeof time === 'string' && time.match(/^\d{2}:\d{2}:\d{2}$/)) {
                    return time.slice(0, 5);
                }
                return '00:00';
            };

            const formattedStartTime = formatTime(startTime);
            const formattedEndTime = formatTime(endTime);
            
            const startDateTime = new Date(`${startDate}T${formattedStartTime}:00`);
            const endDateTime = new Date(`${endDate}T${formattedEndTime}:59`);
            
            console.log('DateTimePicker: Creating date range:', {
                startDate,
                startTime,
                formattedStartTime,
                startDateTime: startDateTime.toLocaleString(),
                endDate,
                endTime,
                formattedEndTime,
                endDateTime: endDateTime.toLocaleString()
            });
            
            onDateRangeChange(startDateTime, endDateTime);
        }
    }, [startDate, startTime, endDate, endTime, onDateRangeChange]);

    const handleStartDateChange = (e) => {
        setStartDate(e.target.value);
    };

    const handleStartTimeChange = (time) => {
        console.log('DateTimePicker: Start time changed:', time);
        setStartTime(time || '00:00');
    };

    const handleEndDateChange = (e) => {
        setEndDate(e.target.value);
    };

    const handleEndTimeChange = (time) => {
        console.log('DateTimePicker: End time changed:', time);
        setEndTime(time || '23:59');
    };

    const handleQuickSelect = (hours) => {
        const now = new Date();
        const startDateTime = new Date(now.getTime() - hours * 60 * 60 * 1000);
        
        setStartDate(startDateTime.toLocaleDateString());
        setStartTime(startDateTime.toTimeString().slice(0, 5));
        setEndDate(now.toLocaleDateString());
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
                        <TimePicker
                            value={startTime}
                            onChange={handleStartTimeChange}
                            format="HH:mm"
                            disableClock={true}
                            clearIcon={null}
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
                        <TimePicker
                            value={endTime}
                            onChange={handleEndTimeChange}
                            format="HH:mm"
                            disableClock={true}
                            clearIcon={null}
                            className="time-input"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default DateTimePicker;
