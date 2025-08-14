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

import logging
from datetime import datetime, timezone
import os
import argparse
import sys
import pytz
import asyncio
import aiomysql
import signal
from concurrent.futures import ThreadPoolExecutor

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

# Thread pool executor for blocking operations
executor = ThreadPoolExecutor(max_workers=10)

# Global shutdown flag
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def get_database_connection():
    """Get a database connection to MariaDB"""
    return await aiomysql.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        db=DATABASE_NAME,
        autocommit=True
    )

async def get_current_est_time():
    """Get current time in EST timezone"""
    now = datetime.now(EST)
    return now.strftime('%Y-%m-%d %H:%M:%S')

async def utc_to_est_str(utc_dt):
    """Convert UTC datetime to EST string format"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    est_dt = utc_dt.astimezone(EST)
    return est_dt.strftime('%Y-%m-%d %H:%M:%S')

async def print_status_header():
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
    print("⏰ Started at:", await get_current_est_time())
    print("="*80 + "\n")

async def print_status_update(iteration, QT_status, teledyne_status, labjack_1_status, labjack_2_status, lakeshore_target_stick_status, lakeshore_fridge_temp_status, lakeshore_magnet_temp_status, maxigauge_status, ivc_status):
    """Print a beautiful status update"""
    status_symbols = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'none': '⏸️'
    }
    
    current_time = await get_current_est_time()
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
          f"{current_time}", end='', flush=True)

async def setup_logging(verbose=False, terminal_output=False):
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
    
    handlers = []
    
    file_handler = logging.FileHandler('logs/data_acquisition.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    handlers.append(file_handler)
    
    if verbose:
        debug_handler = logging.FileHandler('logs/data_acquisition_debug.log')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(file_formatter)
        handlers.append(debug_handler)
    
    if terminal_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)
    
    logging.basicConfig(
        level=logging.DEBUG,  # Set to lowest level to capture all
        handlers=handlers,
        force=True  # Override any existing configuration
    )

setup_logging(verbose=False, terminal_output=False)
logger = logging.getLogger(__name__)

from config import *

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

async def ensure_database_directory():
    """Ensure the database directory exists (for local file storage, not needed for MariaDB)"""
    # This function is no longer needed for MariaDB, but kept for compatibility
    pass

async def setup_database():
    """Initialize the database connection and verify connectivity"""
    try:

        async with await get_database_connection() as conn:

            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                if result and result[0] == 1:
                    logger.info(f"Successfully connected to MariaDB at {DATABASE_HOST}:{DATABASE_PORT}")
                    logger.info(f"Database: {DATABASE_NAME}")
                else:
                    raise Exception("Database connectivity test failed")
            

            logger.info("Database setup completed - connectivity verified")
            
    except Exception as e:
        logger.error(f"Database setup error: {e}")
        logger.error("Please check your MariaDB connection parameters:")
        logger.error(f"  Host: {DATABASE_HOST}")
        logger.error(f"  Port: {DATABASE_PORT}")
        logger.error(f"  User: {DATABASE_USER}")
        logger.error(f"  Database: {DATABASE_NAME}")
        raise

async def _read_QT():
    """Read data from QT TCP server using QTReader class"""
    global qt_reader
    
    if qt_reader is None:
        logger.error("QT reader not initialized")
        return None
    
    # Run blocking QT read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, qt_reader.read_qt_data)

async def read_teledyne_data():
    """Read latest teledyne flow data"""
    global teledyne_reader
    
    if teledyne_reader is None:
        return [None] * 3  # Return None for 3 flow values
    
    # Run blocking teledyne read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, teledyne_reader.get_latest_data)

async def read_labjack_data_1():
    """Read latest labjack pressure data"""
    global labjack_reader_1
    
    if labjack_reader_1 is None:
        return [None] * 6  # Return None for 6 pressure values
    
    # Run blocking labjack read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, labjack_reader_1.get_latest_data)

async def read_labjack_data_2():
    """Read latest labjack pressure data"""
    global labjack_reader_2

    if labjack_reader_2 is None:
        return [None] * 4  # Return None for 4 pressure values
    
    # Run blocking labjack read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, labjack_reader_2.get_latest_data)

async def read_lakeshore_data_target_stick():
    """Read latest lakeshore data from target stick"""
    global lakeshore_reader_target_stick

    if lakeshore_reader_target_stick is None:
        return [None] * 8  # Return None for 8 lakeshore values
    
    # Run blocking lakeshore read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lakeshore_reader_target_stick.get_latest_data)

async def read_lakeshore_data_fridge_temp():
    """Read latest lakeshore data from fridge temperature"""
    global lakeshore_reader_fridge_temp

    if lakeshore_reader_fridge_temp is None:
        return [None] * 8  # Return None for 8 lakeshore values
    
    # Run blocking lakeshore read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lakeshore_reader_fridge_temp.get_latest_data)

async def read_lakeshore_data_magnet_temp():
    """Read latest lakeshore data from magnet temperature"""
    global lakeshore_reader_magnet_temp

    if lakeshore_reader_magnet_temp is None:
        return [None] * 8  # Return None for 8 lakeshore values
    
    # Run blocking lakeshore read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lakeshore_reader_magnet_temp.get_latest_data)

async def read_maxigauge_data():
    """Read latest maxigauge data"""
    global maxigauge_reader

    if maxigauge_reader is None:
        return [None] * 6  # Return None for 6 maxigauge values
    
    # Run blocking maxigauge read operation in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, maxigauge_reader.get_latest_data)

async def read_ivc_data():
    """Read latest IVC data"""
    global ivc_reader

    if ivc_reader is None:
        return None  # Return None for IVC value when reader is not available
    
    # Run blocking IVC read operation in thread pool
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(executor, ivc_reader.get_latest_data)
    if data is not None and isinstance(data, (int, float)):
        return data
    else:
        return None

async def insert_QT_data(data):
    """Insert QT data into the QT table"""
    if len(data) != 18:
        logger.error(f"Expected 18 QT values, got {len(data)}")
        return False
        
    try:
        async with await get_database_connection() as conn:
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

            
            await conn.execute('''
                INSERT INTO QT (
                    fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai,
                    pt501_ai, pt502_ai, pt503_ai, pt504_ai,
                    ait501_ai, ti501_ai, ti502_ai, ti503_ai,
                    ti504_ai, ti505_ai, ti523_ai, "Timestamp"
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai, pt501_ai, pt502_ai, pt503_ai, pt504_ai, ait501_ai, ti501_ai, ti502_ai, ti503_ai, ti504_ai, ti505_ai, ti523_ai, await get_current_est_time()))
            
            await conn.commit()
            logger.debug(f"Inserted QT data: {data[:3]}...")
            return True
    except Exception as e:
        logger.error(f"Error inserting QT data: {e}")
        return False

async def insert_teledyne_data(flow_data):
    """Insert Teledyne data into the flow_rates table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
                INSERT INTO Flow_Rates (seperator_flow, magnet_flow, main_flow, "Timestamp") 
                VALUES (%s, %s, %s, %s)
            ''', flow_data + [await get_current_est_time()])
            
            await conn.commit()
            logger.debug(f"Inserted Teledyne data: {flow_data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting Teledyne data: {e}")
        return False

async def insert_labjack_1_data(pressure_data):
    """Insert LabJack data into the pressures table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
                INSERT INTO Labjack (root_exhaust_pressure, buffer_pressure, magnet_pressure, purifier_inlet_pressure, fridge_vapor_pressure, thermocouple, "Timestamp") 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (pressure_data[0], pressure_data[1], pressure_data[2], pressure_data[3], pressure_data[4], pressure_data[5], await get_current_est_time()))
            
            await conn.commit()
            logger.debug(f"Inserted LabJack data: {pressure_data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting LabJack data: {e}")
        return False

async def insert_labjack_2_data(flow_data):
    """Insert LabJack 2 data into the Flow_Rates table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
                INSERT INTO Flow_Rates (microwave_flow, heat_exchanger_flow) 
                VALUES (%s, %s)
            ''', (flow_data[0], flow_data[1]))

            await conn.execute('''
                INSERT INTO Labjack (magnet_bottom_temperature, magnet_top_temperature) 
                VALUES (%s, %s)
            ''', (flow_data[2], flow_data[3]))
            
            await conn.commit()
            logger.debug(f"Inserted LabJack 2 data into Flow_Rates: {flow_data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting LabJack 2 data: {e}")
        return False

