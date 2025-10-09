import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { openPool, checkConnection, closePoolConnection } from './utils/DB.js';
import { fetchData, clear_cache } from './utils/Query.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = globalThis.process?.env?.PORT || 5000;

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
    if (dbConnection && dbConnection.pool) {
        // Test the connection
        dbConnection.pool.getConnection((err, conn) => {
            if (err) {
                res.status(500).json({ status: 'disconnected', message: 'Database connection failed', error: err.message });
            } else {
                checkConnection(conn);
                conn.release();
                res.json({ status: 'connected', message: 'Database is connected' });
            }
        });
    } else {
        res.status(500).json({ status: 'disconnected', message: 'Database is not connected' });
    }
});

// Main data query endpoint
app.get('/query_db', async (req, res) => {
    try {
        const { keys, start_time, end_time, sampling, samplingRate } = req.query;
        
        console.log('Server: Received query_db request with:', { keys, start_time, end_time });
        
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

        // Use the enhanced fetchData function that handles multiple tables
        const data = await fetchData(
            dbConnection.pool, 
            selectedKeys.join(','), 
            start_time, 
            end_time,
            sampling,
            samplingRate
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
    } catch {
        res.status(500).json({ error: 'Failed to clear cache' });
    }
});

// Shutdown endpoint
app.post('/shutdown', (req, res) => {
    console.log('Shutdown request received');
    res.json({ message: 'Server shutting down...' });
    
    // Close database connections gracefully
    if (dbConnection) {
        closePoolConnection(dbConnection.pool);
    }
    
    // Give the response time to be sent before shutting down
    setTimeout(() => {
        console.log('Server shutdown complete');
        process.exit(0);
    }, 1000);
});

// Serve React app for all other routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../dist/index.html'));
});

// Start server
const HOST = globalThis.process?.env?.HOST || '0.0.0.0';
app.listen(PORT, HOST, async () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Server also accessible on http://${HOST}:${PORT}`);
    await initializeDatabase();
});

// Graceful shutdown
globalThis.process?.on('SIGINT', () => {
    if (dbConnection) {
        closePoolConnection(dbConnection.pool);
    }
    globalThis.process?.exit(0);
});