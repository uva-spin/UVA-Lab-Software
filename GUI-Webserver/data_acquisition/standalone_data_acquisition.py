#!/usr/bin/env python3
"""
Standalone Data Acquisition Script
This script runs on the machine connected to Modbus devices and pipelines data directly to the database.
Also reads from teledyne_flow.csv and labjack_pressure.csv in real-time.
"""

from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import struct
import time
import csv
import json
import logging
from datetime import datetime
import os
import threading
from collections import deque
import queue
import sqlite3
from _TeledyneReader import TeledyneDataReader
from _LabJackReader import LabJackReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for even more detail
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_acquisition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add file handler with more detailed format for debugging
debug_handler = logging.FileHandler('data_acquisition_debug.log')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'))
logger.addHandler(debug_handler)

# Import configuration
try:
    from config import *
except ImportError:
    print("No config.py file found, using default configuration")
    # Default configuration if config.py doesn't exist
    DATABASE_PATH = f"{DATABASE_DIR}/{DATABASE_NAME}"
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
    TWIST_PATH = "/www.twist.phys.virginia.edu/www/spin"  # Update this to your actual mount point
    DATABASE_DIR = f"{TWIST_PATH}/instance"
    TELEDYNE_CSV_PATH = f"{TWIST_PATH}/monitoring/teledyne_flow.csv"
    TELEDYNE_CHECK_INTERVAL = 1  # Check for new data every second
    LABJACK_CSV_PATH = f"{TWIST_PATH}/monitoring/labjack_pressure.csv"
    LABJACK_CHECK_INTERVAL = 1  # Check for new data every second

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

Pressure_labels = [
    "Pressure_1"
]

# Global teledyne reader instance
teledyne_reader = None

# Global labjack reader instance
labjack_reader = None

def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(LOCAL_CSV_DIR, exist_ok=True)
    logger.info(f"Data directory ready: {LOCAL_CSV_DIR}")

def ensure_database_directory():
    """Ensure the database directory exists"""
    db_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Database directory created: {db_dir}")

def setup_database():
    """Initialize the database with the schema-defined tables"""
    ensure_database_directory()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Use the schema.sql file to create tables
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

