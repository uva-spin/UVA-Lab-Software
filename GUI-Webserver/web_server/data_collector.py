#!/usr/bin/env python3
import mariadb
import time
import threading
import os
import signal
import sys
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, render_template
import logging
import pytz
import json

DATABASE_FILE = "/var/www/spin/config.json"

# Load database configuration
with open(DATABASE_FILE, 'r') as f:
    config = json.load(f)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure timezone - Use proper Eastern Time that handles EST/EDT automatically
EST = pytz.timezone('America/New_York')

# Global variable to track shutdown state
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    shutdown_requested = True
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_current_est_time():
    """Get the current time in EST/EDT (Eastern Time)"""
    return datetime.now(EST).strftime('%Y-%m-%d %H:%M:%S')

def convert_frontend_timestamp_to_db_format(timestamp_str):
    """
    Convert frontend timestamp format (MM/DD/YYYY HH:mm:ss) to database format (YYYY-MM-DD HH:mm:ss)
    
    Args:
        timestamp_str (str): Timestamp in format "MM/DD/YYYY HH:mm:ss" (e.g., "01/15/2024 14:30:25")
    
    Returns:
        str: Timestamp in format "YYYY-MM-DD HH:mm:ss" (e.g., "2024-01-15 14:30:25")
    """
    try:
        dt = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        logger.warning(f"Could not parse timestamp '{timestamp_str}': {e}")
        return timestamp_str

def convert_db_timestamp_to_js_timestamp(db_timestamp):
    """
    Convert database timestamp to JavaScript timestamp (milliseconds since epoch)
    Assumes database timestamps are in Eastern Time (EST/EDT)
    
    Args:
        db_timestamp: Database timestamp (datetime object or string)
    
    Returns:
        int: JavaScript timestamp (milliseconds since epoch)
    """
    try:
        if isinstance(db_timestamp, str):
            naive_dt = datetime.strptime(db_timestamp, '%Y-%m-%d %H:%M:%S')
            # Localize to Eastern Time
            est_dt = EST.localize(naive_dt)
        elif hasattr(db_timestamp, 'replace'):  
            if db_timestamp.tzinfo is None:
                est_dt = EST.localize(db_timestamp)
            else:
                est_dt = db_timestamp.astimezone(EST)
        else:
            logger.warning(f"Unknown timestamp format: {type(db_timestamp)}")
            return None
        
        # Convert to JavaScript timestamp (milliseconds since epoch)
        return int(est_dt.timestamp() * 1000)
    except Exception as e:
        logger.error(f"Error converting timestamp {db_timestamp}: {e}")
        return None

class DataCollector:
    def __init__(self):
        print(f"Database IP: {config['host']}")
        print(f"Database port: {config['port']}")
        print(f"Database user: {config['user']}")
        print(f"Database password: {config['password']}")
        print(f"Database name: {config['database']}")
        self.setup_database()
        self.db_pool = mariadb.ConnectionPool(
                    pool_name="website_pool",
                    pool_size=20,
                    **config)

    def get_database_connection(self):
        """Get a database connection from the connection pool"""
        if self.db_pool is None:
            raise RuntimeError("Database connection pool not initialized")
        
        try:
            conn = self.db_pool.get_connection()
            return conn
        except mariadb.PoolError as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise

    def close_database_connection(self):
        if self.db_pool is not None:
            self.db_pool.close()
            self.db_pool = None
            logger.info("Database connection pool closed")
        
    def setup_database(self):
        """Initialize the database with the schema-defined tables"""
        
        conn = mariadb.connect(**config)
        cursor = conn.cursor()
        
        try:
            schema_path = "../database_utils/schema.sql"
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                
            # Split the SQL into individual statements and execute them
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            for statement in statements:
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
            
            conn.commit()
            logger.info("Database setup completed using schema.sql")
        except mariadb.Error as e:
            if "already exists" in str(e):
                logger.info("Tables already exist, skipping creation")
            else:
                logger.error(f"Database setup error: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error during database setup: {e}")
            raise
        finally:
            conn.close()

    def get_available_columns_by_table(self):
        """Get available columns organized by table name"""
        try:
            conn = mariadb.connect(**config)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            columns_by_table = {}
            
            for table_name in tables:
                # Get column names for this table
                cursor.execute(f"DESCRIBE {table_name}")
                columns = [col[0] for col in cursor.fetchall()]
                columns_by_table[table_name] = columns
            
            conn.close()
            return columns_by_table
            
        except Exception as e:
            logger.error(f"Error getting columns by table: {e}")
            return {}

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
collector = DataCollector()

@app.route('/', methods=['GET'])
def root():
    """Serve the main plotting interface"""
    return render_template('index.html')


@app.route('/shutdown', methods=['POST'])
def shutdown_server():
    """Endpoint to gracefully shutdown the server"""
    global shutdown_requested
    logger.info("Shutdown requested via HTTP endpoint")
    shutdown_requested = True
    
    def delayed_shutdown():
        time.sleep(1)  
        os._exit(0)
    
    threading.Thread(target=delayed_shutdown, daemon=True).start()
    return jsonify({"status": "shutdown_initiated", "message": "Server shutting down gracefully"}), 200

