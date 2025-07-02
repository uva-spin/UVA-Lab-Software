# Data Acquisition Setup

This guide explains how to set up the data acquisition system on the machine connected to your Modbus devices.

## System Architecture

```
Machine A (Data Acquisition): Modbus Devices → standalone_data_acquisition.py → Machine B (Web Server): Flask Server + HTML Display
```

## Prerequisites

### Machine A (Data Acquisition Computer)
- Python 3.7+
- Network connection to Modbus devices
- Network connection to Machine B (Flask server)

### Machine B (Web Server Computer)
- Flask server running and accessible
- Endpoint to receive data (e.g., `/data`)

## Setup Instructions

### Step 1: Copy Files to Data Acquisition Machine

Copy the following files to the machine connected to your Modbus devices:
- `standalone_data_acquisition.py`
- `setup_data_acquisition.py`
- `config.py` (optional, will be created by setup script)

### Step 2: Run Setup Script

```bash
python setup_data_acquisition.py
```

This script will:
- Check and install required dependencies
- Configure the remote server URL
- Test network connectivity
- Create data directories

### Step 3: Configure Remote Server

During setup, you'll be prompted to enter:
- **IP Address**: The IP address of your Flask server (Machine B)
- **Port**: The port your Flask server is running on (typically 5000)

Example:
```
Enter IP address: 192.168.1.100
Enter port: 5000
```

### Step 4: Start Data Acquisition

```bash
python standalone_data_acquisition.py
```

## Configuration

### config.py

You can manually edit `config.py` to change settings:

```python
# Remote Flask server configuration
REMOTE_SERVER_URL = "http://192.168.1.100:5000/data"

# Local data storage
LOCAL_CSV_DIR = "data_logs"

# Data acquisition settings
SLEEP_INTERVAL = 5  # Seconds between readings
MAX_CONSECUTIVE_FAILURES = 10

# Modbus settings
PLC_IP = "192.168.0.1"
UNIT_ID = 2
INT_PORT = 503
FLOAT_PORT = 502
NUM_REG_TO_READ = 49
```

### Command Line Options

You can also override settings via environment variables:

```bash
export REMOTE_SERVER_URL="http://192.168.1.100:5000/data"
export SLEEP_INTERVAL=10
python standalone_data_acquisition.py
```

## Data Flow

1. **Data Reading**: Script reads data from Modbus devices every 5 seconds
2. **Remote Transmission**: Data is sent to the Flask server via HTTP POST
3. **Local Backup**: Data is saved to local CSV files as backup
4. **Logging**: All activities are logged to `data_acquisition.log`

## File Structure

```
data_acquisition_machine/
├── standalone_data_acquisition.py    # Main data acquisition script
├── setup_data_acquisition.py         # Setup and configuration script
├── config.py                         # Configuration file
├── data_acquisition.log              # Log file
└── data_logs/                        # Local CSV backup directory
    ├── hmi_data_20250220.csv
    ├── hmi_data_20250221.csv
    └── ...
```

## Monitoring and Troubleshooting

### Check if Data Acquisition is Running

```bash
ps aux | grep standalone_data_acquisition
```

### View Logs

```bash
tail -f data_acquisition.log
```

### Test Network Connectivity

```bash
curl http://192.168.1.100:5000/health
```

### Check Local Data Files

```bash
ls -la data_logs/
head -10 data_logs/hmi_data_$(date +%Y%m%d).csv
```

## Common Issues

### 1. Cannot Connect to Modbus Devices

**Symptoms**: "Failed to read float registers" in logs

**Solutions**:
- Check PLC IP address in config.py
- Verify network connectivity to PLC
- Check Modbus port settings
- Ensure PLC is powered on and accessible

### 2. Cannot Connect to Remote Server

**Symptoms**: "Failed to send data to remote server" in logs

**Solutions**:
- Verify Flask server is running on Machine B
- Check IP address and port in config.py
- Test network connectivity between machines
- Check firewall settings

### 3. Permission Errors

**Symptoms**: "Permission denied" when creating files

**Solutions**:
- Ensure write permissions in current directory
- Run script with appropriate user permissions
- Check disk space availability

### 4. High CPU Usage

**Symptoms**: System becomes slow

**Solutions**:
- Increase SLEEP_INTERVAL in config.py
- Check for network timeouts
- Monitor system resources

## Data Format

The script sends data in this format to the Flask server:

```json
[
  100.0, 50.0, 200.0, 75.0, 25.0, 300.0, 400.0, 500.0, 600.0,
  95.5, 98.2, 150.0, 75.5, 80.2, 85.1, 90.3, 95.7, 88.9
]
```

Each value corresponds to a Modbus register in order.

## Local CSV Backup Format

Local CSV files contain:
- `timestamp`: ISO format timestamp
- `FC501.AI.Value`, `FC501_OUT.Value`, etc.: Modbus values

Example:
```csv
timestamp,FC501.AI.Value,FC501_OUT.Value,...
2025-02-20T14:30:15.123456,100.0,50.0,...
```

## Stopping the Data Acquisition

Press `Ctrl+C` to gracefully stop the data acquisition script.

## Running as a Service

### Linux (systemd)

Create a service file `/etc/systemd/system/data-acquisition.service`:

```ini
[Unit]
Description=Data Acquisition Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/data_acquisition
ExecStart=/usr/bin/python3 standalone_data_acquisition.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable data-acquisition
sudo systemctl start data-acquisition
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., at startup)
4. Set action to start `python standalone_data_acquisition.py`
5. Configure to run whether user is logged on or not 