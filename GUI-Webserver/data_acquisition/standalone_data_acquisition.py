#!/usr/bin/env python3
"""
Standalone Data Acquisition Script
This script runs on the machine connected to QT devices and pipelines data directly to the database.
Also reads from teledyne_flow.csv and labjack_pressure.csv in real-time.

Usage:
    python standalone_data_acquisition.py                    # Run with file logging only
    python standalone_data_acquisition.py --terminal-log     # Show logs in terminal
    python standalone_data_acquisition.py --verbose          # Enable verbose logging with file logging
    python standalone_data_acquisition.py --verbose --terminal-log  # Verbose mode with terminal output
"""

from pyModbusTCP.client import ModbusClient
import struct
import time
import csv
import json
import logging
from datetime import datetime, timezone
import os
import threading
import sqlite3
import argparse
import sys
import pytz

from _TeledyneReader import TeledyneDataReader
from _LabJackReader import LabJackReader_1, LabJackReader_2
from _LakeShoreReader import LakeShoreReader
from _MaxiGaugeReader import MaxiGaugeReader
from _IVCReader import IVCReader
from _QTReader import QTReader


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

def print_status_header():
    """Print a beautiful status header for the data acquisition system"""
    print("\n" + "="*80)
    print("🚀 UVA Lab Data Acquisition System")
    print("="*80)
    print("📊 Collecting data from multiple sources:")
    print("   • QT System")
    print("   • Teledyne Flow Meters")
    print("   • LabJack Pressure Sensors")
    print("   • LakeShore Temperature Controllers")
    print("   • MaxiGauge Pressure Gauges")
    print("   • IVC Pressure Gauge")
    print("="*80)
    print("💾 Data is being saved to database")
    print("📝 Logs are being written to data_acquisition.log")
    print("⏰ Started at:", get_current_est_time())
    print("="*80 + "\n")

def print_status_update(iteration, QT_status, teledyne_status, labjack_1_status, labjack_2_status, lakeshore_target_stick_status, lakeshore_fridge_temp_status, lakeshore_magnet_temp_status, maxigauge_status, ivc_status):
    """Print a beautiful status update"""
    status_symbols = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'none': '⏸️'
    }
    
    print(f"\r🔄 {iteration:4d} | "
          f"QT:{status_symbols.get(QT_status, '❓')} | "
          f"TDY:{status_symbols.get(teledyne_status, '❓')} | "
          f"LJ1:{status_symbols.get(labjack_1_status, '❓')} | "
          f"LJ2:{status_symbols.get(labjack_2_status, '❓')} | "
          f"LS-TS:{status_symbols.get(lakeshore_target_stick_status, '❓')} | "
          f"LS-FT:{status_symbols.get(lakeshore_fridge_temp_status, '❓')} | "
          f"LS-MT:{status_symbols.get(lakeshore_magnet_temp_status, '❓')} | "
          f"MG:{status_symbols.get(maxigauge_status, '❓')} | "
          f"IVC:{status_symbols.get(ivc_status, '❓')} | "
          f"{get_current_est_time()}", end='', flush=True)

def setup_logging(verbose=False, terminal_output=False):
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Determine log level
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    handlers = []
    
    # File handler for all logs
    file_handler = logging.FileHandler('logs/data_acquisition.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    handlers.append(file_handler)
    
    # Debug file handler if verbose
    if verbose:
        debug_handler = logging.FileHandler('logs/data_acquisition_debug.log')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(file_formatter)
        handlers.append(debug_handler)
    
    # Console handler if terminal output requested
    if terminal_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Set to lowest level to capture all
        handlers=handlers,
        force=True  # Override any existing configuration
    )

setup_logging(verbose=False, terminal_output=False)
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
    TELEDYNE_CHECK_INTERVAL = 10  # Check for new data every second
    LABJACK_CHECK_INTERVAL = 1  # Check for new data every second
    LAKESHORE_CHECK_INTERVAL = 1  # Check for new data every second
    MAXIGAUGE_CHECK_INTERVAL = 1  # Check for new data every second

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

# Global teledyne reader instance
teledyne_reader = None

# Global labjack reader instance
labjack_reader_1 = None
labjack_reader_2 = None