def _read_HMI():
    """Read data from Modbus TCP server"""
    plc_ip = PLC_IP
    unit_id = UNIT_ID
    int_port = INT_PORT
    float_port = FLOAT_PORT
    num_reg_to_read = NUM_REG_TO_READ

    logger.info(f"=== Starting HMI Read ===")
    logger.info(f"PLC IP: {plc_ip}")
    logger.info(f"Unit ID: {unit_id}")
    logger.info(f"Integer Port: {int_port}")
    logger.info(f"Float Port: {float_port}")

    try:
        # Test network connectivity first
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 2 second timeout
            result = sock.connect_ex((plc_ip, int_port))
            if result == 0:
                logger.info(f"Network connection to {plc_ip}:{int_port} successful")
            else:
                logger.error(f"Cannot connect to {plc_ip}:{int_port} - Port closed or unreachable")
        except Exception as e:
            logger.error(f"Network test failed: {e}")
        finally:
            sock.close()

        # Read integer values
        logger.info("Creating ModbusClient for integer registers...")
        client = ModbusClient(
            host=plc_ip,
            port=int_port,
            unit_id=unit_id,
            auto_open=True,
            auto_close=False,
        )
        
        if not client.is_open:
            logger.error(f"Failed to open connection for integer registers")
            logger.info("Attempting manual open...")
            open_result = client.open()
            logger.info(f"Manual open result: {open_result}")
            if not client.is_open:
                return None
            
        logger.info("Reading integer registers...")
        int_regs = client.read_holding_registers(0, num_reg_to_read)
        if int_regs:
            int_values = utils.get_list_2comp(int_regs, 16)
            logger.info(f'Successfully read integer values: {int_values[:3]}... ({len(int_values)} values)')
        else:
            logger.warning(f"Failed to read integer registers from {plc_ip}:{int_port}")

        # Read float values
        logger.info(f"Connecting to PLC for float registers (Port {float_port})...")
        client = ModbusClient(host=plc_ip, port=float_port, unit_id=unit_id, auto_open=True, auto_close=False)
        
        if not client.is_open:
            logger.error("Failed to open connection for float registers")
            return None
            
        logger.info("Reading float registers...")
        float_regs = client.read_holding_registers(0, num_reg_to_read)
        
        if not float_regs:
            logger.error(f"Failed to read float registers from {plc_ip}:{float_port}")
            return None
            
        logger.info(f"Successfully read {len(float_regs)} float registers")
            
        float_values = []
        logger.info("Converting register pairs to float values...")
        for i in range(0, num_reg_to_read - 1, 2):
            try:
                raw = struct.pack(">HH", float_regs[i], float_regs[i + 1])  # Big Endian format
                value = struct.unpack(">f", raw)[0]  # Convert to float
                float_values.append(value)
            except Exception as e:
                logger.error(f"Error converting registers {i},{i+1} to float: {e}")
                return None
        
        # Round float values to 2 decimal places
        rounded_float_values = [round(value, 2) for value in float_values]
        logger.info(f"Processed {len(rounded_float_values)} float values")
        
        # Log each value with its corresponding label
        for label, value in zip(labels, rounded_float_values[:18]):
            logger.debug(f"{label}: {value}")
        
        # Ensure we have exactly 18 values for HMI data
        if len(rounded_float_values) >= 18:
            hmi_data = rounded_float_values[:18]
            logger.info("Successfully read all HMI data:")
            logger.info("First 3 values:")
            for i in range(3):
                logger.info(f"  {labels[i]}: {hmi_data[i]}")
            logger.info("... (15 more values)")
            return hmi_data
        else:
            logger.error(f"Not enough float values: got {len(rounded_float_values)}, need 18")
            return None
        
    except Exception as e:
        logger.error(f"Error reading Modbus data: {e}")
        logger.error(f"Exception details:", exc_info=True)  # This will log the full traceback
        return None
    finally:
        try:
            if client.is_open:
                client.close()
                logger.info("Closed Modbus connection")
        except:
            pass

def read_teledyne_data():
    """Read latest teledyne flow data"""
    global teledyne_reader
    
    if teledyne_reader is None:
        return None
        
    return teledyne_reader.get_latest_data()

def read_labjack_data():
    """Read latest labjack pressure data"""
    global labjack_reader
    
    if labjack_reader is None:
        return None
        
    return labjack_reader.get_latest_data()

def insert_hmi_data(data):
    """Insert HMI data into the hmi table"""
    if len(data) != 18:
        logger.error(f"Expected 18 HMI values, got {len(data)}")
        return False
        
    conn = sqlite3.connect(DATABASE_PATH)
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

def insert_teledyne_data(flow_data):
    """Insert Teledyne data into the flow_rates table"""
    if len(flow_data) != 3:
        logger.error(f"Expected 3 flow values, got {len(flow_data)}")
        return False
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO flow_rates (flow_1, flow_2, flow_3) VALUES (?, ?, ?)
        ''', flow_data)
        
        conn.commit()
        logger.info(f"Inserted Teledyne data: {flow_data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting Teledyne data: {e}")
        return False
    finally:
        conn.close()

def insert_labjack_data(pressure_data):
    """Insert LabJack data into the pressures table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO pressures (pressure_1) VALUES (?)
        ''', (pressure_data,))
        
        conn.commit()
        logger.info(f"Inserted LabJack data: {pressure_data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting LabJack data: {e}")
        return False
    finally:
        conn.close()

