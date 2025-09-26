import React, { useState, useEffect } from 'react';
import TimePicker from 'react-time-picker';
import 'react-time-picker/dist/TimePicker.css';
import '../pages/LabPage.css';

function TimeTravel({ value, onChange, maxHours = 72 }) {
    const [time, setTime] = useState(value || '00:01:00');

    // Update internal state when value prop changes
    useEffect(() => {
        if (value !== undefined) {
            setTime(value);
        }
    }, [value]);

    const handleTimeChange = (newTime) => {
        setTime(newTime);
        
        // Validate maximum hours limit
        if (newTime) {
            const [hours, minutes, seconds] = newTime.split(':').map(Number);
            const totalHours = hours + minutes / 60 + seconds / 3600;
            
            if (totalHours > maxHours) {
                // Cap at maximum hours
                const cappedHours = Math.min(hours, maxHours);
                const cappedTime = `${cappedHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                setTime(cappedTime);
                onChange && onChange(cappedTime);
                return;
            }
        }
        
        onChange && onChange(newTime);
    };

    return (
        <div className="my-custom-time-picker">
            <TimePicker 
                value={time} 
                onChange={handleTimeChange} 
                format="HH:mm:ss" 
                disableClock={true}
                maxDetail="second"
            />
        </div>
    );
}

export default TimeTravel;