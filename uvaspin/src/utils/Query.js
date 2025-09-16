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

// Determine table name based on column names
function getTableNameFromColumns(columns) {
    if (!columns || columns.length === 0) return null;
    
    // Convert columns to string if it's an array
    const columnString = Array.isArray(columns) ? columns.join(',') : columns;
    
    // QT table columns (from DataSelectionSidebar.jsx)

    const qt_pressures = ['pt501_ai', 'pt502_ai', 'pt503_ai', 'pt504_ai']
    const qt_flows = ['fc501_ai', 'fc501_out', 'fc502_ai', 'fc502_out']
    const qt_temperatures = ['ait501_ai', 'ti501_ai', 'ti502_ai', 'ti503_ai', 'ti504_ai', 'ti505_ai', 'ti523_ai']
    const qt_level_indicators = ['lit501_ai']

    const qtColumns = [
        qt_pressures, qt_flows, qt_temperatures, qt_level_indicators
    ];
    
    // Check if any QT columns are present
    const hasQtColumns = qtColumns.some(col => columnString.includes(col));
    if (hasQtColumns) {
        if (qt_pressures.some(col => columnString.includes(col))) {
            return 'QT.Pressures';
        }
        if (qt_flows.some(col => columnString.includes(col))) {
            return 'QT.Flows';
        }
        if (qt_temperatures.some(col => columnString.includes(col))) {
            return 'QT.Temperatures';
        }
        if (qt_level_indicators.some(col => columnString.includes(col))) {
            return 'QT.Level Indicators';
        }
        else {
            return null;
        }
    }
    
    // Pressure table columns
    const pressureColumns = [
        'root_exhaust_pressure', 'buffer_pressure', 'magnet_pressure', 
        'purifier_inlet_pressure', 'fridge_vapor_pressure', 'maxigauge_pressure', 'ivc_pressure'
    ];
    const hasPressureColumns = pressureColumns.some(col => columnString.includes(col));
    if (hasPressureColumns) {
        return 'Pressures';
    }
    
    // Temperature table columns
    const temperatureColumns = [
        'thermocouple', 'magnet_bottom_temperature', 'magnet_top_temperature',
        'fridge_target_top_up_temperature', 'fridge_target_top_up_center_temperature',
        'fridge_target_top_down_temperature', 'fridge_target_bottom_up_temperature',
        'fridge_target_bottom_up_center_temperature', 'fridge_target_bottom_down_temperature',
        'fridge_target_top_cernox_temperature', 'fridge_target_bottom_cernox_temperature',
        'magnet_channel_1', 'magnet_channel_2', 'magnet_channel_3', 'magnet_channel_4',
        'magnet_channel_5', 'magnet_channel_6', 'magnet_channel_7', 'magnet_channel_8'
    ];
    const hasTemperatureColumns = temperatureColumns.some(col => columnString.includes(col));
    if (hasTemperatureColumns) {
        return 'Temperatures';
    }
    
    // Flow table columns
    const flowColumns = [
        'separator_flow', 'magnet_flow', 'main_flow', 'microwave_flow', 'heat_exchanger_flow'
    ];
    const hasFlowColumns = flowColumns.some(col => columnString.includes(col));
    if (hasFlowColumns) {
        return 'Flows';
    }
    
    // NMR table columns
    const nmrColumns = [
        'run_number', 'measurement_type', 'peak_amp', 'peak_center', 'beam_on', 'rf_level',
        'if_atten', 'he_temperature', 'he_pressure', 'nmr_channel', 'temperature',
        'calibration_constant', 'polarization', 'polarization_std', 'snr', 'step_width',
        'center_freq', 'freq_span', 'area', 'phase_voltage', 'tune_voltage'
    ];
    const hasNmrColumns = nmrColumns.some(col => columnString.includes(col));
    if (hasNmrColumns) {
        return 'NMR';
    }
    
    // Default fallback
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