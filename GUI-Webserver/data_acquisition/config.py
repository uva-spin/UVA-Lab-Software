# Configuration file for data acquisition system

# Remote Flask server configuration
REMOTE_SERVER_URL = "http://128.143.231.224:5000"  # Flask server's IP and port

TWIST_PATH = "/mnt/twist/www/spin/"

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
TELEDYNE_CSV_PATH = f"{TWIST_PATH}/monitoring/teledyne_flow.csv"  # Path to teledyne flow CSV file
TELEDYNE_CHECK_INTERVAL = 1  # Check for new teledyne data every second

# LabJack pressure data settings
LABJACK_CSV_PATH = f"{TWIST_PATH}/monitoring/labjack_pressure.csv"  # Path to labjack pressure CSV file
LABJACK_CHECK_INTERVAL = 1  # Check for new labjack data every second

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data_acquisition.log" 


### Database settings
DATABASE_DIR = f"/mnt/twist/www/spin/instance"

DATABASE_NAME = "flaskr.sqlite"

DATABASE_PATH = f"{DATABASE_DIR}/{DATABASE_NAME}"