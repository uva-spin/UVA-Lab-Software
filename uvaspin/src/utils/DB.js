const mariadb = require('mariadb/callback');
const fs = require('fs');

config_file = '../../../config.json'

fs.readFile(config_file, 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading config file:', err);
        return;
    }
    config = JSON.parse(data);
});

function createPool() {
    return mariadb.createPool(config);
}

function closePoolConnection(pool) {
    /* close connnection in case of error to preserve resources */
    pool.end()
    console.log('Closed database connection')
}

function openPool() {
    const pool = createPool();
    const conn = pool.getConnection();
    console.log('Connected to database');
    return { conn, pool };
}

function checkConnection(conn) {
    conn.ping(err => {
        if (err) {
            console.log('Connection to database lost. Error: ', err);
        } else {
            console.log('Connection to database is still alive')
        }
    })
}




module.exports = { openPool, checkConnection, closePoolConnection};