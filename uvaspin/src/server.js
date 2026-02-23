import express from 'express';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import { openPool, checkConnection, closePoolConnection } from './utils/DB.js';
import { fetchData, clear_cache } from './utils/Query.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = globalThis.process?.env?.PORT || 5000;
const CONTROL_API_KEY = globalThis.process?.env?.CONTROL_API_KEY || '';
const HOST = globalThis.process?.env?.HOST || '127.0.0.1';
const MAX_QUERY_KEYS = Number.parseInt(globalThis.process?.env?.MAX_QUERY_KEYS || '100', 10);
const MAX_QUERY_RANGE_DAYS = Number.parseInt(globalThis.process?.env?.MAX_QUERY_RANGE_DAYS || '365', 10);
const ALLOWED_ORIGINS = (globalThis.process?.env?.ALLOWED_ORIGINS || 'http://localhost:5173,http://127.0.0.1:5173')
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);

// Middleware
app.use(cors({
    origin(origin, callback) {
        // Allow non-browser requests (no Origin header).
        if (!origin) return callback(null, true);
        if (ALLOWED_ORIGINS.includes(origin)) return callback(null, true);
        return callback(new Error('CORS origin denied'));
    },
}));
app.use(express.json());
app.use(express.static(path.join(__dirname, '../dist')));

const queryRateLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 120,
    standardHeaders: true,
    legacyHeaders: false,
});

const controlRateLimiter = rateLimit({
    windowMs: 5 * 60 * 1000,
    max: 20,
    standardHeaders: true,
    legacyHeaders: false,
});

function secureCompare(a, b) {
    const left = Buffer.from(String(a), 'utf8');
    const right = Buffer.from(String(b), 'utf8');
    if (left.length !== right.length) return false;
    return crypto.timingSafeEqual(left, right);
}

function requireControlApiKey(req, res, next) {
    if (!CONTROL_API_KEY) {
        return res.status(503).json({ error: 'Control API key is not configured' });
    }

    const headerKey = req.get('x-api-key');
    if (!headerKey) {
        return res.status(401).json({ error: 'Missing API key' });
    }

    if (!secureCompare(headerKey, CONTROL_API_KEY)) {
        return res.status(403).json({ error: 'Invalid API key' });
    }

    return next();
}

function validateQueryRequest(req, res, next) {
    const { keys, start_time, end_time } = req.query;

    if (!keys || typeof keys !== 'string') {
        return res.status(400).json({ error: 'Keys parameter is required' });
    }

    if (keys.length > 4000) {
        return res.status(400).json({ error: 'Keys parameter is too large' });
    }

    const selectedKeys = keys
        .split(',')
        .map((value) => value.trim())
        .filter(Boolean);
    if (selectedKeys.length === 0) {
        return res.status(400).json({ error: 'At least one key is required' });
    }
    if (selectedKeys.length > MAX_QUERY_KEYS) {
        return res.status(400).json({ error: `Too many keys requested (max ${MAX_QUERY_KEYS})` });
    }
    if (!selectedKeys.every((value) => /^[A-Za-z0-9_]+$/.test(value))) {
        return res.status(400).json({ error: 'Invalid key format' });
    }

    const parsedStart = start_time ? new Date(start_time) : null;
    const parsedEnd = end_time ? new Date(end_time) : null;
    if (parsedStart && Number.isNaN(parsedStart.getTime())) {
        return res.status(400).json({ error: 'Invalid start_time format' });
    }
    if (parsedEnd && Number.isNaN(parsedEnd.getTime())) {
        return res.status(400).json({ error: 'Invalid end_time format' });
    }
    if (parsedStart && parsedEnd && parsedEnd < parsedStart) {
        return res.status(400).json({ error: 'end_time must be after start_time' });
    }
    if (parsedStart && parsedEnd) {
        const rangeMs = parsedEnd.getTime() - parsedStart.getTime();
        const maxRangeMs = MAX_QUERY_RANGE_DAYS * 24 * 60 * 60 * 1000;
        if (rangeMs > maxRangeMs) {
            return res.status(400).json({ error: `Requested time range exceeds ${MAX_QUERY_RANGE_DAYS} days` });
        }
    }

    req.validatedQuery = {
        selectedKeys,
        startTime: start_time || null,
        endTime: end_time || null,
    };
    return next();
}

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
                console.error('Health check connection failure:', err);
                res.status(500).json({ status: 'disconnected', message: 'Database connection failed' });
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
app.get('/query_db', queryRateLimiter, validateQueryRequest, async (req, res) => {
    try {
        const { selectedKeys, startTime, endTime } = req.validatedQuery;
        
        console.log('Server: Received query_db request with:', { selectedKeys, startTime, endTime });
        
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
            startTime, 
            endTime,
        );

        res.json({
            data: data || [],
            available_keys: selectedKeys,
            missing_keys: []
        });

    } catch (error) {
        console.error('Error querying database:', error);
        res.status(500).json({ 
            error: 'Database query failed'
        });
    }
});

// Clear cache endpoint
app.post('/clear_cache', controlRateLimiter, requireControlApiKey, (req, res) => {
    try {
        clear_cache();
        res.json({ message: 'Cache cleared successfully' });
    } catch {
        res.status(500).json({ error: 'Failed to clear cache' });
    }
});

// Shutdown endpoint
app.post('/shutdown', controlRateLimiter, requireControlApiKey, (req, res) => {
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