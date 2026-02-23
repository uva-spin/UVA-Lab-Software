import mariadb from 'mariadb/callback.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();
let config = null;

function loadLegacyFileConfig() {
    const configPath = path.join(__dirname, '../../config.json');
    const configData = fs.readFileSync(configPath, 'utf8');
    const parsed = JSON.parse(configData);
    const required = ['host', 'port', 'user', 'password', 'database'];
    const missing = required.filter((k) => !(k in parsed));
    if (missing.length > 0) {
        throw new Error(`config.json missing required keys: ${missing.join(', ')}`);
    }
    return parsed;
}

function loadEnvConfig() {
    const envConfig = {
        host: process.env.DB_HOST,
        port: process.env.DB_PORT ? Number.parseInt(process.env.DB_PORT, 10) : undefined,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME,
    };

    const required = ['host', 'port', 'user', 'password', 'database'];
    const missing = required.filter((k) => envConfig[k] === undefined || envConfig[k] === null || envConfig[k] === '');
    if (missing.length > 0) {
        throw new Error(`Missing required DB environment variables: ${missing.join(', ')}`);
    }
    if (!Number.isInteger(envConfig.port) || envConfig.port <= 0) {
        throw new Error('DB_PORT must be a positive integer');
    }
    return envConfig;
}

try {
    if (process.env.USE_LEGACY_DB_CONFIG === 'true') {
        config = loadLegacyFileConfig();
        console.warn('Using legacy DB config file via USE_LEGACY_DB_CONFIG=true');
    } else {
        config = loadEnvConfig();
    }
} catch (err) {
    console.error('Database configuration error:', err.message);
}

function createPool() {
    try {
        if (!config) {
            throw new Error('Database configuration not initialized');
        }
        return mariadb.createPool(config);
    } catch (error) {
        console.error('Failed to create database pool:', error);
        return null;
    }
}

function closePoolConnection(pool) {
    if (pool) {
        pool.end();
        console.log('Closed database connection');
    }
}

function openPool() {
    const pool = createPool();
    if (!pool) {
        throw new Error('Failed to create database pool');
    }
    
    pool.getConnection((err, conn) => {
        if (err) {
            console.error('Failed to get database connection:', err);
            throw err;
        }
        console.log('Connected to database');
        return { conn, pool };
    });
    
    return { pool };
}

function checkConnection(conn) {
    if (conn && conn.ping) {
        conn.ping(err => {
            if (err) {
                console.log('Connection to database lost. Error: ', err);
            } else {
                console.log('Connection to database is still alive');
            }
        });
    }
}

export { openPool, checkConnection, closePoolConnection };