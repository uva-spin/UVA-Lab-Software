# Configuration file for data acquisition system
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

# Local data storage
LOCAL_CSV_DIR = "data_logs"  

# Data acquisition settings
SLEEP_INTERVAL = 5  
MAX_CONSECUTIVE_FAILURES = 10  

# PLC configuration
PLC_IP = os.getenv("DAQ_PLC_IP", "172.29.36.195")
UNIT_ID = _env_int("DAQ_UNIT_ID", 2)
INT_PORT = _env_int("DAQ_INT_PORT", 503)
FLOAT_PORT = _env_int("DAQ_FLOAT_PORT", 502)
NUM_REG_TO_READ = _env_int("DAQ_NUM_REG_TO_READ", 36)

# Device TCP configuration
TELEDYNE_IP = os.getenv("DAQ_TELEDYNE_IP", "172.29.36.192")
TELEDYNE_PORT = _env_int("DAQ_TELEDYNE_PORT", 101)
MAXIGAUGE_IP = os.getenv("DAQ_MAXIGAUGE_IP", "172.29.36.194")
MAXIGAUGE_PORT = _env_int("DAQ_MAXIGAUGE_PORT", 8000)

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
    "target_stick": os.getenv("DAQ_LAKESHORE_TARGET_STICK_PORT", "COM4"),
    "fridge_temp": os.getenv("DAQ_LAKESHORE_FRIDGE_PORT", "COM5"),
    "magnet_temp": os.getenv("DAQ_LAKESHORE_MAGNET_PORT", "COM6"),
}

# IVC pressure controller serial port
IVC_PORT = os.getenv("DAQ_IVC_PORT", "COM7")

# Data collection intervals (seconds)
TELEDYNE_CHECK_INTERVAL = _env_int("DAQ_TELEDYNE_CHECK_INTERVAL", 10)  # Check for new teledyne data
LABJACK_CHECK_INTERVAL = _env_int("DAQ_LABJACK_CHECK_INTERVAL", 1)    # Check for new labjack data
LAKESHORE_CHECK_INTERVAL = _env_int("DAQ_LAKESHORE_CHECK_INTERVAL", 1)  # Check for new lakeshore data
MAXIGAUGE_CHECK_INTERVAL = _env_int("DAQ_MAXIGAUGE_CHECK_INTERVAL", 1)  # Check for new maxigauge data
ASYNC_READ_INTERVAL = _env_int("DAQ_ASYNC_READ_INTERVAL", 1)       # Check for new data (async)

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data_acquisition.log"

# Network paths
TWIST_PATH = os.getenv("DAQ_TWIST_PATH")

DATABASE_FILE = os.getenv("DAQ_DATABASE_FILE")


