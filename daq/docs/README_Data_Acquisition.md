# Data Acquisition Setup

This guide explains how to set up the data acquisition system on the machine connected to your Modbus devices.

## Architecture (ETL Pipeline)

The DAQ system follows a clean **Extract → Transform → Load** pattern:

```
devices/ (Extract)  →  core/pipeline (Transform)  →  core/loaders (Load)  →  MariaDB
```

**Key modules:**
- `config.py` - Single source of configuration
- `core/schema.py` - Table/column definitions (aligned with schema.sql)
- `core/loaders.py` - Unified MariaDB INSERT layer
- `core/pipeline.py` - ETL orchestration
- `acquisition/standalone.py` - Entry point
- `devices/` - Hardware readers (QT, Teledyne, LabJack, LakeShore, MaxiGauge, IVC)

## System Architecture

```
Modbus/TCP/Serial Devices → run.py → MariaDB
```

## Prerequisites

### Data Acquisition Computer
- Python 3.7+
- Network connection to devices (QT PLC, Teledyne, MaxiGauge)
- USB for LabJack, serial ports for LakeShore/IVC
- MariaDB access (config.json with host, port, user, password, database)

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd daq
pip install -r requirements.txt
```

### Step 2: Configure

Edit `config.json` in the daq directory. Set the `database` section with your MariaDB credentials:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "your_user",
    "password": "your_password",
    "database": "your_database"
  },
  ...
}
```

Or set `DAQ_CONFIG` to the path of your config file.

### Step 3: Start Data Acquisition

```bash
cd daq
python run.py
```

Options:
```bash
python run.py --verbose          # Verbose logging
python run.py --terminal-log     # Show logs in terminal
```

## Configuration

### config.json

Edit `config.json` to change settings. Key sections:

- **database** – MariaDB credentials (host, port, user, password, database)
- **paths** – local_csv_dir, logs_dir
- **intervals** – sleep_interval, teledyne_check_interval, etc.
- **plc** – ip, unit_id, int_port, float_port, qt_labels
- **devices** – lakeshore_ports, ivc_port
- **remote** – server_url

Example overrides:

```json
{
  "intervals": { "sleep_interval": 10 },
  "plc": { "ip": "192.168.0.1", "float_port": 502, "num_reg_to_read": 49 }
}
```

Environment variables: `DAQ_CONFIG` (config path), `REMOTE_SERVER_URL`.

## Data Flow

1. **Extract**: Device readers poll hardware (QT, Teledyne, LabJack, LakeShore, MaxiGauge, IVC)
2. **Transform**: Pipeline maps raw values to schema columns
3. **Load**: MariaDBLoader inserts into MariaDB tables
4. **Logging**: All activities are logged to `logs/data_acquisition.log`

## File Structure

```
daq/
├── run.py                    # Entry point
├── config.py                 # Loads config.json
├── config.json               # All configuration (database, intervals, plc, etc.)
├── core/                     # ETL pipeline
├── acquisition/              # Entry point logic
├── devices/                  # Hardware readers
├── web_server/               # Flask API (optional)
└── logs/
    └── data_acquisition.log
```

## Monitoring and Troubleshooting

### Check if Data Acquisition is Running

```bash
ps aux | grep run.py
```

### View Logs

```bash
tail -f logs/data_acquisition.log
```

## Common Issues

### 1. Cannot Connect to Modbus Devices

**Symptoms**: "Failed to read float registers" in logs

**Solutions**:
- Check PLC IP address in config.json
- Verify network connectivity to PLC
- Check Modbus port settings
- Ensure PLC is powered on and accessible

### 2. Cannot Connect to Database

**Symptoms**: "Database setup error" or "Failed to create connection pool" in logs

**Solutions**:
- Verify config.json exists and has correct host, port, user, password, database
- Test MariaDB connectivity: `mysql -h host -u user -p database -e "SELECT 1"`
- Check firewall allows connection to MariaDB port

### 3. Permission Errors

**Symptoms**: "Permission denied" when creating files

**Solutions**:
- Ensure write permissions in current directory
- Run script with appropriate user permissions
- Check disk space availability

### 4. High CPU Usage

**Symptoms**: System becomes slow

**Solutions**:
- Increase intervals.sleep_interval in config.json
- Check for network timeouts
- Monitor system resources

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
WorkingDirectory=/path/to/daq
ExecStart=/usr/bin/python3 run.py
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
4. Set action to start `python run.py` (from daq directory)
5. Configure to run whether user is logged on or not 