# Global lakeshore readers instance
lakeshore_reader_target_stick = None
lakeshore_reader_fridge_temp = None
lakeshore_reader_magnet_temp = None

# Global maxigauge reader instance
maxigauge_reader = None

# Global IVC reader instance
ivc_reader = None

# Global QT reader instance
qt_reader = None

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

def _read_QT():
    """Read data from QT TCP server using QTReader class"""
    global qt_reader
    
    if qt_reader is None:
        logger.error("QT reader not initialized")
        return None
        
    return qt_reader.read_qt_data()

def read_teledyne_data():
    """Read latest teledyne flow data"""
    global teledyne_reader
    
    # if teledyne_reader is None:
    #     return [None] * 3  # Return None for 3 flow values
        
    return teledyne_reader.get_latest_data()

def read_labjack_data():
    """Read latest labjack pressure data"""
    global labjack_reader_1
    
    if labjack_reader_1 is None:
        return [None] * 6  # Return None for 4 pressure values
        
    return labjack_reader_1.get_latest_data()

def read_labjack_data_2():
    """Read latest labjack pressure data"""
    global labjack_reader_2

    if labjack_reader_2 is None:
        return [None] * 2  # Return None for 2 pressure values
        
    return labjack_reader_2.get_latest_data()

def read_lakeshore_data_target_stick():
    """Read latest lakeshore data from target stick"""
    global lakeshore_reader_target_stick

    if lakeshore_reader_target_stick is None:
        return [None] * 8  # Return None for 8 lakeshore values
        
    
    return lakeshore_reader_target_stick.get_latest_data()

def read_lakeshore_data_fridge_temp():
    """Read latest lakeshore data from fridge temperature"""
    global lakeshore_reader_fridge_temp

    if lakeshore_reader_fridge_temp is None:
        return [None] * 8  # Return None for 8 lakeshore values
    
    return lakeshore_reader_fridge_temp.get_latest_data()

def read_lakeshore_data_magnet_temp():
    """Read latest lakeshore data from magnet temperature"""
    global lakeshore_reader_magnet_temp

    if lakeshore_reader_magnet_temp is None:
        return [None] * 8  # Return None for 8 lakeshore values
    
    return lakeshore_reader_magnet_temp.get_latest_data()

def read_maxigauge_data():
    """Read latest maxigauge data"""
    global maxigauge_reader

    if maxigauge_reader is None:
        return [None] * 6  # Return None for 6 maxigauge values
    
    return maxigauge_reader.get_latest_data()

def read_ivc_data():
    """Read latest IVC data"""
    global ivc_reader

    if ivc_reader is None:
        return None  # Return None for IVC value when reader is not available
    
    data = ivc_reader.get_latest_data()
    if data is not None and isinstance(data, (int, float)):
        return data
    else:
        return None

def insert_QT_data(data):
    """Insert QT data into the QT table"""
    if len(data) != 18:
        logger.error(f"Expected 18 QT values, got {len(data)}")
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
            INSERT INTO QT (
                fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                pt501_ai, pt502_ai, pt503_ai, pt504_ai,
                ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                ti504_ai, ti505_ai, ti523_ai, "Timestamp"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai, pt501_ai, pt502_ai, pt503_ai, pt504_ai, ait501_ai, ti501_ai, ti502_ai, ti503_ai, ti504_ai, ti505_ai, ti523_ai, get_current_est_time()))
        
        conn.commit()
        logger.debug(f"Inserted QT data: {data[:3]}...")
        return True
    except Exception as e:
        logger.error(f"Error inserting QT data: {e}")
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
        logger.debug(f"Inserted Teledyne data: {flow_data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting Teledyne data: {e}")
        return False
    finally:
        conn.close()

