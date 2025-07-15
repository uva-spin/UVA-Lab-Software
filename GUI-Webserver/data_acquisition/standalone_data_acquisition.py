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
from datetime import datetime, timezone
import os
import threading
import sqlite3
from _TeledyneReader import TeledyneDataReader
from _LabJackReader import LabJackReader
import pytz
import argparse

# Global args variable for command line arguments
args = None

# Configure timezone
EST = pytz.timezone('America/New_York')

def get_current_est_time():
    """Get current time in EST timezone"""
    now = datetime.now(EST)
    return now.strftime('%Y-%m-%d %H:%M:%S')

def utc_to_est_str(utc_dt):
    """Convert UTC datetime to EST string format"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    est_dt = utc_dt.astimezone(EST)
    return est_dt.strftime('%Y-%m-%d %H:%M:%S')

logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for even more detail
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
    NUM_REG_TO_READ = 36

    LOG_LEVEL = "INFO"
    LOG_FILE = "data_acquisition.log"
    TWIST_PATH = "//twist.phys.virginia.edu/www/spin"  
    DATABASE_DIR = f"{TWIST_PATH}/instance"
    TELEDYNE_CHECK_INTERVAL = 1  # Check for new data every second
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
    "Seperator_Flow",
    "Magnet_Flow", 
    "Main_Flow"
]

Pressure_labels = [
    "Root_Exhaust_Pressure",
    "Buffer_Pressure",
    "Magnet_Pressure",
    "Purifier_Inlet_Pressure",
    "Fridge_Vapor_Pressure"
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
        # Read integer values
        logger.info("Reading integer values")
        client = ModbusClient(host=plc_ip, port=int_port, unit_id=unit_id, auto_open=True, auto_close=False)
        int_regs = client.read_holding_registers(0, num_reg_to_read)
        if int_regs:
            int_values = utils.get_list_2comp(int_regs, 16)
            logger.info(f'Successfully read integer values: {int_values[:3]}... ({len(int_values)} values)')
        else:
            logger.warning(f"Failed to read integer registers from {plc_ip}:{int_port}")

        # Read float values
        logger.info("Reading float values")
        client = ModbusClient(host=plc_ip, port=float_port, unit_id=unit_id, auto_open=True, auto_close=False)
        float_regs = client.read_holding_registers(0, num_reg_to_read)
        
        if not float_regs:
            logger.error(f"Failed to read float registers from {plc_ip}:{float_port}")
            return None
            
        logger.info(f"Successfully read {len(float_regs)} float registers")
            
        float_values = []
        logger.info("Converting register pairs to float values...")
        for i in range(0, num_reg_to_read - 1, 2):
            raw = struct.pack(">HH", float_regs[i], float_regs[i + 1])  # Big Endian format
            float_values.append(struct.unpack(">f", raw)[0])  # Convert to float
        
        # Round float values to 2 decimal places
        rounded_float_values = [round(value, 2) for value in float_values]
        logger.info(f"Processed {len(rounded_float_values)} float values")
        
        # Log each value with its corresponding label
        if args.debug:
            for label, value in zip(labels, rounded_float_values[:18]):
                logger.debug(f"{label}: {value}")
        
        # Ensure we have exactly 18 values for HMI data
        if len(rounded_float_values) >= 18:
            hmi_data = rounded_float_values[:18]
            logger.info("Successfully read all HMI data")
            if args.debug:
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
        if args.debug:
            logger.error(f"Exception details:", exc_info=True)  # This will log the full traceback
        return None
    finally:
        try:
            if not client or not client.is_open:
                client.close()
                logger.info("Closed Modbus connection")
        except:
            pass

def read_teledyne_data():
    """Read latest teledyne flow data"""
    global teledyne_reader
    
    # if teledyne_reader is None:
    #     return [None] * 3  # Return None for 3 flow values
        
    return teledyne_reader.get_latest_data()

def read_labjack_data():
    """Read latest labjack pressure data"""
    global labjack_reader
    
    if labjack_reader is None:
        return [None] * 5  # Return None for 4 pressure values
        
    return labjack_reader.get_latest_data()

def insert_hmi_data(data):
    """Insert HMI data into the hmi table"""
    if len(data) != 18:
        logger.error(f"Expected 18 HMI values, got {len(data)}")
        return False
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    fc501_ai = data[0]
    fc501_out = data[1]
    fc502_ai = data[2]
    fc502_out = data[3]
    lit501_ai = data[4]
    pt501_ai = data[5]
    pt502_ai = data[6]
    pt503_ai = data[7]
    pt504_ai = data[8]
    ait501_ai = data[11]
    ti501_ai = data[12]
    ti502_ai = data[13]
    ti503_ai = data[14]
    ti504_ai = data[15]
    ti505_ai = data[16]
    ti523_ai = data[17]

    # Exclue pruity upstream and downstream
    
    try:
        cursor.execute('''
            INSERT INTO HMI (
                fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                pt501_ai, pt502_ai, pt503_ai, pt504_ai,
                ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                ti504_ai, ti505_ai, ti523_ai, "Timestamp"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data + [get_current_est_time()])
        
        conn.commit()
        if args.debug:
            logger.info(f"DEBUG: Inserted HMI data: {data[:3]}...")
        return True
    except Exception as e:
        logger.error(f"Error inserting HMI data: {e}")
        return False
    finally:
        conn.close()

def insert_teledyne_data(flow_data):
    """Insert Teledyne data into the flow_rates table"""
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Flow_Rates (seperator_flow, magnet_flow, main_flow, "Timestamp") 
            VALUES (?, ?, ?, ?)
        ''', flow_data + [get_current_est_time()])
        
        conn.commit()
        if args.debug:
            logger.info(f"DEBUG: Inserted Teledyne data: {flow_data}")
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
            INSERT INTO Pressures (root_exhaust_pressure, buffer_pressure, magnet_pressure, purifier_inlet_pressure, fridge_vapor_pressure, "Timestamp") 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pressure_data[0], pressure_data[1], pressure_data[2], pressure_data[3], pressure_data[4], get_current_est_time()))
        
        conn.commit()
        if args.debug:
            logger.info(f"DEBUG: Inserted LabJack data: {pressure_data}")
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
    if args.debug:
        print("DEBUG: Attempting to insert HMI data")
    if modbus_data is not None:
        insert_hmi_data(modbus_data)
        # if not insert_hmi_data(modbus_data):
        #     success = False
        success = True
        # logger.info("DEBUG: Successfully inserted HMI data")
    else:
        success = False
        logger.error("Failed to insert HMI data")
    
    # Insert Teledyne data
    if args.debug:
        print("DEBUG: Attempting to insert Teledyne data")
    if teledyne_data is not None:
        seperator_flow = teledyne_data[0]
        magnet_flow = teledyne_data[1]
        main_flow = teledyne_data[2]
        if any(v is not None for v in [seperator_flow, magnet_flow, main_flow]):
            if not insert_teledyne_data([seperator_flow, magnet_flow, main_flow]):
                success = False
                logger.error("Failed to insert Teledyne data")
        else:
            logger.warning("Missing required teledyne flow values. Inserting None values instead...")
            seperator_flow = magnet_flow = main_flow = None
            insert_teledyne_data([seperator_flow, magnet_flow, main_flow])
    else:
        if args.debug:
            print("DEBUG: Successfully inserted Teledyne data")
            
    
    # Insert LabJack data
    if args.debug:
        print("DEBUG: Attempting to insert LabJack data")
    if labjack_data is not None:
        root_exhaust_pressure = labjack_data[0]
        buffer_pressure = labjack_data[1]
        magnet_pressure = labjack_data[2]
        purifier_inlet_pressure = labjack_data[3]
        fridge_vapor_pressure = labjack_data[4]
        if args.debug:
            print(f"DEBUG:Pressure 1: {root_exhaust_pressure}, Pressure 2: {buffer_pressure}, Pressure 3: {magnet_pressure}, Pressure 4: {purifier_inlet_pressure}, Pressure 5: {fridge_vapor_pressure}")
        insert_labjack_data([root_exhaust_pressure, buffer_pressure, magnet_pressure, purifier_inlet_pressure, fridge_vapor_pressure])
        success = True
    else:
        success = False
        logger.error("Failed to insert LabJack data")
    
    return success


def main():
    """Main data acquisition loop"""
    global args
    parser = argparse.ArgumentParser(description='Data Acquisition System')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    global teledyne_reader, labjack_reader

    if args.debug:
        debug_handler = logging.FileHandler('data_acquisition_debug.log')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'))
        logger.addHandler(debug_handler)

    if args.debug:
        logger.info("Starting Data Acquisition System with Direct Database Pipeline")
        logger.info("DEBUG: Debug mode enabled")
        logger.info(f"DEBUG: Database path: {DATABASE_PATH}")
        logger.info(f"DEBUG: Sleep interval: {SLEEP_INTERVAL} seconds")
        logger.info(f"DEBUG: PLC IP: {PLC_IP}")
        logger.info(f"DEBUG: Unit ID: {UNIT_ID}")
        logger.info(f"DEBUG: Integer Port: {INT_PORT}")
        logger.info(f"DEBUG: Float Port: {FLOAT_PORT}")
        logger.info(f"DEBUG: Number of registers to read: {NUM_REG_TO_READ}")
        logger.info(f"DEBUG: Labels: {labels}")
        logger.info(f"DEBUG: Teledyne labels: {teledyne_labels}")
        logger.info(f"DEBUG: Pressure labels: {Pressure_labels}")
        logger.info(f"DEBUG: Max consecutive failures: {MAX_CONSECUTIVE_FAILURES}")

    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Setup database
    if args.debug:
        logger.info("DEBUG: Setting up database")
    try:
        setup_database()
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        return
    
    # Start teledyne data reader
    try:
        teledyne_reader = TeledyneDataReader(TELEDYNE_CHECK_INTERVAL)
        teledyne_reader.start()
        if args.debug:
            logger.info("DEBUG: Teledyne data reader started")
    except Exception as e:
        logger.error(f"Error starting teledyne data reader: {e}")
    
    # Start labjack data reader
    try:
        labjack_reader = LabJackReader(LABJACK_CHECK_INTERVAL)
        labjack_reader.start()
        if args.debug:
            logger.info("DEBUG: LabJack data reader started")
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
                    logger.warning("Some data failed to insert into database \n")
                
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