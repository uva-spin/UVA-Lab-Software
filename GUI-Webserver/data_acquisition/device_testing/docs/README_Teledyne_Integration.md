# Teledyne Flow Data Integration

## Overview

The data acquisition system has been enhanced to read teledyne flow data in real-time from a CSV file alongside the existing Modbus data collection.

## Features

- **Real-time CSV monitoring**: Continuously monitors `teledyne_flow.csv` for new data
- **Thread-safe operation**: Uses a separate thread to monitor the CSV file without blocking the main data acquisition loop
- **Automatic data parsing**: Parses timestamp and three flow values from each CSV line
- **Combined data transmission**: Sends both Modbus and teledyne data to the remote server
- **Local backup**: Saves combined data to local CSV files as backup

## File Structure

The teledyne flow data should be stored in:
```
GUI-Webserver/static/csv/teledyne_flow.csv
```

## CSV Format

The teledyne flow CSV file should have the following format:
```csv
timestamp,flow_1,flow_2,flow_3
2025-02-20T14:30:15.123456,25.5,26.2,24.8
2025-02-20T14:30:20.234567,25.6,26.3,24.9
```

Where:
- `timestamp`: ISO format timestamp
- `flow_1`, `flow_2`, `flow_3`: Flow rate values (numeric)

## Configuration

Add the following settings to `config.py`:

```python
# Teledyne flow data settings
TELEDYNE_CSV_PATH = "../static/csv/teledyne_flow.csv"  # Path to teledyne flow CSV file
TELEDYNE_CHECK_INTERVAL = 1  # Check for new teledyne data every second
```

## Data Structure

The system now sends combined data to the remote server with the following structure:

```json
{
    "timestamp": "2025-02-20T14:30:15.123456",
    "modbus_data": [25.5, 26.2, 24.8, ...],
    "teledyne_data": {
        "timestamp": "2025-02-20T14:30:15.123456",
        "flow_1": 25.5,
        "flow_2": 26.2,
        "flow_3": 24.8
    }
}
```

## Local CSV Output

The local backup CSV files now include both Modbus and teledyne data with the following columns:

1. `timestamp` - System timestamp
2. `FC501.AI.Value` - Modbus data (18 columns)
3. `FC501_OUT.Value`
4. ...
5. `TI523.AI.Value`
6. `teledyne_timestamp` - Teledyne data timestamp
7. `teledyne_flow_1` - First flow value
8. `teledyne_flow_2` - Second flow value
9. `teledyne_flow_3` - Third flow value

## Testing

Run the test script to verify the teledyne data reading functionality:

```bash
cd GUI-Webserver/data_acquisition
python test_teledyne_reader.py
```

## Operation

1. The system starts a background thread that monitors the teledyne CSV file
2. When new data is detected, it's parsed and added to a thread-safe queue
3. The main data acquisition loop reads from both Modbus and the teledyne queue
4. Data is combined and sent to the remote server
5. Combined data is also saved to local CSV files

## Error Handling

- If the teledyne CSV file is not found, the system continues with Modbus data only
- If teledyne data parsing fails, the error is logged and the system continues
- If no new teledyne data is available, empty values are sent for teledyne fields

## Performance

- The teledyne monitoring thread runs independently and doesn't affect Modbus data collection timing
- File monitoring uses efficient file seeking to only read new data
- The check interval is configurable (default: 1 second) 