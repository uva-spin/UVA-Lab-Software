# Configuration file for data acquisition system
import os

# Project root (parent of daq/)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Local data storage
LOCAL_CSV_DIR = "data_logs"  

# Data acquisition settings
SLEEP_INTERVAL = 5  
MAX_CONSECUTIVE_FAILURES = 10  

# PLC configuration
PLC_IP = "172.29.36.195"
UNIT_ID = 2
INT_PORT = 503
FLOAT_PORT = 502
NUM_REG_TO_READ = 36

# QT (PLC) data labels
QT_LABELS = [
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
    "TI523.AI.Value",
]

# LakeShore temperature controller serial ports
LAKESHORE_PORTS = {
    "target_stick": "COM4",
    "fridge_temp": "COM5",
    "magnet_temp": "COM6",
}

# IVC pressure controller serial port
IVC_PORT = "COM7"

# Data collection intervals (seconds)
TELEDYNE_CHECK_INTERVAL = 10  # Check for new teledyne data
LABJACK_CHECK_INTERVAL = 1    # Check for new labjack data
LAKESHORE_CHECK_INTERVAL = 1  # Check for new lakeshore data
MAXIGAUGE_CHECK_INTERVAL = 1  # Check for new maxigauge data
ASYNC_READ_INTERVAL = 1       # Check for new data (async)

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data_acquisition.log"

# Database - use shared config.json from uvaspin (host, port, user, password, database, connectionLimit)
DATABASE_FILE = os.path.join(_PROJECT_ROOT, "uvaspin", "config.json")

# Network paths
TWIST_PATH = "//twist.phys.virginia.edu/www/spin"

