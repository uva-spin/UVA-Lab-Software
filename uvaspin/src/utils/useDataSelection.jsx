import { useState, useCallback, createContext, useContext } from 'react';

// Create context for data selection
const DataSelectionContext = createContext();

// Provider component
export const DataSelectionProvider = ({ children }) => {
    const [selectedParameters, setSelectedParameters] = useState(new Set());
    const [activePlotId, setActivePlotId] = useState(null);
    const [plotData, setPlotData] = useState({}); // Store data for each plot

    const toggleParameter = useCallback((parameter) => {
        if (activePlotId) {
            setPlotData(prev => {
                const newPlotData = { ...prev };
                if (!newPlotData[activePlotId]) {
                    newPlotData[activePlotId] = new Set();
                }
                const plotParams = new Set(newPlotData[activePlotId]);
                if (plotParams.has(parameter)) {
                    plotParams.delete(parameter);
                } else {
                    plotParams.add(parameter);
                }
                newPlotData[activePlotId] = plotParams;
                return newPlotData;
            });
        } else {
            setSelectedParameters(prev => {
                const newSet = new Set(prev);
                if (newSet.has(parameter)) {
                    newSet.delete(parameter);
                } else {
                    newSet.add(parameter);
                }
                return newSet;
            });
        }
    }, [activePlotId]);

    const clearSelection = useCallback(() => {
        if (activePlotId) {
            setPlotData(prev => {
                const newPlotData = { ...prev };
                newPlotData[activePlotId] = new Set();
                return newPlotData;
            });
        } else {
            setSelectedParameters(new Set());
        }
    }, [activePlotId]);

    const clearPlot = useCallback((plotId) => {
        setPlotData(prev => {
            const newPlotData = { ...prev };
            newPlotData[plotId] = new Set();
            return newPlotData;
        });
    }, []);

    const selectAll = useCallback((parameters) => {
        if (activePlotId) {
            setPlotData(prev => {
                const newPlotData = { ...prev };
                newPlotData[activePlotId] = new Set(parameters);
                return newPlotData;
            });
        } else {
            setSelectedParameters(new Set(parameters));
        }
    }, [activePlotId]);

    const isSelected = useCallback((parameter) => {
        if (activePlotId && plotData[activePlotId]) {
            return plotData[activePlotId].has(parameter);
        }
        return selectedParameters.has(parameter);
    }, [selectedParameters, activePlotId, plotData]);

    const addParameters = useCallback((parameters) => {
        if (activePlotId) {
            setPlotData(prev => {
                const newPlotData = { ...prev };
                if (!newPlotData[activePlotId]) {
                    newPlotData[activePlotId] = new Set();
                }
                const plotParams = new Set(newPlotData[activePlotId]);
                parameters.forEach(param => plotParams.add(param));
                newPlotData[activePlotId] = plotParams;
                return newPlotData;
            });
        } else {
            setSelectedParameters(prev => {
                const newSet = new Set(prev);
                parameters.forEach(param => newSet.add(param));
                return newSet;
            });
        }
    }, [activePlotId]);

    const removeParameters = useCallback((parameters) => {
        if (activePlotId && plotData[activePlotId]) {
            setPlotData(prev => {
                const newPlotData = { ...prev };
                const plotParams = new Set(newPlotData[activePlotId]);
                parameters.forEach(param => plotParams.delete(param));
                newPlotData[activePlotId] = plotParams;
                return newPlotData;
            });
        } else {
            setSelectedParameters(prev => {
                const newSet = new Set(prev);
                parameters.forEach(param => newSet.delete(param));
                return newSet;
            });
        }
    }, [activePlotId, plotData]);

    const setActivePlot = useCallback((plotId) => {
        setActivePlotId(plotId);
    }, []);

    const getPlotParameters = useCallback((plotId) => {
        return plotData[plotId] || new Set();
    }, [plotData]);

    const value = {
        selectedParameters,
        activePlotId,
        plotData,
        toggleParameter,
        clearSelection,
        clearPlot,
        selectAll,
        isSelected,
        addParameters,
        removeParameters,
        setActivePlot,
        getPlotParameters,
        count: selectedParameters.size
    };

    return (
        <DataSelectionContext.Provider value={value}>
            {children}
        </DataSelectionContext.Provider>
    );
};

// Hook to use data selection
export const useDataSelection = () => {
    const context = useContext(DataSelectionContext);
    if (!context) {
        throw new Error('useDataSelection must be used within a DataSelectionProvider');
    }
    return context;
};
