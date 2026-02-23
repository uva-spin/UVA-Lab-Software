// Query utilities for database operations
let cache = new Map();

export function clear_cache() {
    cache.clear();
    console.log('Cache cleared');
}

// Convert timestamp string to database format (yyyy-mm-dd hh:mm:ss)
// Accepts ISO 8601 (preferred) or locale strings
function formatTimestampForDB(timestampStr) {
    if (!timestampStr) return null;
    
    const date = new Date(timestampStr);
    if (Number.isNaN(date.getTime())) return null;
    const year = date.getFullYear().toString();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function parseValidatedTimestamp(timestampStr, label) {
    if (!timestampStr) return null;
    const formatted = formatTimestampForDB(timestampStr);
    if (!formatted) {
        throw new Error(`Invalid ${label} timestamp`);
    }
    return formatted;
}

function deriveModuloFactor(startTime, endTime) {
    if (!startTime || !endTime) {
        return 1;
    }

    const start = new Date(startTime).getTime();
    const end = new Date(endTime).getTime();
    if (Number.isNaN(start) || Number.isNaN(end) || end <= start) {
        return 1;
    }

    const diffMs = end - start;
    if (diffMs > 30 * 24 * 60 * 60 * 1000) return 1000;
    if (diffMs > 7 * 24 * 60 * 60 * 1000) return 500;
    if (diffMs > 24 * 60 * 60 * 1000) return 100;
    if (diffMs > 60 * 60 * 1000) return 10;
    return 1;
}

// Hash map table for column to database table mapping
const COLUMN_TO_TABLE_MAP = {
    // QT table columns
    'fc501_ai': 'QT',
    'fc501_out': 'QT',
    'fc502_ai': 'QT',
    'fc502_out': 'QT',
    'lit501_ai': 'QT',
    'pt501_ai': 'QT',
    'pt502_ai': 'QT',
    'pt503_ai': 'QT',
    'pt504_ai': 'QT',
    'ait501_ai': 'QT',
    'ti501_ai': 'QT',
    'ti502_ai': 'QT',
    'ti503_ai': 'QT',
    'ti504_ai': 'QT',
    'ti505_ai': 'QT',
    'ti523_ai': 'QT',
    
    // Labjack table columns
    'root_exhaust_pressure': 'Labjack',
    'buffer_pressure': 'Labjack',
    'magnet_pressure': 'Labjack',
    'purifier_inlet_pressure': 'Labjack',
    'fridge_vapor_pressure': 'Labjack',
    'thermocouple': 'Labjack',
    'magnet_bottom_temperature': 'Labjack',
    'magnet_top_temperature': 'Labjack',
    
    // Flow_Rates table columns
    'seperator_flow': 'Flow_Rates',
    'magnet_flow': 'Flow_Rates',
    'main_flow': 'Flow_Rates',
    'microwave_flow': 'Flow_Rates',
    'heat_exchanger_flow': 'Flow_Rates',
    
    // Lakeshore_Target_Stick table columns
    'target_stick_buffer_top_temperature': 'Lakeshore_Target_Stick',
    'target_stick_buffer_bottom_temperature': 'Lakeshore_Target_Stick',
    'target_stick_seperator_top_temperature': 'Lakeshore_Target_Stick',
    'target_stick_seperator_bottom_temperature': 'Lakeshore_Target_Stick',
    'target_stick_heat_exchanger_top_temperature': 'Lakeshore_Target_Stick',
    'target_stick_heat_exchanger_bottom_temperature': 'Lakeshore_Target_Stick',
    'target_stick_annealing_plate_bar_temperature': 'Lakeshore_Target_Stick',
    'target_stick_annealing_plate_top_temperature': 'Lakeshore_Target_Stick',
    
    // Lakeshore_Fridge_Temp table columns
    'fridge_target_top_up_temperature': 'Lakeshore_Fridge_Temp',
    'fridge_target_top_up_center_temperature': 'Lakeshore_Fridge_Temp',
    'fridge_target_top_down_temperature': 'Lakeshore_Fridge_Temp',
    'fridge_target_bottom_up_temperature': 'Lakeshore_Fridge_Temp',
    'fridge_target_bottom_up_center_temperature': 'Lakeshore_Fridge_Temp',
    'fridge_target_bottom_down_temperature': 'Lakeshore_Fridge_Temp',
    'fridge_target_top_cernox_temperature': 'Lakeshore_Fridge_Temp',
    'fridge_target_bottom_cernox_temperature': 'Lakeshore_Fridge_Temp',
    
    // Lakeshore_Magnet_Temp table columns
    'magnet_channel_1': 'Lakeshore_Magnet_Temp',
    'magnet_channel_2': 'Lakeshore_Magnet_Temp',
    'magnet_channel_3': 'Lakeshore_Magnet_Temp',
    'magnet_channel_4': 'Lakeshore_Magnet_Temp',
    'magnet_channel_5': 'Lakeshore_Magnet_Temp',
    'magnet_channel_6': 'Lakeshore_Magnet_Temp',
    'magnet_channel_7': 'Lakeshore_Magnet_Temp',
    'magnet_channel_8': 'Lakeshore_Magnet_Temp',
    
    // MaxiGauge table columns
    'maxigauge_seperator_inlet_pressure': 'MaxiGauge',
    'maxigauge_upper_roots_pressure': 'MaxiGauge',
    'maxigauge_channel_3': 'MaxiGauge',
    'maxigauge_channel_4': 'MaxiGauge',
    'maxigauge_channel_5': 'MaxiGauge',
    'maxigauge_channel_6': 'MaxiGauge',
    
    // IVC table columns
    'ivc_pressure': 'IVC',
    
    // NMR table columns
    'run_number': 'NMR',
    'measurement_type': 'NMR',
    'peak_amp': 'NMR',
    'peak_center': 'NMR',
    'beam_on': 'NMR',
    'rf_level': 'NMR',
    'if_atten': 'NMR',
    'he_temperature': 'NMR',
    'he_pressure': 'NMR',
    'nmr_channel': 'NMR',
    'temperature': 'NMR',
    'calibration_constant': 'NMR',
    'polarization': 'NMR',
    'polarization_std': 'NMR',
    'snr': 'NMR',
    'step_width': 'NMR',
    'center_freq': 'NMR',
    'freq_span': 'NMR',
    'area': 'NMR',
    'phase_voltage': 'NMR',
    'tune_voltage': 'NMR'
};

export async function fetchData(pool, keys, start_time, end_time) {
    const validatedStartTime = parseValidatedTimestamp(start_time, 'start_time');
    const validatedEndTime = parseValidatedTimestamp(end_time, 'end_time');
    const moduloFactor = deriveModuloFactor(start_time, end_time);

        console.log(`Query.js: Using modulo factor: ${moduloFactor}`);

    try {
        // Convert keys to array if it's a string
        const columnArray = Array.isArray(keys) ? keys : keys.split(',');
        
        // Group columns by their respective tables
        const tableGroups = {};
        columnArray.forEach(column => {
            const trimmedColumn = column.trim();
            const tableName = COLUMN_TO_TABLE_MAP[trimmedColumn];
            
            if (tableName) {
                if (!tableGroups[tableName]) {
                    tableGroups[tableName] = [];
                }
                tableGroups[tableName].push(trimmedColumn);
            } else {
                console.warn(`No table mapping found for column: ${trimmedColumn}`);
            }
        });

        // If no table groups found, return empty result
        if (Object.keys(tableGroups).length === 0) {
            console.warn('No valid table mappings found for the requested columns');
            return [];
        }

        console.log(`Querying ${Object.keys(tableGroups).length} tables:`, Object.keys(tableGroups));
        
        const cacheKey = `${Object.keys(tableGroups).sort().join('_')}_${keys}_${validatedStartTime || ''}_${validatedEndTime || ''}_${moduloFactor}`;
        
        // Check cache first
        if (cache.has(cacheKey)) {
            console.log('Returning cached data');
            return cache.get(cacheKey);
        }

        // Execute queries for each table and merge results
        const allResults = [];
        
        for (const [tableName, columns] of Object.entries(tableGroups)) {
            try {
                // First, get total count to calculate sampling interval
                let countQuery = `SELECT COUNT(*) as total_count FROM ${tableName}`;
                const conditions = [];
                const conditionParams = [];
                
                if (validatedStartTime) {
                    conditions.push('timestamp >= ?');
                    conditionParams.push(validatedStartTime);
                }
                if (validatedEndTime) {
                    conditions.push('timestamp <= ?');
                    conditionParams.push(validatedEndTime);
                }
                
                if (conditions.length > 0) {
                    countQuery += ` WHERE ${conditions.join(' AND ')}`;
                }
                
                const countResult = await new Promise((resolve, reject) => {
                    pool.query(countQuery, conditionParams, (err, rows) => {
                        if (err) {
                            console.error(`Error getting count for table ${tableName}:`, err);
                            resolve(0); 
                        } else {
                            resolve(rows[0]?.total_count || 0);
                        }
                    });
                });
                
                console.log(`Table ${tableName}: Total rows matching criteria: ${countResult}`);
                
                let query;
                                
                query = `SELECT ${columns.join(', ')}, timestamp FROM ${tableName}`;
                
                const allConditions = [...conditions];
                const queryParams = [...conditionParams];
                allConditions.push(`id % ${moduloFactor} = 0`);
                allConditions.push(`(${columns.map(col => `${col} IS NOT NULL`).join(' OR ')})`);
                
                if (allConditions.length > 0) {
                    query += ` WHERE ${allConditions.join(' AND ')}`;
                }
                
                query += ` ORDER BY timestamp ASC`;
                
                console.log(`Table ${tableName}: Using modulo sampling: id % ${moduloFactor} = 0`);



                console.log(`Executing query for table ${tableName}:`, query);
                
                // Execute query using promise-based approach
                const result = await new Promise((resolve, reject) => {
                    pool.query(query, queryParams, (err, rows) => {
                        if (err) {
                            console.error(`Error querying table ${tableName}:`, err);
                            reject(err);
                        } else {
                            console.log(`Query for table ${tableName} executed successfully, rows returned:`, rows ? rows.length : 0);
                            resolve(rows);
                        }
                    });
                });

                // Keep only rows that contain at least one non-null requested value.
                // This prevents "empty plots with lots of null rows" when tables are sparsely populated.
                if (result && result.length > 0) {
                    const filteredRows = result.filter(row =>
                        columns.some(col => row[col] !== null && row[col] !== undefined)
                    );

                    const enrichedResult = filteredRows.map(row => {
                        const r = { ...row, _table_source: tableName };
                        if (row.Timestamp !== undefined && r.timestamp === undefined) r.timestamp = row.Timestamp;
                        return r;
                    });

                    console.log(
                        `Table ${tableName}: non-null rows after filtering: ${enrichedResult.length}/${result.length}`
                    );
                    allResults.push(...enrichedResult);
                }
                
            } catch (tableError) {
                console.error(`Error querying table ${tableName}:`, tableError);
                // Continue with other tables even if one fails
            }
        }

        // Sort merged results by timestamp
        allResults.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        console.log(`Total merged results: ${allResults.length} rows`);
        
        // Cache the result
        cache.set(cacheKey, allResults);
        
        return allResults;
        
    } catch (error) {
        console.error('Error in fetchData:', error);
        throw error;
    }
}

export const fetchDataFromDB = async (selectedKeys, startTime = null, endTime = null) => {
    const now = new Date();
    const defaultStartTime = startTime || new Date(now.getTime() - 24 * 60 * 60 * 1000); // 24 hours ago
    const defaultEndTime = endTime || now;
    
    // Use ISO 8601 format for reliable parsing on server (avoids locale-dependent "expected pattern" errors)
    const startTimeStr = defaultStartTime.toISOString();
    const endTimeStr = defaultEndTime.toISOString();
    
    const params = new URLSearchParams();
    params.append('keys', selectedKeys.join(','));
    params.append('start_time', startTimeStr);
    params.append('end_time', endTimeStr);
    try {
        const response = await fetch(`/query_db?${params.toString()}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error('Failed to fetch data from server');
        }


        const text = await response.text();
        let result;
        try {
            result = JSON.parse(text);
        } catch {
            console.error('Response was not valid JSON:', text.slice(0, 200));
            throw new Error('Server returned invalid response (expected JSON)');
        }
        console.log('Received data points:', result.data ? result.data.length : 0);

        // Normalize row keys: DB/schema may use "Timestamp" (capital T), but plot code expects "timestamp"
        const normalizedData = (result.data || []).map(row => {
            const normalized = { ...row };
            if (normalized.Timestamp !== undefined && normalized.timestamp === undefined) {
                normalized.timestamp = normalized.Timestamp;
            }
            return normalized;
        });

        return {
            data: normalizedData,
            availableKeys: result.available_keys || [],
            missingKeys: result.missing_keys || []
        };
    } catch (err) {
        console.warn('Database connection failed, returning empty data:', err.message);
        
        // Return empty data when database is not available
        return {
            data: [],
            availableKeys: [],
            missingKeys: selectedKeys
        };
    }
};
