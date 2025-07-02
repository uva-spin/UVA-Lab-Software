import sqlite3
import json
import time
import threading
import os
from datetime import datetime
from pathlib import Path
import requests
from flask import Flask, request, jsonify, render_template
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, db_path="../instance/flaskr.sqlite"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Initialize the database with the updated schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create the main data table with all columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS merged_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                -- HMI Data columns
                fc501_ai FLOAT,
                fc501_out FLOAT,
                fc502_ai FLOAT,
                fc502_out FLOAT,
                lit501_ai FLOAT,
                pt501_ai FLOAT,
                pt502_ai FLOAT,
                pt503_ai FLOAT,
                pt504_ai FLOAT,
                purity_downstream FLOAT,
                purity_upstream FLOAT,
                ait501_ai FLOAT,
                ti501_ai FLOAT,
                ti502_ai FLOAT,
                ti503_ai FLOAT,
                ti504_ai FLOAT,
                ti505_ai FLOAT,
                ti523_ai FLOAT,
                
                -- R Values columns
                r2_value FLOAT,
                
                -- Channel Data columns (CH1, CH2, CH3)
                ch1 FLOAT,
                ch2 FLOAT,
                ch3 FLOAT,
                
                -- Metadata
                data_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index on timestamp for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON merged_data(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database setup completed")
    
    def insert_merged_data(self, data):
        """Insert merged data that may contain HMI data plus additional columns"""
        if not isinstance(data, list):
            logger.error(f"Expected list data, got {type(data)}")
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Determine data type based on length
            if len(data) == 18:
                # Pure HMI data - 18 values
                cursor.execute('''
                    INSERT INTO merged_data (
                        fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                        pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream,
                        purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                        ti504_ai, ti505_ai, ti523_ai, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data + ['hmi'])
                logger.info(f"Inserted HMI data: {data[:3]}...")
                
            elif len(data) == 21:
                # HMI data (18) + R2 value (1) + CH1, CH2, CH3 (3) = 21 values
                hmi_data = data[:18]
                r2_value = data[18]
                ch1, ch2, ch3 = data[19:22]
                
                cursor.execute('''
                    INSERT INTO merged_data (
                        fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                        pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream,
                        purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                        ti504_ai, ti505_ai, ti523_ai, r2_value, ch1, ch2, ch3, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', hmi_data + [r2_value, ch1, ch2, ch3, 'merged'])
                logger.info(f"Inserted merged data with HMI + R2 + CH: {data[:3]}...")
                
            elif len(data) == 24:
                # Extended merged data - handle based on your specific format
                # Assuming: HMI (18) + R2 (1) + CH1, CH2, CH3 (3) + additional (2) = 24 values
                hmi_data = data[:18]
                r2_value = data[18]
                ch1, ch2, ch3 = data[19:22]
                additional = data[22:24]  # Any additional columns
                
                cursor.execute('''
                    INSERT INTO merged_data (
                        fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                        pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream,
                        purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                        ti504_ai, ti505_ai, ti523_ai, r2_value, ch1, ch2, ch3, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', hmi_data + [r2_value, ch1, ch2, ch3, 'merged_extended'])
                logger.info(f"Inserted extended merged data: {data[:3]}...")
                
            else:
                logger.error(f"Unexpected data length: {len(data)}. Expected 18, 21, or 24 values")
                return False
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting merged data: {e}")
            return False
        finally:
            conn.close()

    def insert_hmi_data(self, data):
        """Insert HMI data into the database"""
        if len(data) != 18:  # Expected 18 values from HMI_TCP_Server
            logger.error(f"Expected 18 HMI values, got {len(data)}")
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO merged_data (
                    fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                    pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream,
                    purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                    ti504_ai, ti505_ai, ti523_ai, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data + ['hmi'])
            
            conn.commit()
            logger.info(f"Inserted HMI data: {data[:3]}...")  # Log first 3 values
            return True
        except Exception as e:
            logger.error(f"Error inserting HMI data: {e}")
            return False
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
    """Query database for plotting data"""
    try:
        # Get parameters from request
        keys = request.args.get('keys', '').split(',')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        
        # Filter out empty keys
        keys = [key.strip() for key in keys if key.strip()]
        
        if not keys:
            return jsonify({"error": "No keys provided"}), 400
        
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        # First, get the actual columns that exist in the database
        cursor.execute("PRAGMA table_info(merged_data)")
        table_info = cursor.fetchall()
        available_columns = [col[1] for col in table_info]
        
        # Filter keys to only include columns that actually exist
        valid_keys = [key for key in keys if key in available_columns]
        invalid_keys = [key for key in keys if key not in available_columns]
        
        if invalid_keys:
            logger.warning(f"Requested columns not found in database: {invalid_keys}")
        
        if not valid_keys:
            return jsonify({"error": "No valid columns provided", "invalid_keys": invalid_keys}), 400
        
        # Build the query dynamically based on requested columns
        columns = ['timestamp'] + valid_keys
        column_list = ', '.join(columns)
        
        # Build WHERE clause for time range if provided
        where_clause = ""
        params = []
        if start_time and end_time:
            where_clause = "WHERE timestamp BETWEEN ? AND ?"
            params = [start_time, end_time]
        
        query = f"SELECT {column_list} FROM merged_data {where_clause} ORDER BY timestamp DESC LIMIT 1000"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
            data.append(row_dict)
        
        conn.close()
        
        return jsonify({
            "columns": valid_keys,
            "data": data,
            "invalid_keys": invalid_keys
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
                return jsonify({"status": "success", "message": "Data received and stored"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to store data"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
    except Exception as e:
        logger.error(f"Error receiving HMI data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/data', methods=['POST'])
def receive_data():
    """Endpoint to receive data from data acquisition devices"""
    try:
        data = request.get_json()
        if data and isinstance(data, list):
            success = collector.insert_merged_data(data)
            if success:
                return jsonify({"status": "success", "message": "Data received and stored"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to store data"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
    except Exception as e:
        logger.error(f"Error receiving data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False) 