def pipeline_to_database(modbus_data, teledyne_data, labjack_data):
    """Pipeline data directly to the database"""
    success = True
    
    # Insert HMI/Modbus data
    if modbus_data is not None:
        if not insert_hmi_data(modbus_data):
            success = False
            logger.error("Failed to insert HMI data")
    
    # Insert Teledyne data
    if teledyne_data is not None:
        flow_1 = teledyne_data.get('flow_1')
        flow_2 = teledyne_data.get('flow_2')
        flow_3 = teledyne_data.get('flow_3')
        if all(v is not None for v in [flow_1, flow_2, flow_3]):
            if not insert_teledyne_data([flow_1, flow_2, flow_3]):
                success = False
                logger.error("Failed to insert Teledyne data")
        else:
            logger.warning("Missing required teledyne flow values")
    
    # Insert LabJack data
    if labjack_data is not None:
        pressure_1 = labjack_data.get('Pressure_1')
        if pressure_1 is not None:
            if not insert_labjack_data(pressure_1):
                success = False
                logger.error("Failed to insert LabJack data")
        else:
            logger.warning("Missing LabJack pressure value")
    
    return success

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
                header_row = ['timestamp'] + labels + teledyne_labels + Pressure_labels
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
    global teledyne_reader, labjack_reader
    
    logger.info("Starting Data Acquisition System with Direct Database Pipeline")
    logger.info(f"Database path: {DATABASE_PATH}")
    logger.info(f"Sleep interval: {SLEEP_INTERVAL} seconds")
    logger.info(f"Teledyne CSV path: {TELEDYNE_CSV_PATH}")
    logger.info(f"LabJack CSV path: {LABJACK_CSV_PATH}")
    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Setup database
    try:
        setup_database()
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        return
    
    # Start teledyne data reader
    try:
        teledyne_reader = TeledyneDataReader(TELEDYNE_CSV_PATH, TELEDYNE_CHECK_INTERVAL)
        teledyne_reader.start()
        logger.info("Teledyne data reader started")
    except Exception as e:
        logger.error(f"Error starting teledyne data reader: {e}")
    
    # Start labjack data reader
    try:
        labjack_reader = LabJackReader(LABJACK_CSV_PATH, LABJACK_CHECK_INTERVAL)
        labjack_reader.start()
        logger.info("LabJack data reader started")
    except Exception as e:
        logger.error(f"Error starting labjack data reader: {e}")
    
    consecutive_failures = 0
    max_consecutive_failures = MAX_CONSECUTIVE_FAILURES
    
    try:
        while True:
            try:
                # Read data from Modbus
                modbus_data = _read_HMI()
                
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

                # Read labjack data
                labjack_data = read_labjack_data()
                
                # Pipeline data directly to database
                db_success = pipeline_to_database(modbus_data, teledyne_data, labjack_data)
                
                if not db_success:
                    logger.warning("Some data failed to insert into database")
                
                # Create combined data for CSV backup
                combined_data = {
                    'timestamp': datetime.now().isoformat(),
                    'modbus_data': modbus_data,
                    'teledyne_data': teledyne_data,
                    'labjack_data': labjack_data
                }
                
                # Create CSV data for backup
                csv_data = modbus_data.copy()
                
                if teledyne_data:
                    csv_data.extend([
                        teledyne_data.get('Timestamp', ''),
                        teledyne_data.get('flow_1', ''),
                        teledyne_data.get('flow_2', ''),
                        teledyne_data.get('flow_3', '')
                    ])
                else:
                    csv_data.extend(['', '', '', ''])
                
                if labjack_data:
                    csv_data.extend([
                        labjack_data.get('Timestamp', ''),
                        labjack_data.get('Pressure_1', '')
                    ])
                else:
                    csv_data.extend(['', ''])
                
                # Always save locally as backup
                csv_success = save_to_local_csv(combined_data, csv_data)
                
                if not csv_success:
                    logger.warning("Failed to save CSV backup")
                
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

        if labjack_reader:
            labjack_reader.stop()
            logger.info("LabJack data reader stopped")

if __name__ == '__main__':
    main() 