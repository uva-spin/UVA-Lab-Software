import mariadb from 'mariadb/callback.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let config = {};

// Read config file
const configPath = path.join(__dirname, '../../config.json');
try {
    const configData = fs.readFileSync(configPath, 'utf8');
    config = JSON.parse(configData);
} catch (err) {
    console.error('Error reading config file\n \
        Cannot Establish Connection to Database \
        \n Error:', err);
}

function createPool() {
    try {
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