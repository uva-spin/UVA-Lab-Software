import { useState, useEffect, useRef } from 'react';

// Cache duration in milliseconds (1 minute = 60000ms)
const CACHE_DURATION = 60000;

function usePageDataCache(pageKey, initialData = null) {
    const [data, setData] = useState(initialData);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const lastAccessTimeRef = useRef(Date.now());
    const cacheTimeoutRef = useRef(null);

    // Function to check if data should be cleared due to inactivity
    const checkCacheValidity = () => {
        const now = Date.now();
        const timeSinceLastAccess = now - lastAccessTimeRef.current;
        
        if (timeSinceLastAccess > CACHE_DURATION) {
            // Clear the data if it's been more than 1 minute since last access
            setData(null);
            setError(null);
            setIsLoading(false);
        }
    };

    // Update last access time when data is accessed
    const updateAccessTime = () => {
        lastAccessTimeRef.current = Date.now();
    };

    // Function to fetch new data
    const fetchData = async (fetchFunction) => {
        if (!fetchFunction) return;
        
        setIsLoading(true);
        setError(null);
        updateAccessTime();

        try {
            const newData = await fetchFunction();
            setData(newData);
        } catch (err) {
            setError(err.message || 'Failed to fetch data');
        } finally {
            setIsLoading(false);
        }
    };

    // Function to manually clear cache
    const clearCache = () => {
        setData(null);
        setError(null);
        setIsLoading(false);
        lastAccessTimeRef.current = Date.now();
    };

    // Function to set data manually (for real-time updates)
    const setDataManually = (newData) => {
        setData(newData);
        updateAccessTime();
    };

    // Set up periodic cache checking
    useEffect(() => {
        const interval = setInterval(checkCacheValidity, 30000); // Check every 30 seconds
        
        return () => {
            clearInterval(interval);
            if (cacheTimeoutRef.current) {
                clearTimeout(cacheTimeoutRef.current);
            }
        };
    }, []);

    // Clear cache when component unmounts
    useEffect(() => {
        return () => {
            clearCache();
        };
    }, []);

    return {
        data,
        isLoading,
        error,
        fetchData,
        clearCache,
        setDataManually,
        updateAccessTime
    };
}

export default usePageDataCache;
