# Configuration file for data acquisition system

# Remote Flask server configuration
REMOTE_SERVER_URL = "http://128.143.231.224:5000"  # Flask server's IP and port

# Network share path for the local machine
TWIST_PATH = "//twist.phys.virginia.edu/www/spin"  # UNC path to the network share

DATA_PATH = f"{REMOTE_SERVER_URL}/data"

# Local data storage
LOCAL_CSV_DIR = "data_logs"  # Directory to store local CSV backups

# Data acquisition settings
SLEEP_INTERVAL = 5  # Seconds between data readings
MAX_CONSECUTIVE_FAILURES = 10  # Stop after this many consecutive failures

# Modbus settings
PLC_IP = "172.29.36.195"
UNIT_ID = 2
INT_PORT = 503
FLOAT_PORT = 502
NUM_REG_TO_READ = 36  

# Teledyne flow data settings
TELEDYNE_CHECK_INTERVAL = 1  # Check for new teledyne data every second

# LabJack pressure data settings
LABJACK_CHECK_INTERVAL = 1  # Check for new labjack data every second

# LakeShore temperature data settings
LAKESHORE_CHECK_INTERVAL = 1  # Check for new lakeshore data every second

# MaxiGauge pressure data settings
MAXIGAUGE_CHECK_INTERVAL = 1  # Check for new maxigauge data every second

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data_acquisition.log" 


### Database settings
DATABASE_DIR = "//twist.phys.virginia.edu/www/spin/instance"
DATABASE_NAME = "flaskr.sqlite"
DATABASE_PATH = f"{DATABASE_DIR}/{DATABASE_NAME}"