# Configuration file for data acquisition system

# Remote Flask server configuration
REMOTE_SERVER_URL = "http://128.143.231.224:5000"  # Flask server's IP and port

TWIST_PATH = "\\www.twist.phys.virginia.edu\www\spin"

DATA_PATH = f"{REMOTE_SERVER_URL}/data"

# Local data storage
LOCAL_CSV_DIR = "data_logs"  # Directory to store local CSV backups

# Data acquisition settings
SLEEP_INTERVAL = 5  # Seconds between data readings
MAX_CONSECUTIVE_FAILURES = 10  # Stop after this many consecutive failures

# Modbus settings
PLC_IP = "192.168.0.1"
UNIT_ID = 2
INT_PORT = 503
FLOAT_PORT = 502
NUM_REG_TO_READ = 36  # Changed from 49 to 36 to get exactly 18 float values

# Teledyne flow data settings
TELEDYNE_CSV_PATH = "{TWIST_PATH}\monitoring\teledyne_flow.csv"  # Path to teledyne flow CSV file
TELEDYNE_CHECK_INTERVAL = 1  # Check for new teledyne data every second

# LabJack pressure data settings
LABJACK_CSV_PATH = r"{TWIST_PATH}\monitoring\labjack_pressure.csv"  # Path to labjack pressure CSV file
LABJACK_CHECK_INTERVAL = 1  # Check for new labjack data every second

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data_acquisition.log" 


### Database settings
DATABASE_DIR = f"{TWIST_PATH}\instance"

DATABASE_NAME = "flaskr.sqlite"

DATABASE_PATH = "{DATABASE_DIR}\{DATABASE_NAME}"

def _read_HMI():
    """Read data from Modbus TCP server"""
    plc_ip = PLC_IP
    unit_id = UNIT_ID
    int_port = INT_PORT
    float_port = FLOAT_PORT
    num_reg_to_read = NUM_REG_TO_READ

    logger.info(f"Attempting to read HMI data from PLC at {plc_ip}")
    logger.info(f"Connection details: Unit ID: {unit_id}, Integer Port: {int_port}, Float Port: {float_port}")

    try:
        # Read integer values
        logger.info(f"Connecting to PLC for integer registers (Port {int_port})...")
        client = ModbusClient(host=plc_ip, port=int_port, unit_id=unit_id, auto_open=True, auto_close=False)
        
        if not client.is_open:
            logger.error("Failed to open connection for integer registers")
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