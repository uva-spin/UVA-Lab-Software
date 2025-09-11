const mariadb = require('mariadb/callback');
const fs = require('fs');
const path = require('path');

let config = {};

// Read config file
const configPath = path.join(__dirname, '../../config.json');
try {
    const configData = fs.readFileSync(configPath, 'utf8');
    config = JSON.parse(configData);
} catch (err) {
    console.error('Error reading config file:', err);
    // Use default config or environment variables
    config = {
        host: process.env.DB_HOST || 'localhost',
        user: process.env.DB_USER || 'root',
        password: process.env.DB_PASSWORD || '',
        database: process.env.DB_NAME || 'uvaspin',
        connectionLimit: 5
    };
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

module.exports = { openPool, checkConnection, closePoolConnection };