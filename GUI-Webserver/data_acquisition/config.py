# Configuration file for data acquisition system

# Remote Flask server configuration
REMOTE_SERVER_URL = "http://172.29.36.50:5000/data"  # Change this to your Flask server's IP and port

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
NUM_REG_TO_READ = 49

# Teledyne flow data settings
TELEDYNE_CSV_PATH = "../static/csv/teledyne_flow.csv"  # Path to teledyne flow CSV file
TELEDYNE_CHECK_INTERVAL = 1  # Check for new teledyne data every second

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data_acquisition.log" 