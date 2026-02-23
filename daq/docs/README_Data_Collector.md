# Data Collector System

## Overview

The Data Collector is a Flask-based web server that receives data from multiple sources via HTTP endpoints and stores it in a SQLite database. It serves as the central data collection point for the lab monitoring system.

## Architecture

```
Data Acquisition Machine (Modbus) → HTTP POST → Data Collector Machine → SQLite Database
HMI TCP Server (Modbus) → HTTP POST → Data Collector Machine → SQLite Database
```

## Key Changes Made

### 1. Removed CSV File Monitoring
- **Problem**: The data collector was trying to monitor local CSV files that were being generated on different machines
- **Solution**: Removed CSV monitoring functionality and focused on HTTP data reception

### 2. Fixed Endpoint URLs
- **Problem**: HMI TCP server was sending to incorrect endpoints
- **Solution**: Updated URLs to match the data collector's expected endpoints

### 3. Simplified Data Flow
- Data acquisition devices send data directly via HTTP POST
- No more file-based data transfer between machines
- Real-time data collection and storage

## Data Flow

### 1. HMI Data (18 values)
```
HMI_TCP_Server.py → POST /receive_hmi_data → Data Collector → Database
```

### 2. Merged Data (18+ values)
```
run.py → MariaDB (direct) | Data Collector reads from DB
```

### 3. Data Query
```
Web Interface → GET /query_db → Data Collector → Database → JSON Response
```

## Setup Instructions

### On Data Collector Machine

1. **Install Dependencies**:
   ```bash
   cd GUI-Webserver/web_server
   pip install -r requirements.txt
   ```

2. **Start Data Collector**:
   ```bash
   python start_data_collector.py
   ```

3. **Verify Operation**:
   ```bash
   python test_data_collector.py
   ```

### On Data Acquisition Machine

1. **Configure Data Acquisition**:
   ```bash
   cd GUI-Webserver/data_acquisition
   # Edit config.json (remote.server_url) or set REMOTE_SERVER_URL env var
   ```

2. **Start Data Acquisition**:
   ```bash
   python run.py
   ```

### On HMI Machine

1. **Configure HMI TCP Server**:
   ```bash
   cd GUI-Webserver/utils
   # Edit HMI_TCP_Sserver.py to set correct URL
   ```

2. **Start HMI Server**:
   ```bash
   python HMI_TCP_Sserver.py
   ```

## Endpoints

### POST /receive_hmi_data
- **Purpose**: Receive HMI data (18 values)
- **Data Format**: JSON array of 18 float values
- **Example**:
  ```json
  [10.5, 20.3, 15.7, 25.1, 30.2, 40.1, 50.8, 60.3, 70.9, 80.4, 90.2, 100.1, 110.5, 120.8, 130.3, 140.7, 150.2, 160.9]
  ```

### POST /data
- **Purpose**: Receive merged data (18+ values)
- **Data Format**: JSON array of float values
- **Supported Lengths**: 18, 21, or 24 values

### GET /query_db
- **Purpose**: Query stored data for plotting
- **Parameters**:
  - `keys`: Comma-separated column names
  - `start_time`: Start timestamp (optional)
  - `end_time`: End timestamp (optional)

### GET /health
- **Purpose**: Health check endpoint
- **Returns**: Status and timestamp

## Database Schema

The `merged_data` table stores all data with the following columns:

- **HMI Data**: fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai, pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream, purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai, ti504_ai, ti505_ai, ti523_ai
- **Additional Data**: r2_value, ch1, ch2, ch3
- **Metadata**: timestamp, data_source, created_at

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if data collector is running on correct port (5000)
   - Verify firewall settings
   - Check network connectivity between machines

2. **Data Not Being Stored**:
   - Check data collector logs for errors
   - Verify data format matches expected schema
   - Check database permissions

3. **Endpoint Not Found (404)**:
   - Verify correct URL endpoints
   - Check if Flask app is running
   - Ensure proper HTTP method (POST vs GET)

### Testing

Use the test script to verify all endpoints:
```bash
python test_data_collector.py
```

### Logs

Check the console output for detailed logging information. The data collector logs all incoming requests and database operations.

## Configuration

### Data Collector Configuration
- **Port**: 5000 (default)
- **Host**: 0.0.0.0 (accepts connections from any IP)
- **Database**: ../instance/flaskr.sqlite

### Network Configuration
- **Data Collector IP**: 172.29.36.50:5000
- **Data Acquisition IP**: Configure in config.json (plc.ip)
- **HMI Server IP**: Configure in HMI_TCP_Sserver.py

## Security Notes

- The data collector accepts connections from any IP (0.0.0.0)
- Consider implementing authentication for production use
- Database file should have appropriate permissions
- Consider using HTTPS for sensitive data transmission 