async def insert_lakeshore_data_target_stick(data):
    """Insert Lakeshore data into the lakeshore_target_stick table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], await get_current_est_time()))
            
            await conn.commit()
            logger.debug(f"Inserted Target Stick Lakeshore data: {data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting Target Stick Lakeshore data: {e}")
        return False

async def insert_lakeshore_data_fridge_temp(data):
    """Insert Lakeshore data into the lakeshore_fridge_temp table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], await get_current_est_time()))

            await conn.commit()
            logger.debug(f"Inserted Fridge Lakeshore data: {data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting Fridge Lakeshore data: {e}")
        return False

async def insert_lakeshore_data_magnet_temp(data):
    """Insert Lakeshore data into the lakeshore_magnet_temp table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], await get_current_est_time()))
            
            await conn.commit()
            logger.debug(f"Inserted Magnet Lakeshore data: {data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting Magnet Lakeshore data: {e}")
        return False

async def insert_maxigauge_data(data):
    """Insert MaxiGauge data into the maxigauge table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
                INSERT INTO MaxiGauge (
                    "maxigauge_seperator_inlet_pressure",
                    "maxigauge_upper_roots_pressure",
                    "maxigauge_channel_3",
                    "maxigauge_channel_4",
                    "maxigauge_channel_5",
                    "maxigauge_channel_6",
                    "Timestamp"
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (data[0], data[1], data[2], data[3], data[4], data[5], await get_current_est_time()))

            await conn.commit()
            logger.debug(f"Inserted MaxiGauge data: {data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting MaxiGauge data: {e}")
        return False