def insert_flow_data_combined(teledyne_data=None, labjack_2_data=None):
    """
    Insert flow data from both Teledyne and LabJack 2 sources into the Flow_Rates table.
    This function handles the coordination between the two data sources.
    
    Args:
        teledyne_data (list): [seperator_flow, magnet_flow, main_flow] or None
        labjack_2_data (list): [flow_meter_1, flow_meter_2] or None
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Prepare the data for insertion
        seperator_flow = teledyne_data[0] if teledyne_data and len(teledyne_data) >= 1 else None
        magnet_flow = teledyne_data[1] if teledyne_data and len(teledyne_data) >= 2 else None
        main_flow = teledyne_data[2] if teledyne_data and len(teledyne_data) >= 3 else None
        flow_meter_1 = labjack_2_data[0] if labjack_2_data and len(labjack_2_data) >= 1 else None
        flow_meter_2 = labjack_2_data[1] if labjack_2_data and len(labjack_2_data) >= 2 else None
        
        cursor.execute('''
            INSERT INTO Flow_Rates (
                seperator_flow, magnet_flow, main_flow, 
                microwave_flow_meter, heat_exchanger_flow_meter, "Timestamp"
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (seperator_flow, magnet_flow, main_flow, flow_meter_1, flow_meter_2, get_current_est_time()))
        
        conn.commit()
        logger.debug(f"Inserted combined flow data - Teledyne: {teledyne_data}, LabJack2: {labjack_2_data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting combined flow data: {e}")
        return False
    finally:
        conn.close()

def insert_labjack_1_data(pressure_data):
    """Insert LabJack data into the pressures table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Labjack (root_exhaust_pressure, buffer_pressure, magnet_pressure, purifier_inlet_pressure, fridge_vapor_pressure, thermocouple, "Timestamp") 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (pressure_data[0], pressure_data[1], pressure_data[2], pressure_data[3], pressure_data[4], pressure_data[5], get_current_est_time()))
        
        conn.commit()
        logger.debug(f"Inserted LabJack data: {pressure_data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting LabJack data: {e}")
        return False
    finally:
        conn.close()

def insert_labjack_2_data(flow_data):
    """Insert LabJack 2 data into the Flow_Rates table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert LabJack 2 flow meter data into the Flow_Rates table
        # This will create a new row with flow_meter_1 and flow_meter_2 values
        cursor.execute('''
            INSERT INTO Flow_Rates (microwave_flow_meter, heat_exchanger_flow_meter, "Timestamp") 
            VALUES (?, ?, ?)
        ''', (flow_data[0], flow_data[1], get_current_est_time()))
        
        conn.commit()
        logger.debug(f"Inserted LabJack 2 data into Flow_Rates: {flow_data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting LabJack 2 data: {e}")
        return False
    finally:
        conn.close()

def insert_lakeshore_data_target_stick(data):
    """Insert Lakeshore data into the lakeshore_target_stick table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Lakeshore_Target_Stick (
                "target_stick_buffle_top_temperature",
                "target_stick_buffle_bottom_temperature",
                "target_stick_seperator_top_temperature",
                "target_stick_seperator_bottom_temperature",
                "target_stick_heat_exchanger_top_temperature",
                "target_stick_heat_exchanger_bottom_temperature",
                "target_stick_annealing_plate_bar_temperature",
                "target_stick_annealing_plate_top_temperature",
                "Timestamp"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], get_current_est_time()))
        
        conn.commit()
        logger.debug(f"Inserted Target Stick Lakeshore data: {data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting Target Stick Lakeshore data: {e}")
        return False
    finally:
        conn.close()

def insert_lakeshore_data_fridge_temp(data):
    """Insert Lakeshore data into the lakeshore_fridge_temp table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Lakeshore_Fridge_Temp (
                "fridge_target_top_up_temperature",
                "fridge_target_top_up_center_temperature",
                "fridge_target_top_down_temperature",
                "fridge_target_bottom_up_temperature",
                "fridge_target_bottom_up_center_temperature",
                "fridge_target_bottom_down_temperature",
                "fridge_target_top_cernox_temperature",
                "fridge_target_bottom_cernox_temperature",
                "Timestamp"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], get_current_est_time()))

        conn.commit()
        logger.debug(f"Inserted Fridge Lakeshore data: {data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting Fridge Lakeshore data: {e}")
        return False
    finally:
        conn.close()

def insert_lakeshore_data_magnet_temp(data):
    """Insert Lakeshore data into the lakeshore_magnet_temp table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Lakeshore_Magnet_Temp (
                "magnet_channel_1",
                "magnet_channel_2",
                "magnet_channel_3",
                "magnet_channel_4",
                "magnet_channel_5",
                "magnet_channel_6",
                "magnet_channel_7",
                "magnet_channel_8",
                "Timestamp"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], get_current_est_time()))
        
        conn.commit()
        logger.debug(f"Inserted Magnet Lakeshore data: {data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting Magnet Lakeshore data: {e}")
        return False
    finally:
        conn.close()

