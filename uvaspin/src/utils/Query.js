// Query utilities for database operations
let cache = new Map();

export function clear_cache() {
    cache.clear();
    console.log('Cache cleared');
}

// Convert ISO timestamp to database format (yy-mm-dd hh:mm:ss)
function formatTimestampForDB(isoString) {
    if (!isoString) return null;
    
    const date = new Date(isoString);
    const year = date.getFullYear().toString();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export async function fetchData(pool, table_name, keys, start_time, end_time) {
    try {
        // Validate table name to prevent SQL injection
        if (!table_name || typeof table_name !== 'string') {
            throw new Error('Invalid table name provided');
        }
        
        // Create cache key
        const cacheKey = `${table_name}_${keys}_${start_time}_${end_time}`;
        
        // Check cache first
        if (cache.has(cacheKey)) {
            console.log('Returning cached data');
            return cache.get(cacheKey);
        }

        // Build query with parameterized table name
        let query = `SELECT ${keys}, timestamp FROM \`${table_name}\``;
        const conditions = [];
        
        if (start_time) {
            const formattedStartTime = formatTimestampForDB(start_time);
            conditions.push(`timestamp >= '${formattedStartTime}'`);
        }
        if (end_time) {
            const formattedEndTime = formatTimestampForDB(end_time);
            conditions.push(`timestamp <= '${formattedEndTime}'`);
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