@app.route('/query_db', methods=['GET'])
def query_db():
    """Get recent data from the database based on timestamp"""
    try:
        keys = request.args.get('keys', '').split(',')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        
        keys = [key.strip() for key in keys if key.strip()]
        
        if not keys:
            return jsonify({"error": "No keys provided"}), 400
            
        if not start_time or not end_time:
            return jsonify({"error": "Start time and end time must be provided"}), 400

        db_start_time = convert_frontend_timestamp_to_db_format(start_time)
        db_end_time = convert_frontend_timestamp_to_db_format(end_time)
        
        logger.info(f"Original timestamps - start: {start_time}, end: {end_time}")
        logger.info(f"Converted timestamps - start: {db_start_time}, end: {db_end_time}")
        logger.info(f"Fetching data for keys: {keys}")
        logger.info(f"Time range (EST): {db_start_time} to {db_end_time}")
        
        conn = collector.get_database_connection()
        cursor = conn.cursor()
        
        all_data = {}
        available_keys = []
        missing_keys = []
        
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        
        # Check each table for the requested columns
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = [col[0] for col in cursor.fetchall()]
            
            # Find which keys are in this table
            table_keys = [key for key in keys if key in columns]
            if not table_keys:
                continue
                
            logger.info(f"Found keys {table_keys} in table {table}")
            
            columns_str = ', '.join(['Timestamp'] + table_keys)
            query = f"""
                SELECT {columns_str}
                FROM {table}
                WHERE Timestamp BETWEEN %s AND %s
                ORDER BY Timestamp ASC
            """
            logger.info(f"DB start time: {db_start_time}")
            logger.info(f"DB end time: {db_end_time}")
            logger.info(f"Executing query: {query} with params: {db_start_time}, {db_end_time}")
            
            # Execute query with converted timestamps
            cursor.execute(query, (db_start_time, db_end_time))
            rows = cursor.fetchall()
            
            logger.info(f"Found {len(rows)} rows in table {table}")
            
            if rows:
                for row in rows:
                    timestamp = row[0]
                    
                    js_timestamp = convert_db_timestamp_to_js_timestamp(timestamp)
                    if js_timestamp is None:
                        logger.warning(f"Could not convert timestamp: {timestamp}")
                        continue
                    
                    if js_timestamp not in all_data:
                        all_data[js_timestamp] = {'Timestamp': js_timestamp}
                    
                    for i, key in enumerate(table_keys, 1):
                        try:
                            all_data[js_timestamp][key] = float(row[i])
                        except (ValueError, TypeError):
                            logger.warning(f"Could not convert value for {key}: {row[i]}")
                            all_data[js_timestamp][key] = None
                
                available_keys.extend(table_keys)
            else:
                missing_keys.extend(table_keys)
        
        data = list(all_data.values())
        data.sort(key=lambda x: x['Timestamp'])
        
        if available_keys:
            logger.info(f"Found data for keys: {available_keys}")
            logger.info(f"Sample data point: {data[0] if data else 'No data'}")
        if missing_keys:
            logger.warning(f"No data found for keys: {missing_keys}")
        
        return jsonify({
            "data": data,
            "available_keys": available_keys,
            "missing_keys": missing_keys,
            "timezone": "EST",
            "time_range": {
                "start": start_time,
                "end": end_time,
                "db_start": db_start_time,
                "db_end": db_end_time
            }
        }), 200
        
    except mariadb.Error as e:
        logger.error(f"Error getting recent data: {e}")
        logger.exception("Full traceback:")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        collector.close_database_connection()

@app.route('/get_available_columns', methods=['GET'])
def get_available_columns():
    """Get list of available columns from all tables"""
    try:
        
        conn = collector.get_database_connection()
        cursor = conn.cursor()
        columns_by_table = collector.get_available_columns_by_table()
        
        all_columns = []
        for table_columns in columns_by_table.values():
            all_columns.extend(table_columns)
        
        unique_columns = []
        for col in all_columns:
            if col not in unique_columns:
                unique_columns.append(col)
        
        logger.info(f"Available columns: {unique_columns}")
        logger.info(f"Columns by table: {columns_by_table}")
        
        return jsonify({
            "columns": unique_columns,  
            "tables": columns_by_table,
            "total_columns": len(unique_columns),
            "table_count": len(columns_by_table)
        }), 200
        
    except mariadb.Error as e:
        logger.error(f"Error getting available columns: {e}")
        return jsonify({"error": str(e), "columns": []}), 500
    finally:
        cursor.close()
        conn.close()
        collector.close_database_connection()

        
@app.route('/db_status', methods=['GET'])
def get_db_status():
    """Check database status and available tables"""
    try:
        conn = collector.get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        table_info = {}
        total_records = 0
        
        for table_name in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            table_schema = cursor.fetchall()
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = cursor.fetchone()[0]
            total_records += record_count
            
            table_info[table_name] = {
                "columns": [col[0] for col in table_schema],
                "record_count": record_count
            }
            
        return jsonify({
            "status": "ok",
            "tables": table_info,
            "total_records": total_records,
            "has_data": total_records > 0
        }), 200
        
    except mariadb.Error as e:
        logger.error(f"Error checking database status: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        collector.close_database_connection()
@app.route('/test_db', methods=['GET'])
def test_db():
    """Test database connection and data availability"""
    try:
        conn = mariadb.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        total_records = 0
        data_sources = []
        
        for table_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            
            if count > 0:
                data_sources.append(table_name)
                
            cursor.execute(f"SELECT Timestamp FROM {table_name} ORDER BY Timestamp DESC LIMIT 1")
            latest = cursor.fetchone()
            if latest:
                logger.info(f"Latest record in {table_name}: {latest[0]}")
                
        return jsonify({
            "status": "ok",
            "total_records": total_records,
            "data_sources": data_sources,
            "tables": tables
        }), 200
        
    except mariadb.Error as e:
        logger.error(f"Error testing database: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        collector.close_database_connection()

if __name__ == '__main__':
    # Start Flask app
    logger.info("Starting Data Collector Server...")
    logger.info("Press Ctrl+C or send POST to /shutdown to stop the server")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
    finally:
        logger.info("Data Collector Server stopped.") 
        logger.error(f"Error starting server: {e}")
        sys.exit(1) 