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
    'target_stick_buffle_top_temperature': 'Lakeshore_Target_Stick',
    'target_stick_buffle_bottom_temperature': 'Lakeshore_Target_Stick',
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

// Determine table name based on column names using hash map
function getTableNameFromColumns(columns) {
    if (!columns || columns.length === 0) return null;
    
    // Convert columns to array if it's a string
    const columnArray = Array.isArray(columns) ? columns : columns.split(',');
    
    // Find the table for the first column (assuming all columns in a query belong to the same table)
    const firstColumn = columnArray[0].trim();
    const tableName = COLUMN_TO_TABLE_MAP[firstColumn];
    
    if (tableName) {
        console.log(`Mapped column '${firstColumn}' to table '${tableName}'`);
        return tableName;
    }
    
    // If first column not found, check all columns
    for (const column of columnArray) {
        const trimmedColumn = column.trim();
        const mappedTable = COLUMN_TO_TABLE_MAP[trimmedColumn];
        if (mappedTable) {
            console.log(`Mapped column '${trimmedColumn}' to table '${mappedTable}'`);
            return mappedTable;
        }
    }
    
    console.warn(`No table mapping found for columns: ${columnArray.join(', ')}`);
    return null;
}

export async function fetchData(pool, table_name, keys, start_time, end_time) {
    try {
        // Determine the actual table name based on the column names
        const actualTableName = getTableNameFromColumns(keys);
        console.log(`Using table: ${actualTableName} for columns: ${keys}`);
        
        // Create cache key
        const cacheKey = `${actualTableName}_${keys}_${start_time}_${end_time}`;
        
        // Check cache first
        if (cache.has(cacheKey)) {
            console.log('Returning cached data');
            return cache.get(cacheKey);
        }

        // Build query
        let query = `SELECT ${keys}, timestamp FROM ${actualTableName}`;
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
        const result = await pool.query(query, (err, rows) => {
            if (err) {
                console.error('Error in fetchData:', err);
                throw err;
            }
            return rows;
        });

        console.log('Result:', result);
        
        // Cache the result
        cache.set(cacheKey, result);
        
        return result.rows;
        
    } catch (error) {
        console.error('Error in fetchData:', error);
        throw error;
    }
}