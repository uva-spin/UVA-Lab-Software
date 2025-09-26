import { useState } from "react";
import React, {useState, useEffect} from 'react';


function AveragePage(labtype) {
    const [timeRange, setTimeRange] = useState({start: null, end: null});
    const [selectedParameters, setSelectedParameters] = useState([]);
    const [nPoints, setNPoints] = useState(10);
    const [samplingFactor, setSamplingFactor] = useState(1);
    if (labtype == 'lab42') {
        const [selectedData, setSelectedData] = useState({
            qt: [],
            pressures: [],
            temperatures: [],
            flows: [],
            nmr: []
        })
    } else if (labtype == 'lab36') {
        const [selectedData, setSelectedData] = useState({
            qt: [],
            pressures: [],
            temperatures: [],
            flows: [],
            nmr: []
        })
    } else {
        const [selectedData, setSelectedData] = useState({null: []})
    }

    const handleTimeRangeChange = (start, end) => {
        setTimeRange({start, end});
    }

    const handleSelectedParametersChange = (parameters) => {
        setSelectedParameters(parameters);
    }

    const handleNPointsChange = (nPoints) => {
        setNPoints(nPoints);
    }

    const handleSamplingFactorChange = (samplingFactor) => {
        setSamplingFactor(samplingFactor);
    }

    const hasSelectedData = () => {
        return Object.values(selectedData).some(category => category.length > 0);
    };

    const handleAverage = () => {
        console.log('Average');
        console.log(timeRange);
        console.log(selectedParameters);
        console.log(nPoints);
        console.log(samplingFactor);
    }

    return (
        <div>
            <h1>Average Page</h1>
        </div>
    )
}

export default AveragePage;
}