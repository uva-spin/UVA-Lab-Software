import React from 'react';
import TimePicker from 'react-time-picker';
import 'react-time-picker/dist/TimePicker.css';
import '/src/pages/css/LabPage.css';

function TimeTravel({ time, setTime, maxHours = 72 }) {

    const validateAndUpdateTime = (newTime) => {
        if (!newTime) return null;
        
        try {
            const [hours, minutes, seconds] = newTime.split(':').map(Number);
            const totalHours = hours + minutes / 60 + seconds / 3600;
            
            if (totalHours > maxHours) {
                // Cap at maximum hours
                const cappedHours = Math.min(hours, maxHours);
                const cappedTime = `${cappedHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                console.log('TimeTravel: Capped time to:', cappedTime);
                return cappedTime;
            }
            return newTime;
        } catch (error) {
            console.warn('TimeTravel: Invalid time format:', newTime);
            return null;
        }
    };

    const handleTimeChange = (newTime) => {
        const validatedTime = validateAndUpdateTime(newTime);
        if (validatedTime !== null) {
            setTime(validatedTime);
        }
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