import React, { useState } from 'react';
import IndividualPlot from '../components/IndividualPlot';
import DateTimePicker from '../components/DateTimePicker';
import { useDataSelection } from '../utils/useDataSelection';

function HistoryPage() {
    const { selectedParameters } = useDataSelection();
    const [dateRange, setDateRange] = useState({ start: null, end: null });
    
    const handleDateRangeChange = (startDate, endDate) => {
        setDateRange({ start: startDate, end: endDate });
    };

    return (
        <div className="history-page">
            <div className="history-controls">
                <DateTimePicker 
                    onDateRangeChange={handleDateRangeChange}
                />
            </div>
            <div className="history-plot-container">
                <IndividualPlot 
                    plotId="history-plot" 
                    plotNumber="History" 
                    labType="history"
                    dateRange={dateRange}
                />
            </div>
        </div>
    );
}

export default HistoryPage;

