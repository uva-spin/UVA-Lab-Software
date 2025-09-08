const mariadb = require('mariadb/callback');
const { closePoolConnection } = require('./DB');

const cache = new Map();

function get_cache(table_name, key, start_time, end_time) {
    return cache.get(`${table_name}_${key}_${start_time}_${end_time}`);
}

function set_cache(table_name, key, start_time, end_time, data) {
    cache.set(`${table_name}_${key}_${start_time}_${end_time}`, data);
}

function clear_cache() {
    cache.clear();
}

function fetchData(pool, table_name, key, start_time, end_time) {
    if (get_cache(table_name, key, start_time, end_time)) {
        return get_cache(table_name, key, start_time, end_time);
    }
    pool.query(`SELECT ${key} FROM ${table_name} WHERE timestamp BETWEEN ${start_time} AND ${end_time}`, (err, rows) => {
        const err_times = 0;
        if (err) {
            err_times++;
            if (err_times > 3) {
                closePoolConnection(pool)
            }
            pool.rollback(err => {
                console.error(err);
            })
        }
    pool.commit(err => {
        if (err) {
            err_times++;
            if (err_times > 3) {
                closePoolConnection(pool)
            }
            pool.rollback(err => {
                console.error(err);
            })
        }
        })
        set_cache(table_name, key, start_time, end_time, rows);
        return rows;
    });
}



module.exports = { fetchData, clear_cache };