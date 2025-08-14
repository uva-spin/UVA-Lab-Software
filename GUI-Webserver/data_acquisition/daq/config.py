# Configuration file for data acquisition system

# Remote Flask server configuration
REMOTE_SERVER_URL = "http://128.143.231.224:5000"  # Flask server's IP and port

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

# MariaDB Database Configuration
DATABASE_HOST = "localhost"          # MariaDB server hostname or IP address
DATABASE_PORT = 3306                 # MariaDB port (default is 3306)
DATABASE_USER = "root"      # MariaDB username
DATABASE_PASSWORD = "pswrd"  # MariaDB password
DATABASE_NAME = "uvaspin"           # MariaDB database name

# Data Collection Settings
LOCAL_CSV_DIR = "data_logs"
SLEEP_INTERVAL = 5                  
MAX_CONSECUTIVE_FAILURES = 10

# PLC Configuration
PLC_IP = "172.29.36.195"
UNIT_ID = 2
INT_PORT = 503
FLOAT_PORT = 502
NUM_REG_TO_READ = 36

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "data_acquisition.log"

# Network Paths
TWIST_PATH = "//twist.phys.virginia.edu/www/spin"

# Data Collection Intervals
TELEDYNE_CHECK_INTERVAL = 10        # Check for new data every 10 seconds
LABJACK_CHECK_INTERVAL = 1          # Check for new data every 1 second
LAKESHORE_CHECK_INTERVAL = 1        # Check for new data every 1 second
MAXIGAUGE_CHECK_INTERVAL = 1        # Check for new data every 1 second

# Security Notes:
# - Store passwords securely (consider using environment variables)
# - Use SSL connections for production environments
# - Limit database user permissions to only what's necessary
# - Regularly rotate database passwords