async def insert_ivc_data(data):
    """Insert IVC data into the ivc table"""
    try:
        async with await get_database_connection() as conn:
            await conn.execute('''
                INSERT INTO IVC (
                    "ivc_pressure",
                    "Timestamp"
                ) VALUES (%s, %s)
            ''', (data, await get_current_est_time()))
            
            await conn.commit()
            logger.debug(f"Inserted IVC data: {data}")
            return True
    except Exception as e:
        logger.error(f"Error inserting IVC data: {e}")
        return False

async def pipeline_to_database(QT_data, teledyne_data, labjack_data_1, labjack_data_2, lakeshore_data_target_stick, lakeshore_data_fridge_temp, lakeshore_data_magnet_temp, maxigauge_data, ivc_data):
    """Pipeline data directly to the database using concurrent operations"""
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
    
    # Prepare database operations
    db_operations = []
    
    # Add QT data operation
    if QT_data is not None:
        db_operations.append(('QT', insert_QT_data(QT_data)))
    
    # Add LabJack 1 data operation
    if labjack_data_1 is not None and len(labjack_data_1) >= 6:
        root_exhaust_pressure = labjack_data_1[0]
        buffer_pressure = labjack_data_1[1]
        magnet_pressure = labjack_data_1[2]
        purifier_inlet_pressure = labjack_data_1[3]
        fridge_vapor_pressure = labjack_data_1[4]
        thermocouple = labjack_data_1[5]
        logger.debug(f"LabJack 1 data: {labjack_data_1}")
        db_operations.append(('LabJack_1', insert_labjack_1_data([root_exhaust_pressure, buffer_pressure, magnet_pressure, purifier_inlet_pressure, fridge_vapor_pressure, thermocouple])))
    
    # Add Teledyne data operation
    if teledyne_data is not None and any(v is not None for v in teledyne_data[:3]):
        db_operations.append(('Teledyne', insert_teledyne_data(teledyne_data)))
    
    # Add LabJack 2 data operation
    if labjack_data_2 is not None and len(labjack_data_2) >= 2:
        db_operations.append(('LabJack_2', insert_labjack_2_data(labjack_data_2)))
    
    # Add Lakeshore Target Stick data operation
    if lakeshore_data_target_stick is not None:
        db_operations.append(('Lakeshore_TS', insert_lakeshore_data_target_stick(lakeshore_data_target_stick)))
    
    # Add Lakeshore Fridge Temp data operation
    if lakeshore_data_fridge_temp is not None:
        db_operations.append(('Lakeshore_FT', insert_lakeshore_data_fridge_temp(lakeshore_data_fridge_temp)))
    
    # Add Lakeshore Magnet Temp data operation
    if lakeshore_data_magnet_temp is not None:
        db_operations.append(('Lakeshore_MT', insert_lakeshore_data_magnet_temp(lakeshore_data_magnet_temp)))
    
    # Add MaxiGauge data operation
    if maxigauge_data is not None and isinstance(maxigauge_data, list) and len(maxigauge_data) == 6:
        logger.debug(f"MaxiGauge data: {maxigauge_data}")
        db_operations.append(('MaxiGauge', insert_maxigauge_data(maxigauge_data)))
    
    # Add IVC data operation
    if ivc_data is not None and isinstance(ivc_data, (int, float)):
        logger.debug(f"IVC data: {ivc_data}")
        db_operations.append(('IVC', insert_ivc_data(ivc_data)))
    
    # Execute all database operations concurrently
    if db_operations:
        try:
            # Run all operations concurrently
            results = await asyncio.gather(*[op[1] for op in db_operations], return_exceptions=True)
            
            # Process results and update statuses
            for i, (operation_name, _) in enumerate(db_operations):
                result = results[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Error in {operation_name} operation: {result}")
                    if operation_name == 'QT':
                        QT_status = 'error'
                    elif operation_name == 'Teledyne':
                        teledyne_status = 'error'
                    elif operation_name == 'LabJack_1':
                        labjack_1_status = 'error'
                    elif operation_name == 'LabJack_2':
                        labjack_2_status = 'error'
                    elif operation_name == 'Lakeshore_TS':
                        lakeshore_target_stick_status = 'error'
                    elif operation_name == 'Lakeshore_FT':
                        lakeshore_fridge_temp_status = 'error'
                    elif operation_name == 'Lakeshore_MT':
                        lakeshore_magnet_temp_status = 'error'
                    elif operation_name == 'MaxiGauge':
                        maxigauge_status = 'error'
                    elif operation_name == 'IVC':
                        ivc_status = 'error'
                elif result:
                    logger.debug(f"Successfully inserted {operation_name} data")
                    if operation_name == 'QT':
                        QT_status = 'success'
                    elif operation_name == 'Teledyne':
                        teledyne_status = 'success'
                    elif operation_name == 'LabJack_1':
                        labjack_1_status = 'success'
                    elif operation_name == 'LabJack_2':
                        labjack_2_status = 'success'
                    elif operation_name == 'Lakeshore_TS':
                        lakeshore_target_stick_status = 'success'
                    elif operation_name == 'Lakeshore_FT':
                        lakeshore_fridge_temp_status = 'success'
                    elif operation_name == 'Lakeshore_MT':
                        lakeshore_magnet_temp_status = 'success'
                    elif operation_name == 'MaxiGauge':
                        maxigauge_status = 'success'
                    elif operation_name == 'IVC':
                        ivc_status = 'success'
                else:
                    logger.error(f"Failed to insert {operation_name} data")
                    if operation_name == 'QT':
                        QT_status = 'error'
                    elif operation_name == 'Teledyne':
                        teledyne_status = 'error'
                    elif operation_name == 'LabJack_1':
                        labjack_1_status = 'error'
                    elif operation_name == 'LabJack_2':
                        labjack_2_status = 'error'
                    elif operation_name == 'Lakeshore_TS':
                        lakeshore_target_stick_status = 'error'
                    elif operation_name == 'Lakeshore_FT':
                        lakeshore_fridge_temp_status = 'error'
                    elif operation_name == 'Lakeshore_MT':
                        lakeshore_magnet_temp_status = 'error'
                    elif operation_name == 'MaxiGauge':
                        maxigauge_status = 'error'
                    elif operation_name == 'IVC':
                        ivc_status = 'error'
                        
        except Exception as e:
            logger.error(f"Error during concurrent database operations: {e}")
            # Set all statuses to error if there's a general failure
            QT_status = 'error'
            teledyne_status = 'error'
            labjack_1_status = 'error'
            labjack_2_status = 'error'
            lakeshore_target_stick_status = 'error'
            lakeshore_fridge_temp_status = 'error'
            lakeshore_magnet_temp_status = 'error'
            maxigauge_status = 'error'
            ivc_status = 'error'
    
    # Calculate overall success based on whether any data was successfully inserted
    successful_inserts = sum(1 for status in [QT_status, teledyne_status, labjack_1_status, labjack_2_status, 
                                             lakeshore_target_stick_status, lakeshore_fridge_temp_status, 
                                             lakeshore_magnet_temp_status, maxigauge_status, ivc_status] 
                           if status == 'success')
    
    overall_success = successful_inserts > 0

    return overall_success, QT_status, teledyne_status, labjack_1_status, labjack_2_status, lakeshore_target_stick_status, lakeshore_fridge_temp_status, lakeshore_magnet_temp_status, maxigauge_status, ivc_status


async def main():
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
        await print_status_header()

    logger.info("Starting Data Acquisition System with Direct Database Pipeline")
    if args.verbose:
        logger.info("VERBOSE: Verbose mode enabled")
        logger.info(f"VERBOSE: Database host: {DATABASE_HOST}")
        logger.info(f"VERBOSE: Database port: {DATABASE_PORT}")
        logger.info(f"VERBOSE: Database user: {DATABASE_USER}")
        logger.info(f"VERBOSE: Database name: {DATABASE_NAME}")
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
        await setup_database()
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
        if ivc_reader.data_stream():
            logger.info("IVC data reader started and data stream initiated")
        else:
            logger.error("IVC data reader started but failed to start data stream")
    except Exception as e:
        logger.error(f"Error starting ivc data reader: {e}")

    iteration = 0
    
    try:
        while not shutdown_event.is_set():
            try:
                iteration += 1
                
                QT_data, teledyne_data, labjack_data_1, labjack_data_2, lakeshore_data_target_stick, lakeshore_data_fridge_temp, lakeshore_data_magnet_temp, maxigauge_data, ivc_data = await asyncio.gather(
                    _read_QT(),
                    read_teledyne_data(),
                    read_labjack_data_1(),
                    read_labjack_data_2(),
                    read_lakeshore_data_target_stick(),
                    read_lakeshore_data_fridge_temp(),
                    read_lakeshore_data_magnet_temp(),
                    read_maxigauge_data(),
                    read_ivc_data(),
                    return_exceptions=True
                )
                
                if isinstance(QT_data, Exception):
                    logger.error(f"Error reading QT data: {QT_data}")
                    QT_data = None
                if isinstance(teledyne_data, Exception):
                    logger.error(f"Error reading Teledyne data: {teledyne_data}")
                    teledyne_data = None
                if isinstance(labjack_data_1, Exception):
                    logger.error(f"Error reading LabJack 1 data: {labjack_data_1}")
                    labjack_data_1 = None
                if isinstance(labjack_data_2, Exception):
                    logger.error(f"Error reading LabJack 2 data: {labjack_data_2}")
                    labjack_data_2 = None
                if isinstance(lakeshore_data_target_stick, Exception):
                    logger.error(f"Error reading Lakeshore Target Stick data: {lakeshore_data_target_stick}")
                    lakeshore_data_target_stick = None
                if isinstance(lakeshore_data_fridge_temp, Exception):
                    logger.error(f"Error reading Lakeshore Fridge Temp data: {lakeshore_data_fridge_temp}")
                    lakeshore_data_fridge_temp = None
                if isinstance(lakeshore_data_magnet_temp, Exception):
                    logger.error(f"Error reading Lakeshore Magnet Temp data: {lakeshore_data_magnet_temp}")
                    lakeshore_data_magnet_temp = None
                if isinstance(maxigauge_data, Exception):
                    logger.error(f"Error reading MaxiGauge data: {maxigauge_data}")
                    maxigauge_data = None
                if isinstance(ivc_data, Exception):
                    logger.error(f"Error reading IVC data: {ivc_data}")
                    ivc_data = None
                
                if QT_data is None:
                    logger.warning(f"Failed to read QT data. Continuing with other data sources (Teledyne, LabJack, LakeShore, MaxiGauge, IVC)...")
                
                # Pipeline data directly to database
                db_success, QT_status, teledyne_status, labjack_1_status, labjack_2_status, lakeshore_target_stick_status, lakeshore_fridge_temp_status, lakeshore_magnet_temp_status, maxigauge_status, ivc_status = await pipeline_to_database(
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
                    await print_status_update(iteration, 
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
                
                if shutdown_event.is_set():
                    break
                    
                # await asyncio.sleep(SLEEP_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Data acquisition stopped by user")
                if not args.verbose and not args.terminal_log:
                    print("\n\n🛑 Data acquisition stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                if not args.verbose and not args.terminal_log:
                    await print_status_update(iteration, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error')
                
                # Continue with next iteration after error
                if not shutdown_event.is_set():
                    await asyncio.sleep(SLEEP_INTERVAL)
        
        logger.info("Shutdown signal received, cleaning up...")
                
    finally:
        logger.info("Cleaning up data acquisition system")

        executor.shutdown(wait=True)
        logger.info("Thread pool executor shutdown")

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
    asyncio.run(main()) 