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

from config import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    """Get the current time in EST"""
    return datetime.now(timezone(timedelta(hours=-5))).strftime('%Y-%m-%d %H:%M:%S')

def convert_frontend_timestamp_to_db_format(timestamp_str):
    """
    Convert frontend timestamp format (MM/DD/YYYY HH:mm:ss) to database format (YYYY-MM-DD HH:mm:ss)
    
    Args:
        timestamp_str (str): Timestamp in format "MM/DD/YYYY HH:mm:ss" (e.g., "01/15/2024 14:30:25")
    
    Returns:
        str: Timestamp in format "YYYY-MM-DD HH:mm:ss" (e.g., "2024-01-15 14:30:25")
    """
    try:
        # Parse the frontend format: "MM/DD/YYYY HH:mm:ss" (without comma)
        dt = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
        # Convert to database format: "YYYY-MM-DD HH:mm:ss"
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        logger.warning(f"Could not parse timestamp '{timestamp_str}': {e}")
        # If parsing fails, return the original string and let the database handle it
        return timestamp_str

class DataCollector:
    def __init__(self):
        print(f"Database IP: {DATABASE_HOST}")
        print(f"Database port: {DATABASE_PORT}")
        print(f"Database user: {DATABASE_USER}")
        print(f"Database password: {DATABASE_PASSWORD}")
        print(f"Database name: {DATABASE_NAME}")
        self.setup_database()
        
    def setup_database(self):
        """Initialize the database with the schema-defined tables"""
        
        conn = mariadb.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME,
            autocommit=True
        )
        cursor = conn.cursor()
        
        try:
            # Use the schema.sql file instead of hardcoded table creation
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

    def get_data_by_time_range(self, start_time=None, end_time=None, table_name=None):
        """Get data from specific table(s) within a time range"""
        
        try:
            
            conn = mariadb.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                database=DATABASE_NAME,
                autocommit=True
            )
            cursor = conn.cursor()
            if table_name:
                # Query specific table
                tables = [table_name]
            else:
                # Get all tables
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
            
            all_data = {}
            
            for table in tables:
                # Build time range query
                base_query = f"SELECT * FROM {table}"
                conditions = []
                params = []
                
                if start_time:
                    conditions.append("Timestamp >= %s")
                    params.append(start_time)
                    
                if end_time:
                    conditions.append("Timestamp <= %s")
                    params.append(end_time)
                
                if conditions:
                    query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY Timestamp DESC"
                else:
                    query = f"{base_query} ORDER BY Timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"DESCRIBE {table}")
                columns = [col[0] for col in cursor.fetchall()]
                
                # Convert to list of dictionaries
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column] = row[i]
                    table_data.append(row_dict)
                
                all_data[table] = table_data
            
            conn.close()
            return all_data
            
        except Exception as e:
            logger.error(f"Error getting data by time range: {e}")
            return {}

    def get_latest_data_from_all_tables(self):
        """Get the latest data from all tables and combine them"""
        
        try:
            conn = mariadb.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                database=DATABASE_NAME,
                autocommit=True
            )
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            combined_data = {}
            
            for table_name in tables:
                try:
                    # Get the latest record from each table
                    cursor.execute(f"SELECT * FROM {table_name} ORDER BY Timestamp DESC LIMIT 1")
                    latest_record = cursor.fetchone()
                    
                    if latest_record:
                        # Get column names for this table
                        cursor.execute(f"DESCRIBE {table_name}")
                        columns = [col[0] for col in cursor.fetchall()]
                        
                        # Create a dictionary for this record
                        record_dict = {}
                        for i, column in enumerate(columns):
                            record_dict[column] = latest_record[i]
                        
                        # Add table prefix to avoid column name conflicts
                        for key, value in record_dict.items():
                            if key.lower() not in ['id', 'timestamp', 'created']:
                                prefixed_key = f"{table_name}_{key}"
                                combined_data[prefixed_key] = value
                            else:
                                # Keep timestamp and id fields without prefix
                                combined_data[key] = value
                                
                except Exception as e:
                    logger.warning(f"Error getting latest data from {table_name}: {e}")
                    continue
            
            conn.close()
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting latest data from all tables: {e}")
            return {}

    def insert_data(self, table_name, data):
        """Insert data into the specified table"""
        try:
            conn = mariadb.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                database=DATABASE_NAME,
                autocommit=True
            )
            cursor = conn.cursor()
            
            # Get the column names for the table (excluding id which is auto-increment)
            cursor.execute(f"DESCRIBE {table_name}")
            table_info = cursor.fetchall()
            columns = [col[0] for col in table_info if col[0].lower() != 'id']
            
            # Create placeholders for the SQL query
            placeholders = ', '.join(['%s' for _ in columns])
            column_names = ', '.join(columns)
            
            # Prepare the data tuple - ensure data order matches column order
            data_tuple = []
            for column in columns:
                if column.lower() == 'timestamp' or column.lower() == 'created':
                    # Use current timestamp if not provided
                    data_tuple.append(data.get(column, get_current_est_time()))
                else:
                    data_tuple.append(data.get(column))
            
            # Insert the data
            query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            cursor.execute(query, data_tuple)
            conn.commit()
            
            logger.info(f"Successfully inserted data into {table_name}")
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            return False

    def get_table_data(self, table_name, limit=100):
        """Get recent data from a specific table"""
        try:
            conn = mariadb.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                database=DATABASE_NAME,
                autocommit=True
            )
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY Timestamp DESC LIMIT %s", (limit,))
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [col[0] for col in cursor.fetchall()]
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    row_dict[column] = row[i]
                data.append(row_dict)
            
            conn.close()
            return data
            
        except Exception as e:
            logger.error(f"Error getting data from {table_name}: {e}")
            return []

    def get_available_columns_by_table(self):
        """Get available columns organized by table name"""
        try:
            conn = mariadb.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                database=DATABASE_NAME,
                autocommit=True
            )
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

