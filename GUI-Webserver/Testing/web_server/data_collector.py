#!/usr/bin/env python3
import sqlite3
import json
import time
import threading
import os
import signal
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
from flask import Flask, request, jsonify, render_template
import logging
import pytz

from config import DATABASE_PATH, DATABASE_NAME, DATABASE_DIR

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
    def __init__(self, db_path=f"/var/www/spin/instance/flaskr.sqlite"):
        self.db_path = db_path

        print(f"Database path: {self.db_path}")
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
                       ti504_ai, ti505_ai, ti523_ai, "Timestamp"
                FROM HMI 
                ORDER BY "Timestamp" DESC 
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
                SELECT Pressure_1, Pressure_2, Pressure_3, "Timestamp"
                FROM Pressures 
                ORDER BY "Timestamp" DESC 
                LIMIT 1
            """)
            labjack_data = cursor.fetchone()
            if labjack_data:
                combined_data.update({
                    'Pressure_1': labjack_data[0],
                    'Pressure_2': labjack_data[1],
                    'Pressure_3': labjack_data[2],
                    'labjack_timestamp': get_current_est_time()
                })
            
            # Get latest Teledyne data
            cursor.execute("""
                SELECT seperator_flow, magnet_flow, main_flow, "Timestamp"
                FROM Flow_Rates 
                ORDER BY "Timestamp" DESC 
                LIMIT 1
            """)
            teledyne_data = cursor.fetchone()
            if teledyne_data:
                combined_data.update({
                    'seperator_flow': teledyne_data[0],
                    'magnet_flow': teledyne_data[1],
                    'main_flow': teledyne_data[2],
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
                
                # Check if 'Timestamp' column exists
                has_timestamp_column = '"Timestamp"' in columns
                
                where_clause = ""
                params = []
                order_clause = ""
                
                if has_timestamp_column:
                    if start_time and end_time:
                        where_clause = 'WHERE "Timestamp" BETWEEN ? AND ?'
                        params = [start_time, end_time]
                    order_clause = 'ORDER BY "Timestamp" ASC'
                else:
                    # If no Timestamp column, just get all data
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
            logger.info(f"Inserted HMI data!")
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

        if len(pressure_data) != 4:
            logger.error(f"Expected 4 pressure values, got {len(pressure_data)}")
            return False
        
        try:
            cursor.execute('''
                INSERT INTO labjack (Root_Exhaust_Pressure, Buffer_Pressure, Magnet_Pressure, Purifier_Inlet_Pressure) VALUES (?, ?, ?, ?)
            ''', (pressure_data[0], pressure_data[1], pressure_data[2], pressure_data[3]))
            
            conn.commit()
            logger.info(f"Inserted LabJack data!")
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
                INSERT INTO teledyne (Seperator_Flow, Magnet_Flow, Main_Flow) VALUES (?, ?, ?)
            ''', flow_data)
            
            conn.commit()
            logger.info(f"Inserted Teledyne data!")
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
                seperator_flow = teledyne_data.get('Seperator_Flow')
                magnet_flow = teledyne_data.get('Magnet_Flow')
                main_flow = teledyne_data.get('Main_Flow')
                if all(v is not None for v in [seperator_flow, magnet_flow, main_flow]):
                    success &= self.insert_teledyne_data([seperator_flow, magnet_flow, main_flow])
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
                    if col_name not in ['id', '"Timestamp"']:
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

# @app.route('/query_db', methods=['GET'])
# def query_db():
#     """Query database for plotting data from respective tables"""
#     try:
#         # Get parameters from request
#         keys = request.args.get('keys', '').split(',')
#         start_time = request.args.get('start_time', '')
#         end_time = request.args.get('end_time', '')
#         table_name = request.args.get('table', None)  # None means all tables
        
#         # Filter out empty keys
#         keys = [key.strip() for key in keys if key.strip()]
        
#         if not keys:
#             return jsonify({"error": "No keys provided"}), 400
        
#         # Get available columns by table
#         columns_by_table = collector.get_available_columns_by_table()
        
#         # Check which tables contain the requested keys
#         valid_keys_by_table = {}
#         invalid_keys = []
        
#         for key in keys:
#             key_found = False
#             for table, table_columns in columns_by_table.items():
#                 if key in table_columns:
#                     if table not in valid_keys_by_table:
#                         valid_keys_by_table[table] = []
#                     valid_keys_by_table[table].append(key)
#                     key_found = True
#                     break
            
#             if not key_found:
#                 invalid_keys.append(key)
        
#         if invalid_keys:
#             logger.warning(f"Requested columns not found in any table: {invalid_keys}")
        
#         if not valid_keys_by_table:
#             return jsonify({"error": "No valid columns provided", "invalid_keys": invalid_keys}), 400
        
#         # Get data from tables that contain the requested keys
#         data_by_table = collector.get_data_by_time_range(
#             start_time=start_time, 
#             end_time=end_time, 
#             table_name=table_name
#         )
        
#         # Filter data to only include tables that have the requested keys
#         filtered_data_by_table = {}
#         for table, table_data in data_by_table.items():
#             if table in valid_keys_by_table:
#                 filtered_data_by_table[table] = table_data
        
#         # Combine data from all relevant tables
#         combined_data = []
#         available_keys = set()
        
#         for table, table_data in filtered_data_by_table.items():
#             for record in table_data:
#                 # Add table prefix to timestamp to avoid conflicts
#                 if '"Timestamp"' in record:
#                     record[f'{table}_timestamp'] = record.pop('"Timestamp"')
                
#                 # Track available keys
#                 available_keys.update(record.keys())
#                 combined_data.append(record)
        
#         # Get all valid keys that were actually found in the data
#         all_valid_keys = []
#         for table_keys in valid_keys_by_table.values():
#             all_valid_keys.extend(table_keys)
        
#         # Filter records to only include requested keys that are available
#         final_valid_keys = [key for key in all_valid_keys if key in available_keys]
#         filtered_data = []
#         for record in combined_data:
#             filtered_record = {}
#             for key in final_valid_keys:
#                 if key in record:
#                     filtered_record[key] = record[key]
#             if filtered_record:  # Only add if we have some data
#                 filtered_data.append(filtered_record)
        
#         return jsonify({
#             "tables_queried": list(filtered_data_by_table.keys()),
#             "columns": final_valid_keys,
#             "data": filtered_data,
#             "invalid_keys": invalid_keys,
#             "columns_by_table": valid_keys_by_table
#         }), 200
        
#     except Exception as e:
#         logger.error(f"Error querying database: {e}")
#         return jsonify({"error": str(e)}), 500

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

@app.route('/recent_data', methods=['GET'])
def get_recent_data():
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

        # Get EST timezone
        est = pytz.timezone('America/New_York')
        
        logger.info(f"Fetching data for keys: {keys}")
        logger.info(f"Time range (EST): {db_start_time} to {db_end_time}")
        
        # Connect to database
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        all_data = {}
        available_keys = []
        missing_keys = []
        
        # Check each table for the requested columns
        for table in ['HMI', 'Pressures', 'Flow_Rates']:  
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Find which keys are in this table
            table_keys = [key for key in keys if key in columns]
            if not table_keys:
                continue
                
            logger.info(f"Found keys {table_keys} in table {table}")
            
            # Build the query for this table
            columns_str = ', '.join(['"Timestamp"'] + table_keys)
            query = f"""
                SELECT {columns_str}
                FROM {table}
                WHERE "Timestamp" >= ? AND "Timestamp" <= ?
                ORDER BY "Timestamp" ASC
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
                        all_data[timestamp] = {'timestamp': timestamp}
                    
                    # Add data for each key
                    for i, key in enumerate(table_keys, 1):
                        try:
                            all_data[timestamp][key] = round(float(row[i]), 2)
                        except (ValueError, TypeError):
                            logger.warning(f"Could not convert value for {key}: {row[i]}")
                            all_data[timestamp][key] = None
                
                available_keys.extend(table_keys)
            else:
                missing_keys.extend(table_keys)
                
        conn.close()
        
        # Convert dictionary to list and sort by timestamp
        data = list(all_data.values())
        data.sort(key=lambda x: x['timestamp'])
        
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
        
    except Exception as e:
        logger.error(f"Error getting recent data: {e}")
        logger.exception("Full traceback:")
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

@app.route('/test_db', methods=['GET'])
def test_db():
    """Test database connection and data availability"""
    try:
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        # Get all tables, excluding system tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Filter out system tables
        system_tables = ['sqlite_sequence', 'sqlite_stat1', 'sqlite_stat2', 'sqlite_stat3', 'sqlite_stat4']
        tables = [table for table in all_tables if table not in system_tables]
        
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
        
        conn.close()
        
        return jsonify({
            "status": "ok",
            "total_records": total_records,
            "data_sources": data_sources,
            "tables": tables
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing database: {e}")
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