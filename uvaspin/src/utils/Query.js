// Query utilities for database operations
let cache = new Map();

export function clear_cache() {
    cache.clear();
    console.log('Cache cleared');
}

export async function fetchData(pool, table_name, keys, start_time, end_time) {
    try {
        // Create cache key
        const cacheKey = `${table_name}_${keys}_${start_time}_${end_time}`;
        
        // Check cache first
        if (cache.has(cacheKey)) {
            console.log('Returning cached data');
            return cache.get(cacheKey);
        }

        // Build query
        let query = `SELECT ${keys}, timestamp FROM ${table_name}`;
        const conditions = [];
        
        if (start_time) {
            conditions.push(`timestamp >= '${start_time}'`);
        }
        if (end_time) {
            conditions.push(`timestamp <= '${end_time}'`);
        }
        
        if (conditions.length > 0) {
            query += ` WHERE ${conditions.join(' AND ')}`;
        }
        
        query += ` ORDER BY timestamp ASC`;

        console.log('Executing query:', query);
        
        // Execute query
        const result = await pool.query(query);
        
        // Cache the result
        cache.set(cacheKey, result);
        
        return result;
        
    } catch (error) {
        console.error('Error in fetchData:', error);
        throw error;
    }
}