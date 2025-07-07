#!/usr/bin/env python3
import sqlite3
import json
import time
import threading
import os
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests
from flask import Flask, request, jsonify, render_template
import logging

from config import DATABASE_PATH

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

class DataCollector:
    def __init__(self, db_path=f"{DATABASE_PATH}"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Initialize the database with the schema-defined tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Use the schema.sql file instead of hardcoded table creation
            schema_path = "../database_utils/schema.sql"
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                cursor.executescript(schema_sql)
            
            conn.commit()
            logger.info("Database setup completed using schema.sql")
        except sqlite3.OperationalError as e:
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

    def get_latest_data_from_all_tables(self):
        """Get the latest data from all tables and combine them"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            combined_data = {}
            
            # Get latest HMI data
            cursor.execute("""
                SELECT fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                       pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream,
                       purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                       ti504_ai, ti505_ai, ti523_ai, created
                FROM hmi 
                ORDER BY created DESC 
                LIMIT 1
            """)
            hmi_data = cursor.fetchone()
            if hmi_data:
                combined_data.update({
                    'fc501_ai': hmi_data[0], 'fc501_out': hmi_data[1],
                    'fc502_ai': hmi_data[2], 'fc502_out': hmi_data[3],
                    'lit501_ai': hmi_data[4], 'pt501_ai': hmi_data[5],
                    'pt502_ai': hmi_data[6], 'pt503_ai': hmi_data[7],
                    'pt504_ai': hmi_data[8], 'purity_downstream': hmi_data[9],
                    'purity_upstream': hmi_data[10], 'ait501_ai': hmi_data[11],
                    'ti501_ai': hmi_data[12], 'ti502_ai': hmi_data[13],
                    'ti503_ai': hmi_data[14], 'ti504_ai': hmi_data[15],
                    'ti505_ai': hmi_data[16], 'ti523_ai': hmi_data[17],
                    'hmi_timestamp': hmi_data[18]
                })
            
            # Get latest LabJack data
            cursor.execute("""
                SELECT pressure_1, created
                FROM labjack 
                ORDER BY created DESC 
                LIMIT 1
            """)
            labjack_data = cursor.fetchone()
            if labjack_data:
                combined_data.update({
                    'pressure_1': labjack_data[0],
                    'labjack_timestamp': labjack_data[1]
                })
            
            # Get latest Teledyne data
            cursor.execute("""
                SELECT flow_1, flow_2, flow_3, created
                FROM teledyne 
                ORDER BY created DESC 
                LIMIT 1
            """)
            teledyne_data = cursor.fetchone()
            if teledyne_data:
                combined_data.update({
                    'flow_1': teledyne_data[0],
                    'flow_2': teledyne_data[1],
                    'flow_3': teledyne_data[2],
                    'teledyne_timestamp': teledyne_data[3]
                })
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting latest data from all tables: {e}")
            return {}
        finally:
            conn.close()

    def get_data_by_time_range(self, start_time=None, end_time=None, table_name=None):
        """Get data from specific table(s) within a time range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if table_name:
                # Query specific table
                tables = [table_name]
            else:
                # Query all tables, excluding system tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                all_tables = [row[0] for row in cursor.fetchall()]
                
                # Filter out system tables
                system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
                tables = [table for table in all_tables if table not in system_tables]
            
            all_data = {}
            
            for table in tables:
                # First, get the table schema to understand the structure
                cursor.execute(f"PRAGMA table_info({table})")
                table_info = cursor.fetchall()
                columns = [col[1] for col in table_info]
                
                # Check if 'created' column exists
                has_created_column = 'created' in columns
                
                where_clause = ""
                params = []
                order_clause = ""
                
                if has_created_column:
                    if start_time and end_time:
                        where_clause = "WHERE created BETWEEN ? AND ?"
                        params = [start_time, end_time]
                    order_clause = "ORDER BY created ASC"
                else:
                    # If no created column, just get all data
                    order_clause = "ORDER BY id ASC"
                
                query = f"SELECT * FROM {table} {where_clause} {order_clause}"
                logger.debug(f"Executing query: {query} with params: {params}")
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column] = row[i]
                    table_data.append(row_dict)
                
                all_data[table] = table_data
                logger.debug(f"Retrieved {len(table_data)} records from {table} table")
            
            return all_data
            
        except Exception as e:
            logger.error(f"Error getting data by time range: {e}")
            return {}
        finally:
            conn.close()

    def insert_hmi_data(self, data):
        """Insert HMI data into the hmi table as per schema"""
        if len(data) != 18:
            logger.error(f"Expected 18 HMI values, got {len(data)}")
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO hmi (
                    fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                    pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream,
                    purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                    ti504_ai, ti505_ai, ti523_ai
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            
            conn.commit()
            logger.info(f"Inserted HMI data: {data[:3]}...")
            return True
        except Exception as e:
            logger.error(f"Error inserting HMI data: {e}")
            return False
        finally:
            conn.close()

    def insert_labjack_data(self, pressure_data):
        """Insert LabJack data into the labjack table as per schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO labjack (pressure_1) VALUES (?)
            ''', (pressure_data,))
            
            conn.commit()
            logger.info(f"Inserted LabJack data: {pressure_data}")
            return True
        except Exception as e:
            logger.error(f"Error inserting LabJack data: {e}")
            return False
        finally:
            conn.close()

    def insert_teledyne_data(self, flow_data):
        """Insert Teledyne data into the teledyne table as per schema"""
        if len(flow_data) != 3:
            logger.error(f"Expected 3 flow values, got {len(flow_data)}")
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO teledyne (flow_1, flow_2, flow_3) VALUES (?, ?, ?)
            ''', flow_data)
            
            conn.commit()
            logger.info(f"Inserted Teledyne data: {flow_data}")
            return True
        except Exception as e:
            logger.error(f"Error inserting Teledyne data: {e}")
            return False
        finally:
            conn.close()

    def insert_combined_data(self, combined_data):
        """Insert combined data into appropriate tables based on data type"""
        if not isinstance(combined_data, dict):
            logger.error(f"Expected dict data, got {type(combined_data)}")
            return False
            
        success = True
        
        # Handle HMI/Modbus data
        if 'modbus_data' in combined_data:
            modbus_data = combined_data['modbus_data']
            if isinstance(modbus_data, list) and len(modbus_data) == 18:
                success &= self.insert_hmi_data(modbus_data)
            else:
                logger.error(f"Invalid modbus_data: expected list of 18 values, got {modbus_data}")
                success = False
        
        # Handle Teledyne data
        if 'teledyne_data' in combined_data:
            teledyne_data = combined_data['teledyne_data']
            if isinstance(teledyne_data, dict):
                flow_1 = teledyne_data.get('flow_1')
                flow_2 = teledyne_data.get('flow_2')
                flow_3 = teledyne_data.get('flow_3')
                if all(v is not None for v in [flow_1, flow_2, flow_3]):
                    success &= self.insert_teledyne_data([flow_1, flow_2, flow_3])
                else:
                    logger.error("Missing required teledyne flow values")
                    success = False
            else:
                logger.error(f"Invalid teledyne_data format: expected dict, got {type(teledyne_data)}")
                success = False
        
        # Handle LabJack data
        if 'labjack_data' in combined_data:
            labjack_data = combined_data['labjack_data']
            if isinstance(labjack_data, (int, float)):
                success &= self.insert_labjack_data(labjack_data)
            else:
                logger.error(f"Invalid labjack_data format: expected number, got {type(labjack_data)}")
                success = False
        
        return success

    def get_available_columns_by_table(self):
        """Get all available columns organized by table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all tables, excluding system tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            # Filter out system tables
            system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
            tables = [table for table in all_tables if table not in system_tables]
            
            columns_by_table = {}
            
            for table_name in tables:
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_info = cursor.fetchall()
                
                # Extract column names, excluding metadata columns
                available_columns = []
                for col in table_info:
                    col_name = col[1]
                    # Exclude metadata columns
                    if col_name not in ['id', 'created']:
                        available_columns.append(col_name)
                
                columns_by_table[table_name] = available_columns
            
            return columns_by_table
            
        except Exception as e:
            logger.error(f"Error getting available columns by table: {e}")
            return {}
        finally:
            conn.close()

# Create Flask app for receiving HMI data
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
collector = DataCollector()

@app.route('/', methods=['GET'])
def root():
    """Serve the main plotting interface"""
    return render_template('index.html')

@app.route('/query_db', methods=['GET'])
def query_db():
    """Query database for plotting data from respective tables"""
    try:
        # Get parameters from request
        keys = request.args.get('keys', '').split(',')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        table_name = request.args.get('table', None)  # None means all tables
        
        # Filter out empty keys
        keys = [key.strip() for key in keys if key.strip()]
        
        if not keys:
            return jsonify({"error": "No keys provided"}), 400
        
        # Get available columns by table
        columns_by_table = collector.get_available_columns_by_table()
        
        # Check which tables contain the requested keys
        valid_keys_by_table = {}
        invalid_keys = []
        
        for key in keys:
            key_found = False
            for table, table_columns in columns_by_table.items():
                if key in table_columns:
                    if table not in valid_keys_by_table:
                        valid_keys_by_table[table] = []
                    valid_keys_by_table[table].append(key)
                    key_found = True
                    break
            
            if not key_found:
                invalid_keys.append(key)
        
        if invalid_keys:
            logger.warning(f"Requested columns not found in any table: {invalid_keys}")
        
        if not valid_keys_by_table:
            return jsonify({"error": "No valid columns provided", "invalid_keys": invalid_keys}), 400
        
        # Get data from tables that contain the requested keys
        data_by_table = collector.get_data_by_time_range(
            start_time=start_time, 
            end_time=end_time, 
            table_name=table_name
        )
        
        # Filter data to only include tables that have the requested keys
        filtered_data_by_table = {}
        for table, table_data in data_by_table.items():
            if table in valid_keys_by_table:
                filtered_data_by_table[table] = table_data
        
        # Combine data from all relevant tables
        combined_data = []
        available_keys = set()
        
        for table, table_data in filtered_data_by_table.items():
            for record in table_data:
                # Add table prefix to timestamp to avoid conflicts
                if 'created' in record:
                    record[f'{table}_timestamp'] = record.pop('created')
                
                # Track available keys
                available_keys.update(record.keys())
                combined_data.append(record)
        
        # Get all valid keys that were actually found in the data
        all_valid_keys = []
        for table_keys in valid_keys_by_table.values():
            all_valid_keys.extend(table_keys)
        
        # Filter records to only include requested keys that are available
        final_valid_keys = [key for key in all_valid_keys if key in available_keys]
        filtered_data = []
        for record in combined_data:
            filtered_record = {}
            for key in final_valid_keys:
                if key in record:
                    filtered_record[key] = record[key]
            if filtered_record:  # Only add if we have some data
                filtered_data.append(filtered_record)
        
        return jsonify({
            "tables_queried": list(filtered_data_by_table.keys()),
            "columns": final_valid_keys,
            "data": filtered_data,
            "invalid_keys": invalid_keys,
            "columns_by_table": valid_keys_by_table
        }), 200
        
    except Exception as e:
        logger.error(f"Error querying database: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/receive_hmi_data', methods=['POST'])
def receive_hmi_data():
    """Endpoint to receive HMI data from HMI_TCP_Server.py"""
    try:
        data = request.get_json()
        if data and isinstance(data, list):
            success = collector.insert_hmi_data(data)
            if success:
                return jsonify({"status": "success", "message": "HMI data received and stored"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to store HMI data"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
    except Exception as e:
        logger.error(f"Error receiving HMI data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/receive_labjack_data', methods=['POST'])
def receive_labjack_data():
    """Endpoint to receive LabJack data"""
    try:
        data = request.get_json()
        if data and isinstance(data, (int, float)):
            success = collector.insert_labjack_data(data)
            if success:
                return jsonify({"status": "success", "message": "LabJack data received and stored"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to store LabJack data"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid data format - expected number"}), 400
    except Exception as e:
        logger.error(f"Error receiving LabJack data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/receive_teledyne_data', methods=['POST'])
def receive_teledyne_data():
    """Endpoint to receive Teledyne data"""
    try:
        data = request.get_json()
        if data and isinstance(data, list) and len(data) == 3:
            success = collector.insert_teledyne_data(data)
            if success:
                return jsonify({"status": "success", "message": "Teledyne data received and stored"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to store Teledyne data"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid data format - expected list of 3 values"}), 400
    except Exception as e:
        logger.error(f"Error receiving Teledyne data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/data', methods=['POST'])
def receive_data():
    """Endpoint to receive combined data from data acquisition devices"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        # Handle combined data format
        if isinstance(data, dict):
            success = collector.insert_combined_data(data)
            if success:
                return jsonify({"status": "success", "message": "Combined data received and stored"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to store combined data"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid data format - expected dict"}), 400
    except Exception as e:
        logger.error(f"Error receiving data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

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

@app.route('/latest_data', methods=['GET'])
def get_latest_data():
    """Get the latest data from all tables combined"""
    try:
        latest_data = collector.get_latest_data_from_all_tables()
        
        if not latest_data:
            return jsonify({"error": "No data found in any table"}), 404
        
        return jsonify({
            "status": "success",
            "data": latest_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting latest data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/recent_data', methods=['GET'])
def get_recent_data():
    """Get recent data from the database based on timestamp"""
    try:
        # Get parameters from request
        keys = request.args.get('keys', '').split(',')
        hours_back = int(request.args.get('hours', 1))  # Default to 1 hour
        table_name = request.args.get('table', None)  # None means all tables
        
        # Filter out empty keys
        keys = [key.strip() for key in keys if key.strip()]
        
        if not keys:
            return jsonify({"error": "No keys provided"}), 400
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Get available columns by table
        columns_by_table = collector.get_available_columns_by_table()
        
        # Check which tables contain the requested keys
        valid_keys_by_table = {}
        invalid_keys = []
        
        for key in keys:
            key_found = False
            for table, table_columns in columns_by_table.items():
                if key in table_columns:
                    if table not in valid_keys_by_table:
                        valid_keys_by_table[table] = []
                    valid_keys_by_table[table].append(key)
                    key_found = True
                    break
            
            if not key_found:
                invalid_keys.append(key)
        
        if invalid_keys:
            logger.warning(f"Requested columns not found in any table: {invalid_keys}")
        
        if not valid_keys_by_table:
            return jsonify({"error": "No valid columns provided", "invalid_keys": invalid_keys}), 400
        
        # Get data from tables that contain the requested keys
        data_by_table = collector.get_data_by_time_range(
            start_time=start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time=end_time.strftime('%Y-%m-%d %H:%M:%S'),
            table_name=table_name
        )
        
        # Filter data to only include tables that have the requested keys
        filtered_data_by_table = {}
        for table, table_data in data_by_table.items():
            if table in valid_keys_by_table:
                filtered_data_by_table[table] = table_data
        
        # Combine data from all relevant tables
        combined_data = []
        available_keys = set()
        
        for table, table_data in filtered_data_by_table.items():
            for record in table_data:
                # Add table prefix to timestamp to avoid conflicts
                if 'created' in record:
                    record[f'{table}_timestamp'] = record.pop('created')
                
                # Track available keys
                available_keys.update(record.keys())
                combined_data.append(record)
        
        # Get all valid keys that were actually found in the data
        all_valid_keys = []
        for table_keys in valid_keys_by_table.values():
            all_valid_keys.extend(table_keys)
        
        # Filter records to only include requested keys that are available
        final_valid_keys = [key for key in all_valid_keys if key in available_keys]
        filtered_data = []
        for record in combined_data:
            filtered_record = {}
            for key in final_valid_keys:
                if key in record:
                    filtered_record[key] = record[key]
            if filtered_record:  # Only add if we have some data
                filtered_data.append(filtered_record)
        
        return jsonify({
            "tables_queried": list(filtered_data_by_table.keys()),
            "columns": final_valid_keys,
            "data": filtered_data,
            "invalid_keys": invalid_keys,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours_back": hours_back
            },
            "columns_by_table": valid_keys_by_table
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recent data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/available_columns', methods=['GET'])
def get_available_columns():
    """Get list of available columns from all tables"""
    try:
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
            "columns": unique_columns,  # This is what the HTML expects
            "tables": columns_by_table,
            "total_columns": len(unique_columns),
            "table_count": len(columns_by_table)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting available columns: {e}")
        return jsonify({"error": str(e), "columns": []}), 500

@app.route('/db_status', methods=['GET'])
def get_db_status():
    """Check database status and available tables"""
    try:
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        # Get all tables, excluding system tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Filter out system tables
        system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
        tables = [table for table in all_tables if table not in system_tables]
        
        table_info = {}
        total_records = 0
        
        for table_name in tables:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            table_schema = cursor.fetchall()
            
            # Get total record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = cursor.fetchone()[0]
            total_records += record_count
            
            table_info[table_name] = {
                "columns": [col[1] for col in table_schema],
                "record_count": record_count
            }
        
        conn.close()
        
        return jsonify({
            "status": "ok",
            "tables": table_info,
            "total_records": total_records,
            "has_data": total_records > 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        return jsonify({"error": str(e)}), 500

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