def insert_maxigauge_data(data):
    """Insert MaxiGauge data into the maxigauge table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO MaxiGauge (
                "maxigauge_seperator_inlet_pressure",
                "maxigauge_upper_roots_pressure",
                "channel_3",
                "channel_4",
                "channel_5",
                "channel_6",
                "Timestamp"
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data[0], data[1], data[2], data[3], data[4], data[5], get_current_est_time()))

        conn.commit()
        logger.debug(f"Inserted MaxiGauge data: {data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting MaxiGauge data: {e}")
        return False
    finally:
        conn.close()

def insert_ivc_data(data):
    """Insert IVC data into the ivc table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO IVC (
                "ivc_pressure",
                "Timestamp"
            ) VALUES (?, ?)
        ''', (data, get_current_est_time()))
        
        conn.commit()
        logger.debug(f"Inserted IVC data: {data}")
        return True
    except Exception as e:
        logger.error(f"Error inserting IVC data: {e}")
        return False
    finally:
        conn.close()

def pipeline_to_database(QT_data, teledyne_data, labjack_data_1, labjack_data_2, lakeshore_data_target_stick, lakeshore_data_fridge_temp, lakeshore_data_magnet_temp, maxigauge_data, ivc_data):
    """Pipeline data directly to the database"""
    # Initialize all statuses to 'none' - each data source is independent
    QT_status = 'none'
    teledyne_status = 'none'
    labjack_1_status = 'none'
    labjack_2_status = 'none'
    lakeshore_target_stick_status = 'none'
    lakeshore_fridge_temp_status = 'none'
    lakeshore_magnet_temp_status = 'none'
    maxigauge_status = 'none'
    ivc_status = 'none'
    
    # Insert QT data
    logger.debug("Attempting to insert QT data")
    if QT_data is not None:
        if insert_QT_data(QT_data):
            QT_status = 'success'
            logger.debug("Successfully inserted QT data")
        else:
            QT_status = 'error'
            logger.error("Failed to insert QT data")
    else:
        logger.debug("No QT data available - QT connection may be down")
    
    # Insert LabJack 1 data (pressure data)
    logger.debug("Attempting to insert LabJack 1 data")
    if labjack_data_1 is not None and len(labjack_data_1) >= 6:
        root_exhaust_pressure = labjack_data_1[0]
        buffer_pressure = labjack_data_1[1]
        magnet_pressure = labjack_data_1[2]
        purifier_inlet_pressure = labjack_data_1[3]
        fridge_vapor_pressure = labjack_data_1[4]
        thermocouple = labjack_data_1[5]
        logger.debug(f"LabJack 1 data: {labjack_data_1}")
        if insert_labjack_1_data([root_exhaust_pressure, buffer_pressure, magnet_pressure, purifier_inlet_pressure, fridge_vapor_pressure, thermocouple]):
            labjack_1_status = 'success'
            logger.debug("Successfully inserted LabJack 1 data")
        else:
            labjack_1_status = 'error'
            logger.error("Failed to insert LabJack 1 data")
    else:
        logger.debug("No LabJack 1 data available or insufficient data points")

    # Handle Teledyne and LabJack 2 flow data separately for better status tracking
    logger.debug("Attempting to insert Teledyne flow data")
    if teledyne_data is not None and any(v is not None for v in teledyne_data[:3]):
        if insert_teledyne_data(teledyne_data):
            teledyne_status = 'success'
            logger.debug("Successfully inserted Teledyne data")
        else:
            teledyne_status = 'error'
            logger.error("Failed to insert Teledyne data")
    else:
        logger.debug("No Teledyne data available")

    logger.debug("Attempting to insert LabJack 2 flow data")
    if labjack_data_2 is not None and len(labjack_data_2) >= 2:
        if insert_labjack_2_data(labjack_data_2):
            labjack_2_status = 'success'
            logger.debug("Successfully inserted LabJack 2 data")
        else:
            labjack_2_status = 'error'
            logger.error("Failed to insert LabJack 2 data")
    else:
        logger.debug("No LabJack 2 data available")

    # Insert Lakeshore Target Stick data
    logger.debug("Attempting to insert Target Stick Data")
    if lakeshore_data_target_stick is not None:
        if insert_lakeshore_data_target_stick(lakeshore_data_target_stick):
            lakeshore_target_stick_status = 'success'
            logger.debug("Successfully inserted Target Stick data")
        else:
            lakeshore_target_stick_status = 'error'
            logger.error("Failed to insert Target Stick Data")
    else:
        logger.debug("No Target Stick data available")

    # Insert Lakeshore Fridge Temp data
    logger.debug("Attempting to insert Fridge Temp Data")
    if lakeshore_data_fridge_temp is not None:
        if insert_lakeshore_data_fridge_temp(lakeshore_data_fridge_temp):
            lakeshore_fridge_temp_status = 'success'
            logger.debug("Successfully inserted Fridge Temp data")
        else:
            lakeshore_fridge_temp_status = 'error'
            logger.error("Failed to insert Fridge Temp Data")
    else:
        logger.debug("No Fridge Temp data available")

    # Insert Lakeshore Magnet Temp data
    logger.debug("Attempting to insert Magnet Temp Data")
    if lakeshore_data_magnet_temp is not None:
        if insert_lakeshore_data_magnet_temp(lakeshore_data_magnet_temp):
            lakeshore_magnet_temp_status = 'success'
            logger.debug("Successfully inserted Magnet Temp data")
        else:
            lakeshore_magnet_temp_status = 'error'
            logger.error("Failed to insert Magnet Temp Data")
    else:
        logger.debug("No Magnet Temp data available")

    # Insert MaxiGauge data
    logger.debug("Attempting to insert MaxiGauge data")
    if maxigauge_data is not None:
        if isinstance(maxigauge_data, list) and len(maxigauge_data) == 6:
            logger.debug(f"MaxiGauge data: {maxigauge_data}")
            if insert_maxigauge_data(maxigauge_data):
                maxigauge_status = 'success'
                logger.debug("Successfully inserted MaxiGauge data")
            else:
                maxigauge_status = 'error'
                logger.error("Failed to insert MaxiGauge data")
        else:
            maxigauge_status = 'error'
            logger.error(f"MaxiGauge data has invalid format - expected list of 6 values, got: {type(maxigauge_data)} with value: {maxigauge_data}")
    else:
        logger.debug("No MaxiGauge data available")

    # Insert IVC data
    logger.debug("Attempting to insert IVC data")
    if ivc_data is not None:
        if isinstance(ivc_data, (int, float)):
            logger.debug(f"IVC data: {ivc_data}")
            if insert_ivc_data(ivc_data):
                ivc_status = 'success'
                logger.debug("Successfully inserted IVC data")
            else:
                ivc_status = 'error'
                logger.error("Failed to insert IVC data")
        else:
            ivc_status = 'error'
            logger.error(f"IVC data has invalid format - expected numeric value, got: {type(ivc_data)} with value: {ivc_data}")
    else:
        logger.debug("No IVC data available")

    # Calculate overall success based on whether any data was successfully inserted
    successful_inserts = sum(1 for status in [QT_status, teledyne_status, labjack_1_status, labjack_2_status, 
                                             lakeshore_target_stick_status, lakeshore_fridge_temp_status, 
                                             lakeshore_magnet_temp_status, maxigauge_status, ivc_status] 
                           if status == 'success')
    
    overall_success = successful_inserts > 0

    return overall_success, QT_status, teledyne_status, labjack_1_status, labjack_2_status, lakeshore_target_stick_status, lakeshore_fridge_temp_status, lakeshore_magnet_temp_status, maxigauge_status, ivc_status


def main():
    """Main data acquisition loop"""
    global args
    parser = argparse.ArgumentParser(description='Data Acquisition System')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--terminal-log', action='store_true', help='Show log output in terminal')
    args = parser.parse_args()

    # Setup logging with terminal output if requested
    setup_logging(verbose=args.verbose, terminal_output=args.terminal_log)

    global teledyne_reader, labjack_reader_1, labjack_reader_2, maxigauge_reader, lakeshore_reader_target_stick, lakeshore_reader_fridge_temp, lakeshore_reader_magnet_temp, ivc_reader, qt_reader

    # Print beautiful header if not in verbose mode
    if not args.verbose and not args.terminal_log:
        print_status_header()

    logger.info("Starting Data Acquisition System with Direct Database Pipeline")
    if args.verbose:
        logger.info("VERBOSE: Verbose mode enabled")
        logger.info(f"VERBOSE: Database path: {DATABASE_PATH}")
        logger.info(f"VERBOSE: Sleep interval: {SLEEP_INTERVAL} seconds")
        logger.info(f"VERBOSE: PLC IP: {PLC_IP}")
        logger.info(f"VERBOSE: Unit ID: {UNIT_ID}")
        logger.info(f"VERBOSE: Integer Port: {INT_PORT}")
        logger.info(f"VERBOSE: Float Port: {FLOAT_PORT}")
        logger.info(f"VERBOSE: Number of registers to read: {NUM_REG_TO_READ}")
        logger.info(f"VERBOSE: Labels: {labels}")
        logger.info(f"VERBOSE: Max consecutive failures: {MAX_CONSECUTIVE_FAILURES}")
    
    # Setup database
    logger.info("Setting up database")
    try:
        setup_database()
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        return
    
    # Initialize QT reader
    try:
        qt_reader = QTReader(
            plc_ip=PLC_IP,
            unit_id=UNIT_ID,
            int_port=INT_PORT,
            float_port=FLOAT_PORT,
            num_reg_to_read=NUM_REG_TO_READ,
            labels=labels
        )
        logger.info("QT reader initialized")
    except Exception as e:
        logger.error(f"Error initializing QT reader: {e}")
    
    try:
        teledyne_reader = TeledyneDataReader(TELEDYNE_CHECK_INTERVAL)
        teledyne_reader.start()
        logger.info("Teledyne data reader started")
    except Exception as e:
        logger.error(f"Error starting teledyne data reader: {e}")
    
    # Start labjack data reader
    try:
        labjack_reader_1 = LabJackReader_1(LABJACK_CHECK_INTERVAL)
        labjack_reader_1.start()
        logger.info("LabJack data reader started")

        labjack_reader_2 = LabJackReader_2(LABJACK_CHECK_INTERVAL)
        labjack_reader_2.start()
        logger.info("LabJack data reader started")
    except Exception as e:
        logger.error(f"Error starting labjack data reader: {e}")
    
    # Start lakeshore data readers  

    try:
        lakeshore_reader_target_stick = LakeShoreReader(port="COM4")
        lakeshore_reader_target_stick.start()
        logger.info("Lakeshore data reader started for target stick")
    except Exception as e:
        logger.error(f"Error starting lakeshore data reader: {e}")

    try:
        lakeshore_reader_fridge_temp = LakeShoreReader(port="COM5")
        lakeshore_reader_fridge_temp.start()
        logger.info("Lakeshore data reader started for fridge temp")
    except Exception as e:
        logger.error(f"Error starting lakeshore data reader: {e}")

    try:
        lakeshore_reader_magnet_temp = LakeShoreReader(port="COM6")
        lakeshore_reader_magnet_temp.start()
        logger.info("Lakeshore data reader started for magnet temp")
    except Exception as e:
        logger.error(f"Error starting lakeshore data reader: {e}")

    try:
        maxigauge_reader = MaxiGaugeReader()
        maxigauge_reader.start()
        logger.info("MaxiGauge data reader started")
    except Exception as e:
        logger.error(f"Error starting maxigauge data reader: {e}")

    try:
        ivc_reader = IVCReader(port="COM7")
        ivc_reader.start()
        logger.info("IVC data reader started")
    except Exception as e:
        logger.error(f"Error starting ivc data reader: {e}")

    iteration = 0
    
    try:
        while True:
            try:
                iteration += 1
                
                # Read data from QT()
                QT_data = _read_QT()
                
                if QT_data is None:
                    logger.warning(f"Failed to read QT data. Continuing with other data sources (Teledyne, LabJack, LakeShore, MaxiGauge, IVC)...")
                
                # Read teledyne data
                teledyne_data = read_teledyne_data()

                # Read labjack data
                labjack_data_1 = read_labjack_data()
                labjack_data_2 = read_labjack_data_2()
                
                # Read lakeshore data
                lakeshore_data_target_stick = read_lakeshore_data_target_stick()
                
                lakeshore_data_fridge_temp = read_lakeshore_data_fridge_temp()
                
                lakeshore_data_magnet_temp = read_lakeshore_data_magnet_temp()
                
                # Read maxigauge data
                maxigauge_data = read_maxigauge_data()

                # Read ivc data
                ivc_data = read_ivc_data()

                # Pipeline data directly to database
                db_success, QT_status, teledyne_status, labjack_1_status, labjack_2_status, lakeshore_target_stick_status, lakeshore_fridge_temp_status, lakeshore_magnet_temp_status, maxigauge_status, ivc_status = pipeline_to_database(
                    QT_data, 
                    teledyne_data, 
                    labjack_data_1, 
                    labjack_data_2, 
                    lakeshore_data_target_stick, 
                    lakeshore_data_fridge_temp, 
                    lakeshore_data_magnet_temp, 
                    maxigauge_data,
                    ivc_data
                )
                
                # Print status update if not in verbose mode
                if not args.verbose and not args.terminal_log:
                    print_status_update(iteration, 
                                        QT_status, 
                                        teledyne_status, 
                                        labjack_1_status, 
                                        labjack_2_status, 
                                        lakeshore_target_stick_status, 
                                        lakeshore_fridge_temp_status, 
                                        lakeshore_magnet_temp_status, 
                                        maxigauge_status, ivc_status)
                
                if not db_success:
                    logger.warning("Some data failed to insert into database")
                
                # Log data source status summary for monitoring
                success_count = sum(1 for status in [QT_status, teledyne_status, labjack_1_status, labjack_2_status, 
                                                   lakeshore_target_stick_status, lakeshore_fridge_temp_status, 
                                                   lakeshore_magnet_temp_status, maxigauge_status, ivc_status] 
                                  if status == 'success')
                total_sources = 8
                logger.info(f"Data collection cycle {iteration}: {success_count}/{total_sources} sources active - "
                           f"QT:{QT_status}, Teledyne:{teledyne_status}, LabJack_1:{labjack_1_status}, LabJack_2:{labjack_2_status}, "
                           f"LakeShore-TS:{lakeshore_target_stick_status}, LakeShore-FT:{lakeshore_fridge_temp_status}, "
                           f"LakeShore-MT:{lakeshore_magnet_temp_status}, MaxiGauge:{maxigauge_status}, IVC:{ivc_status}")
                
                # Wait before next reading
                time.sleep(SLEEP_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Data acquisition stopped by user")
                if not args.verbose and not args.terminal_log:
                    print("\n\n🛑 Data acquisition stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                if not args.verbose and not args.terminal_log:
                    print_status_update(iteration, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error')
                time.sleep(SLEEP_INTERVAL)
                
    finally:
        logger.info("Cleaning up data acquisition system")

        if teledyne_reader:
            teledyne_reader.stop()
            logger.info("Teledyne data reader stopped")

        if labjack_reader_1:
            labjack_reader_1.stop()
            logger.info("LabJack data reader stopped")

        if labjack_reader_2:
            labjack_reader_2.stop()
            logger.info("LabJack data reader stopped")
        
        if maxigauge_reader:
            maxigauge_reader.stop()
            logger.info("MaxiGauge data reader stopped")

        if lakeshore_reader_target_stick:
            lakeshore_reader_target_stick.stop()
            logger.info("Lakeshore data reader stopped")

        if lakeshore_reader_fridge_temp:
            lakeshore_reader_fridge_temp.stop()
            logger.info("Lakeshore data reader stopped")

        if lakeshore_reader_magnet_temp:
            lakeshore_reader_magnet_temp.stop()
            logger.info("Lakeshore data reader stopped")

        if ivc_reader:
            ivc_reader.stop()
            logger.info("IVC data reader stopped")

        if qt_reader:
            qt_reader.close_connections()
            logger.info("QT reader connections closed")

        if not args.verbose and not args.terminal_log:
            print("\n\n✅ Data acquisition system shutdown complete")

if __name__ == '__main__':
    main() 