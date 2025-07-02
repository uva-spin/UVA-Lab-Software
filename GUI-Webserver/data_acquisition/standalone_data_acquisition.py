#!/usr/bin/env python3
"""
Standalone Data Acquisition Script
This script runs on the machine connected to Modbus devices and sends data to a remote Flask server.
Also reads from teledyne_flow.csv in real-time.
"""

from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import struct
import time
import csv
import requests
import json
import logging
from datetime import datetime
import os
import threading
from collections import deque
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_acquisition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import configuration
try:
    from config import *
except ImportError:
    # Default configuration if config.py doesn't exist
    REMOTE_SERVER_URL = "http://172.29.36.50:5000/data"
    LOCAL_CSV_DIR = "data_logs"
    SLEEP_INTERVAL = 5
    MAX_CONSECUTIVE_FAILURES = 10
    PLC_IP = "192.168.0.1"
    UNIT_ID = 2
    INT_PORT = 503
    FLOAT_PORT = 502
    NUM_REG_TO_READ = 49
    LOG_LEVEL = "INFO"
    LOG_FILE = "data_acquisition.log"
    TELEDYNE_CSV_PATH = "../static/csv/teledyne_flow.csv"
    TELEDYNE_CHECK_INTERVAL = 1  # Check for new data every second

# Define the labels for the float values
labels = [
    "FC501.AI.Value",
    "FC501_OUT.Value", 
    "FC502.AI.Value",
    "FC502_OUT.Value",
    "LIT501.AI.Value",
    "PT501.AI.Value",
    "PT502.AI.Value",
    "PT503.AI.Value",
    "PT504.AI.Value",
    'Purity Meter_DB."Purity Downstream"',
    'Purity Meter_DB."Purity Upstream"',
    "AIT501.AI.Value",
    "TI501.AI.Value",
    "TI502.AI.Value",
    "TI503.AI.Value",
    "TI504.AI.Value",
    "TI505.AI.Value",
    "TI523.AI.Value"
]

# Define labels for teledyne flow data
teledyne_labels = [
    "teledyne_timestamp",
    "teledyne_flow_1",
    "teledyne_flow_2", 
    "teledyne_flow_3"
]

