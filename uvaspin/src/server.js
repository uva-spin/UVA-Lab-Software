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
app.use(express.static(path.join(__dirname, '../uvaspin/dist')));

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

// Main data query endpoint
app.get('/query_db', async (req, res) => {
    try {
        const { keys, start_time, end_time } = req.query;
        
        if (!keys) {
            return res.status(400).json({ error: 'Keys parameter is required' });
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
            'table_name', // adjust here to allow for multiple tables in future
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
    res.sendFile(path.join(__dirname, '../uvaspin/dist/index.html'));
});

// Start server
app.listen(PORT, async () => {
    console.log(`Server running on port ${PORT}`);
    await initializeDatabase();
});

// Graceful shutdown
process.on('SIGINT', () => {
    if (dbConnection) {
        closePoolConnection(dbConnection.pool);
    }
    process.exit(0);
});