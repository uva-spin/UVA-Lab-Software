import sqlite3
import csv
import json
import time
import threading
import os
from datetime import datetime
from pathlib import Path
import requests
from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, db_path="../instance/flaskr.sqlite", csv_dir="../static/csv"):
        self.db_path = db_path
        self.csv_dir = csv_dir
        self.csv_files = {
            'r_values': 'r_values.csv',
            'hmi_data': 'hmi_data.csv', # HMI data
            'channel_data': 'teledyne_temp.csv'  # CSV file with CH1, CH2, CH3 data
        }
        self.last_modified = {}
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
    
    def process_csv_file(self, filename, data_type):
        """Process a CSV file and insert new data into database"""
        filepath = os.path.join(self.csv_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"CSV file not found: {filepath}")
            return
            
        # Check if file has been modified
        current_mtime = os.path.getmtime(filepath)
        if filename in self.last_modified and current_mtime <= self.last_modified[filename]:
            return  # No changes
            
        self.last_modified[filename] = current_mtime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            with open(filepath, 'r', newline='') as csvfile:
                if data_type == 'channel_data':
                    # For teledyne_temp.csv, use regular reader since no headers
                    reader = csv.reader(csvfile)
                    
                    for row in reader:
                        # Handle CSV with no headers: Timestamp, CH1, CH2, CH3
                        if len(row) >= 4:  # Ensure we have at least 4 columns
                            timestamp = row[0]  # First column is timestamp
                            ch1 = row[1]        # Second column is CH1
                            ch2 = row[2]        # Third column is CH2
                            ch3 = row[3]        # Fourth column is CH3
                            
                            if timestamp and ch1 and ch2 and ch3:
                                cursor.execute('''
                                    SELECT id FROM merged_data 
                                    WHERE timestamp = ? AND data_source = 'channel_data'
                                ''', (timestamp,))
                                
                                if not cursor.fetchone():
                                    cursor.execute('''
                                        INSERT INTO merged_data (timestamp, ch1, ch2, ch3, data_source)
                                        VALUES (?, ?, ?, ?, ?)
                                    ''', (timestamp, float(ch1), float(ch2), float(ch3), 'channel_data'))
                else:
                    # For other CSV files, use DictReader since they have headers
                    reader = csv.DictReader(csvfile)
                    
                    for row in reader:
                        # Check if this record already exists
                        if data_type == 'r_values':
                            timestamp = row.get('Timestamp')
                            r2_value = row.get('R2 Value')
                            
                            if timestamp and r2_value:
                                cursor.execute('''
                                    SELECT id FROM merged_data 
                                    WHERE timestamp = ? AND data_source = 'r_values'
                                ''', (timestamp,))
                                
                                if not cursor.fetchone():
                                    cursor.execute('''
                                        INSERT INTO merged_data (timestamp, r2_value, data_source)
                                        VALUES (?, ?, ?)
                                    ''', (timestamp, float(r2_value), 'r_values'))

            conn.commit()
            logger.info(f"Processed {data_type} CSV file: {filename}")
            
        except Exception as e:
            logger.error(f"Error processing CSV file {filename}: {e}")
        finally:
            conn.close()
    
    def monitor_csv_files(self):
        """Monitor all CSV files for changes"""
        for data_type, filename in self.csv_files.items():
            self.process_csv_file(filename, data_type)
    
    def start_csv_monitoring(self, interval=30):
        """Start a background thread to monitor CSV files"""
        def monitor_loop():
            while True:
                try:
                    self.monitor_csv_files()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in CSV monitoring loop: {e}")
                    time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info(f"Started CSV monitoring with {interval}s interval")

# Create Flask app for receiving HMI data
app = Flask(__name__)
collector = DataCollector()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for basic connectivity test"""
    return jsonify({
        "status": "running",
        "endpoints": {
            "data": "/data (POST)",
            "receive_hmi_data": "/receive_hmi_data (POST)",
            "health": "/health (GET)"
        },
        "timestamp": datetime.now().isoformat()
    }), 200

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
            success = collector.insert_hmi_data(data)
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
    # Start CSV monitoring
    collector.start_csv_monitoring(interval=30)
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False) 