# Create Flask app for receiving QT data
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
    
    # Start shutdown in a separate thread to allow response
    def delayed_shutdown():
        time.sleep(1)  # Give time for response to be sent
        os._exit(0)
    
    threading.Thread(target=delayed_shutdown, daemon=True).start()
    return jsonify({"status": "shutdown_initiated", "message": "Server shutting down gracefully"}), 200

@app.route('/query_db', methods=['GET'])
def query_db():
    """Get recent data from the database based on timestamp"""
    try:
        # Get parameters from request
        keys = request.args.get('keys', '').split(',')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        
        # Filter out empty keys
        keys = [key.strip() for key in keys if key.strip()]
        
        if not keys:
            return jsonify({"error": "No keys provided"}), 400
            
        if not start_time or not end_time:
            return jsonify({"error": "Start time and end time must be provided"}), 400

        # Convert frontend timestamp format to database format
        db_start_time = convert_frontend_timestamp_to_db_format(start_time)
        db_end_time = convert_frontend_timestamp_to_db_format(end_time)
        
        logger.info(f"Original timestamps - start: {start_time}, end: {end_time}")
        logger.info(f"Converted timestamps - start: {db_start_time}, end: {db_end_time}")
        logger.info(f"Fetching data for keys: {keys}")
        logger.info(f"Time range (EST): {db_start_time} to {db_end_time}")
        
        conn = mariadb.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME,
            autocommit=True
        )
        cursor = conn.cursor()
        
        all_data = {}
        available_keys = []
        missing_keys = []
        
        # Get all tables - MariaDB equivalent
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
            
            # Build the query for this table - MariaDB uses %s placeholders and no quotes around column names
            columns_str = ', '.join(['Timestamp'] + table_keys)
            query = f"""
                SELECT {columns_str}
                FROM {table}
                WHERE Timestamp >= %s AND Timestamp <= %s
                ORDER BY Timestamp ASC
            """
            logger.info(f"DB start time: {db_start_time}")
            logger.info(f"DB end time: {db_end_time}")
            logger.info(f"Executing query: {query} with params: {db_start_time}, {db_end_time}")
            
            # Execute query with converted timestamps
            cursor.execute(query, (db_start_time, db_end_time))
            rows = cursor.fetchall()
            
            logger.info(f"Found {len(rows)} rows in table {table}")
            
            # Process data for this table
            if rows:
                for row in rows:
                    timestamp = row[0]
                    
                    if timestamp not in all_data:
                        all_data[timestamp] = {'Timestamp': timestamp}
                    
                    # Add data for each key
                    for i, key in enumerate(table_keys, 1):
                        try:
                            # Don't round the values - let the frontend handle formatting
                            all_data[timestamp][key] = float(row[i])
                        except (ValueError, TypeError):
                            logger.warning(f"Could not convert value for {key}: {row[i]}")
                            all_data[timestamp][key] = None
                
                available_keys.extend(table_keys)
            else:
                missing_keys.extend(table_keys)
        

        
        # Convert dictionary to list and sort by timestamp
        data = list(all_data.values())
        data.sort(key=lambda x: x['Timestamp'])
        
        # Log results
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

@app.route('/get_available_columns', methods=['GET'])
def get_available_columns():
    """Get list of available columns from all tables"""
    try:
        
        conn = mariadb.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME,
            autocommit=True
        )
        cursor = conn.cursor()
        columns_by_table = collector.get_available_columns_by_table()
        
        # Flatten all columns from all tables into a single list
        all_columns = []
        for table_columns in columns_by_table.values():
            all_columns.extend(table_columns)
        
        # Remove duplicates while preserving order
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

@app.route('/db_status', methods=['GET'])
def get_db_status():
    """Check database status and available tables"""
    try:
        conn = mariadb.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Get all tables - MariaDB equivalent  
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        table_info = {}
        total_records = 0
        
        for table_name in tables:
            # Get table schema - MariaDB equivalent
            cursor.execute(f"DESCRIBE {table_name}")
            table_schema = cursor.fetchall()
            
            # Get total record count
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

@app.route('/test_db', methods=['GET'])
def test_db():
    """Test database connection and data availability"""
    try:
        conn = mariadb.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Get all tables - MariaDB equivalent  
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        total_records = 0
        data_sources = []
        
        for table_name in tables:
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            
            if count > 0:
                data_sources.append(table_name)
                
            # Get latest record timestamp
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