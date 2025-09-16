import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { openPool, checkConnection, closePoolConnection } from './utils/DB.js';
import { fetchData, clear_cache } from './utils/Query.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../dist')));

// Database connection
let dbConnection = null;

// Initialize database connection
async function initializeDatabase() {
    try {
        dbConnection = openPool();
        console.log('Database connection initialized');
    } catch (error) {
        console.error('Failed to initialize database:', error);
    }
}

// Health check endpoint
app.get('/health_check', (req, res) => {
    if (dbConnection && dbConnection.conn) {
        checkConnection(dbConnection.conn);
        res.json({ status: 'connected', message: 'Database is connected' });
    } else {
        res.status(500).json({ status: 'disconnected', message: 'Database is not connected' });
    }
});

// Get available tables endpoint
app.get('/tables', async (req, res) => {
    try {
        if (!dbConnection || !dbConnection.pool) {
            return res.status(500).json({ error: 'Database not connected' });
        }

        const result = await dbConnection.pool.query('SHOW TABLES');
        const tables = result.map(row => Object.values(row)[0]);
        
        res.json({ tables });
    } catch (error) {
        console.error('Error fetching tables:', error);
        res.status(500).json({ 
            error: 'Failed to fetch tables',
            message: error.message 
        });
    }
});

// Main data query endpoint
app.get('/query_db', async (req, res) => {
    try {
        const { keys, start_time, end_time, table } = req.query;
        
        if (!keys) {
            return res.status(400).json({ error: 'Keys parameter is required' });
        }

        if (!table) {
            return res.status(400).json({ error: 'Table parameter is required' });
        }

        const selectedKeys = keys.split(',');
        
        if (!dbConnection || !dbConnection.pool) {
            console.warn('Database not connected, returning empty data');
            return res.json({
                data: [],
                available_keys: [],
                missing_keys: selectedKeys
            });
        }

        const data = await fetchData(
            dbConnection.pool, 
            table, // Use the table name from query parameter
            selectedKeys.join(','), 
            start_time, 
            end_time
        );

        res.json({
            data: data || [],
            available_keys: selectedKeys,
            missing_keys: []
        });

    } catch (error) {
        console.error('Error querying database:', error);
        res.status(500).json({ 
            error: 'Database query failed',
            message: error.message 
        });
    }
});

// Clear cache endpoint
app.post('/clear_cache', (req, res) => {
    try {
        clear_cache();
        res.json({ message: 'Cache cleared successfully' });
    } catch (error) {
        res.status(500).json({ error: 'Failed to clear cache' });
    }
});

// Serve React app for all other routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../dist/index.html'));
});

// Start server
app.listen(PORT, '0.0.0.0', async () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Server also accessible on http://0.0.0.0:${PORT}`);
    console.log(`Network accessible on http://128.143.231.224:${PORT}`);
    await initializeDatabase();
});

// Graceful shutdown
process.on('SIGINT', () => {
    if (dbConnection) {
        closePoolConnection(dbConnection.pool);
    }
    process.exit(0);
});