class TeledyneDataReader:
    """Thread-safe class to read teledyne flow data in real-time"""
    
    def __init__(self, csv_path, check_interval=1):
        self.csv_path = csv_path
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the teledyne data reading thread"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_file, daemon=True)
        self.thread.start()
        logger.info(f"Started teledyne data monitoring for {self.csv_path}")
        
    def stop(self):
        """Stop the teledyne data reading thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def get_latest_data(self):
        """Get the latest teledyne data from the queue"""
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None
            
    def _monitor_file(self):
        """Monitor the CSV file for new data"""
        while self.running:
            try:
                if os.path.exists(self.csv_path):
                    with open(self.csv_path, 'r') as file:
                        # Move to the last known position
                        file.seek(self.last_position)
                        
                        # Read new lines
                        new_lines = file.readlines()
                        
                        if new_lines:
                            # Update position for next read
                            self.last_position = file.tell()
                            
                            # Process new lines
                            for line in new_lines:
                                line = line.strip()
                                if line:
                                    try:
                                        # Parse CSV line
                                        data = line.split(',')
                                        if len(data) >= 4:  # timestamp + 3 flow values
                                            teledyne_data = {
                                                'timestamp': data[0],
                                                'flow_1': float(data[1]),
                                                'flow_2': float(data[2]),
                                                'flow_3': float(data[3])
                                            }
                                            self.data_queue.put(teledyne_data)
                                            logger.debug(f"New teledyne data: {teledyne_data}")
                                    except (ValueError, IndexError) as e:
                                        logger.warning(f"Error parsing teledyne data line: {line}, error: {e}")
                else:
                    logger.warning(f"Teledyne CSV file not found: {self.csv_path}")
                    
            except Exception as e:
                logger.error(f"Error monitoring teledyne file: {e}")
                
            time.sleep(self.check_interval)

# Global teledyne reader instance
teledyne_reader = None

def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(LOCAL_CSV_DIR, exist_ok=True)
    logger.info(f"Data directory ready: {LOCAL_CSV_DIR}")

def read_modbus_data():
    """Read data from Modbus TCP server"""
    plc_ip = PLC_IP
    unit_id = UNIT_ID
    int_port = INT_PORT
    float_port = FLOAT_PORT
    num_reg_to_read = NUM_REG_TO_READ

    try:
        # Read integer values
        client = ModbusClient(host=plc_ip, port=int_port, unit_id=unit_id, auto_open=True, auto_close=False)
        int_regs = client.read_holding_registers(0, num_reg_to_read)
        if int_regs:
            logger.debug(f'Integer values: {utils.get_list_2comp(int_regs, 16)}')
        else:
            logger.warning("Failed to read integer registers")

        # Read float values
        client = ModbusClient(host=plc_ip, port=float_port, unit_id=unit_id, auto_open=True, auto_close=False)
        float_regs = client.read_holding_registers(0, num_reg_to_read)
        
        if not float_regs:
            logger.error("Failed to read float registers")
            return None
            
        float_values = []
        for i in range(0, num_reg_to_read - 1, 2):
            raw = struct.pack(">HH", float_regs[i], float_regs[i + 1])  # Big Endian format
            float_values.append(struct.unpack(">f", raw)[0])  # Convert to float
        
        # Round float values to 2 decimal places
        rounded_float_values = [round(value, 2) for value in float_values]
        logger.info(f"Read {len(rounded_float_values)} float values from Modbus")
        
        # Ensure we have exactly 18 values for HMI data
        if len(rounded_float_values) >= 18:
            hmi_data = rounded_float_values[:18]
            logger.info(f"Using first 18 values for HMI data: {hmi_data[:3]}...")
            return hmi_data
        else:
            logger.error(f"Not enough float values: got {len(rounded_float_values)}, need 18")
            return None
        
    except Exception as e:
        logger.error(f"Error reading Modbus data: {e}")
        return None

def read_teledyne_data():
    """Read latest teledyne flow data"""
    global teledyne_reader
    
    if teledyne_reader is None:
        return None
        
    return teledyne_reader.get_latest_data()

def combine_data(modbus_data, teledyne_data):
    """Combine Modbus and teledyne data into a single data structure"""
    combined_data = {
        'timestamp': datetime.now().isoformat(),
        'modbus_data': modbus_data,
        'teledyne_data': teledyne_data
    }
    
    # Create a flat list for CSV storage
    csv_data = modbus_data.copy()
    
    if teledyne_data:
        csv_data.extend([
            teledyne_data['timestamp'],
            teledyne_data['flow_1'],
            teledyne_data['flow_2'],
            teledyne_data['flow_3']
        ])
    else:
        # Add empty values if no teledyne data
        csv_data.extend(['', '', '', ''])
        
    return combined_data, csv_data

def send_to_remote_server(data):
    """Send data to the remote Flask server"""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(REMOTE_SERVER_URL, data=json.dumps(data), headers=headers, timeout=10)
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info("Data sent to remote server successfully")
            return True
        else:
            logger.warning(f"Remote server returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to remote server: {e}")
        return False

def save_to_local_csv(data, csv_data):
    """Save data to local CSV file as backup"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = os.path.join(LOCAL_CSV_DIR, f"hmi_data_{timestamp}.csv")
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            if not file_exists:
                # Write headers
                header_row = ['timestamp'] + labels + teledyne_labels
                writer.writerow(header_row)
            
            # Write data row
            data_row = [datetime.now().isoformat()] + csv_data
            writer.writerow(data_row)
        
        logger.debug(f"Data saved to local CSV: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving to local CSV: {e}")
        return False

def main():
    """Main data acquisition loop"""
    global teledyne_reader
    
    logger.info("Starting Data Acquisition System")
    logger.info(f"Remote server URL: {REMOTE_SERVER_URL}")
    logger.info(f"Sleep interval: {SLEEP_INTERVAL} seconds")
    logger.info(f"Teledyne CSV path: {TELEDYNE_CSV_PATH}")
    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Start teledyne data reader
    teledyne_reader = TeledyneDataReader(TELEDYNE_CSV_PATH, TELEDYNE_CHECK_INTERVAL)
    teledyne_reader.start()
    
    consecutive_failures = 0
    max_consecutive_failures = MAX_CONSECUTIVE_FAILURES
    
    try:
        while True:
            try:
                # Read data from Modbus
                modbus_data = read_modbus_data()
                
                if modbus_data is None:
                    consecutive_failures += 1
                    logger.warning(f"Failed to read Modbus data (attempt {consecutive_failures})")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error("Too many consecutive failures, stopping")
                        break
                        
                    time.sleep(SLEEP_INTERVAL)
                    continue
                
                # Reset failure counter on successful read
                consecutive_failures = 0
                
                # Read teledyne data
                teledyne_data = read_teledyne_data()
                
                # Combine data
                combined_data, csv_data = combine_data(modbus_data, teledyne_data)
                
                # Send to remote server
                server_success = send_to_remote_server(combined_data)
                
                # Always save locally as backup
                csv_success = save_to_local_csv(combined_data, csv_data)
                
                if not server_success:
                    logger.warning("Remote server unavailable, data saved locally only")
                
                # Wait before next reading
                time.sleep(SLEEP_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Data acquisition stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(SLEEP_INTERVAL)
                
    finally:
        # Clean up
        if teledyne_reader:
            teledyne_reader.stop()
            logger.info("Teledyne data reader stopped")

if __name__ == '__main__':
    main() 