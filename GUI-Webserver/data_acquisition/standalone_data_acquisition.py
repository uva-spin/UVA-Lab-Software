#!/usr/bin/env python3
"""
Standalone Data Acquisition Script
This script runs on the machine connected to Modbus devices and sends data to a remote Flask server.
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
        
        return rounded_float_values
        
    except Exception as e:
        logger.error(f"Error reading Modbus data: {e}")
        return None

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

def save_to_local_csv(data):
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
                header_row = ['timestamp'] + labels
                writer.writerow(header_row)
            
            # Write data row
            data_row = [datetime.now().isoformat()] + data
            writer.writerow(data_row)
        
        logger.debug(f"Data saved to local CSV: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving to local CSV: {e}")
        return False

def main():
    """Main data acquisition loop"""
    logger.info("Starting Data Acquisition System")
    logger.info(f"Remote server URL: {REMOTE_SERVER_URL}")
    logger.info(f"Sleep interval: {SLEEP_INTERVAL} seconds")
    
    # Ensure data directory exists
    ensure_data_directory()
    
    consecutive_failures = 0
    max_consecutive_failures = MAX_CONSECUTIVE_FAILURES
    
    while True:
        try:
            # Read data from Modbus
            data = read_modbus_data()
            
            if data is None:
                consecutive_failures += 1
                logger.warning(f"Failed to read data (attempt {consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.error("Too many consecutive failures, stopping")
                    break
                    
                time.sleep(SLEEP_INTERVAL)
                continue
            
            # Reset failure counter on successful read
            consecutive_failures = 0
            
            # Send to remote server
            server_success = send_to_remote_server(data)
            
            # Always save locally as backup
            csv_success = save_to_local_csv(data)
            
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

if __name__ == '__main__':
    main() 