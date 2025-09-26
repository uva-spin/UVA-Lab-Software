import { useState, useCallback, createContext, useContext } from 'react';

// Create context for data selection
const DataSelectionContext = createContext();

// Provider component
export const DataSelectionProvider = ({ children }) => {
    const [selectedParameters, setSelectedParameters] = useState(new Set());
    const [activePlotId, setActivePlotId] = useState(null);
    const [plotData, setPlotData] = useState({}); // Store data for each plot
    const [activeLabType, setActiveLabTypeState] = useState(null); // Track current lab type

    const toggleParameter = useCallback((parameter) => {
        if (activePlotId && activeLabType) {
            const labSpecificPlotId = `${activeLabType}-${activePlotId}`;
            setPlotData(prev => {
                const newPlotData = { ...prev };
                if (!newPlotData[labSpecificPlotId]) {
                    newPlotData[labSpecificPlotId] = new Set();
                }
                const plotParams = new Set(newPlotData[labSpecificPlotId]);
                if (plotParams.has(parameter)) {
                    plotParams.delete(parameter);
                } else {
                    plotParams.add(parameter);
                }
                newPlotData[labSpecificPlotId] = plotParams;
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
    }, [activePlotId, activeLabType]);

    const clearSelection = useCallback(() => {
        if (activePlotId && activeLabType) {
            const labSpecificPlotId = `${activeLabType}-${activePlotId}`;
            setPlotData(prev => {
                const newPlotData = { ...prev };
                newPlotData[labSpecificPlotId] = new Set();
                return newPlotData;
            });
        } else {
            setSelectedParameters(new Set());
        }
    }, [activePlotId, activeLabType]);

    const clearPlot = useCallback((plotId, labType) => {
        const labSpecificPlotId = `${labType}-${plotId}`;
        setPlotData(prev => {
            const newPlotData = { ...prev };
            newPlotData[labSpecificPlotId] = new Set();
            return newPlotData;
        });
    }, []);

    const selectAll = useCallback((parameters) => {
        if (activePlotId && activeLabType) {
            const labSpecificPlotId = `${activeLabType}-${activePlotId}`;
            setPlotData(prev => {
                const newPlotData = { ...prev };
                newPlotData[labSpecificPlotId] = new Set(parameters);
                return newPlotData;
            });
        } else {
            setSelectedParameters(new Set(parameters));
        }
    }, [activePlotId, activeLabType]);

    const isSelected = useCallback((parameter) => {
        if (activePlotId && activeLabType) {
            const labSpecificPlotId = `${activeLabType}-${activePlotId}`;
            return plotData[labSpecificPlotId]?.has(parameter) || false;
        }
        return selectedParameters.has(parameter);
    }, [selectedParameters, activePlotId, activeLabType, plotData]);

    const addParameters = useCallback((parameters) => {
        if (activePlotId && activeLabType) {
            const labSpecificPlotId = `${activeLabType}-${activePlotId}`;
            setPlotData(prev => {
                const newPlotData = { ...prev };
                if (!newPlotData[labSpecificPlotId]) {
                    newPlotData[labSpecificPlotId] = new Set();
                }
                const plotParams = new Set(newPlotData[labSpecificPlotId]);
                parameters.forEach(param => plotParams.add(param));
                newPlotData[labSpecificPlotId] = plotParams;
                return newPlotData;
            });
        } else {
            setSelectedParameters(prev => {
                const newSet = new Set(prev);
                parameters.forEach(param => newSet.add(param));
                return newSet;
            });
        }
    }, [activePlotId, activeLabType]);

    const removeParameters = useCallback((parameters) => {
        if (activePlotId && activeLabType) {
            const labSpecificPlotId = `${activeLabType}-${activePlotId}`;
            if (plotData[labSpecificPlotId]) {
                setPlotData(prev => {
                    const newPlotData = { ...prev };
                    const plotParams = new Set(newPlotData[labSpecificPlotId]);
                    parameters.forEach(param => plotParams.delete(param));
                    newPlotData[labSpecificPlotId] = plotParams;
                    return newPlotData;
                });
            }
        } else {
            setSelectedParameters(prev => {
                const newSet = new Set(prev);
                parameters.forEach(param => newSet.delete(param));
                return newSet;
            });
        }
    }, [activePlotId, activeLabType, plotData]);

    const setActivePlot = useCallback((plotId) => {
        setActivePlotId(plotId);
    }, []);

    const setActiveLabType = useCallback((labType) => {
        setActiveLabTypeState(labType);
    }, []);

    const getPlotParameters = useCallback((plotId, labType) => {
        const labSpecificPlotId = `${labType}-${plotId}`;
        return plotData[labSpecificPlotId] || new Set();
    }, [plotData]);

    const value = {
        selectedParameters,
        activePlotId,
        activeLabType,
        plotData,
        toggleParameter,
        clearSelection,
        clearPlot,
        selectAll,
        isSelected,
        addParameters,
        removeParameters,
        setActivePlot,
        setActiveLabType,
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
