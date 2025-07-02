# Data Collection System

This system collects data from multiple sources and merges them into a single SQLite3 database:

1. **HMI Data**: Real-time data from Modbus TCP server
2. **CSV Files**: Multiple CSV files being updated simultaneously
3. **Merged Database**: All data combined into a single SQLite3 database

## System Architecture

```
HMI_TCP_Server.py → Data Collector (Port 5001) → SQLite Database
CSV Files (Test_data.csv, r_values.csv, hmi_data.csv) → CSV Monitor → SQLite Database
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd GUI-Webserver
pip install -r requirements.txt
```

### 2. Start the Data Collector

```bash
python start_data_collector.py
```

This will:
- Create the `instance/` directory if it doesn't exist
- Initialize the SQLite database with the merged schema
- Start the Flask server on port 5001
- Begin monitoring CSV files for changes

### 3. Start the HMI TCP Server

In a separate terminal:

```bash
cd GUI-Webserver/utils
python HMI_TCP_Sserver.py
```

This will:
- Read data from the Modbus TCP server
- Send data to the local data collector (port 5001)
- Fall back to the external server if local collector is unavailable
- Continue writing to CSV files as before

## Database Schema

The merged database contains a single table `merged_data` with columns for all data sources:

### HMI Data Columns
- `fc501_ai`, `fc501_out`, `fc502_ai`, `fc502_out`
- `lit501_ai`, `pt501_ai`, `pt502_ai`, `pt503_ai`, `pt504_ai`
- `purity_downstream`, `purity_upstream`
- `ait501_ai`, `ti501_ai`, `ti502_ai`, `ti503_ai`, `ti504_ai`, `ti505_ai`, `ti523_ai`

### CSV Data Columns
- `r2_test` (from Test_data.csv)
- `r2_value` (from r_values.csv)

### Metadata Columns
- `id` (auto-increment primary key)
- `timestamp` (when the data was recorded)
- `data_source` (hmi, test_data, or r_values)
- `created_at` (when the record was inserted)

## API Endpoints

### Data Collector (Port 5001)

- `POST /receive_hmi_data` - Receive HMI data from TCP server
- `GET /health` - Health check endpoint

## Monitoring and Querying Data

### View Data Summary

```bash
python query_data.py --summary
```

### View Recent Data

```bash
python query_data.py --limit 50
```

### View Data from Last 24 Hours

```bash
python query_data.py --hours 24
```

### Filter by Data Source

```bash
python query_data.py --source hmi --limit 20
python query_data.py --source test_data --limit 20
python query_data.py --source r_values --limit 20
```

### Export Data to CSV

```bash
python query_data.py --export my_data.csv --limit 1000
python query_data.py --export last_24h.csv --export-hours 24
```

## Configuration

### CSV Monitoring Interval

The CSV files are checked every 30 seconds by default. To change this:

1. Edit `data_collector.py`
2. Modify the `interval` parameter in `start_csv_monitoring(interval=30)`

### Database Location

The database is stored in `instance/flaskr.sqlite` by default. To change this:

1. Edit `data_collector.py`
2. Modify the `db_path` parameter in the `DataCollector` constructor

### CSV File Locations

The system monitors these CSV files in the `static/csv/` directory:
- `Test_data.csv`
- `r_values.csv`
- `hmi_data.csv`

To add or modify monitored files, edit the `csv_files` dictionary in `data_collector.py`.

## Troubleshooting

### Check if Data Collector is Running

```bash
curl http://localhost:5001/health
```

### Check Database Connection

```bash
python query_data.py --summary
```

### View Logs

The data collector logs all activities. Check the console output for:
- Database initialization messages
- CSV file processing messages
- HMI data insertion messages
- Error messages

### Common Issues

1. **Port 5001 already in use**: Change the port in `data_collector.py`
2. **CSV files not found**: Ensure files exist in `static/csv/` directory
3. **Database permission errors**: Check write permissions for `instance/` directory
4. **HMI data not being received**: Check if HMI_TCP_Server.py is running and can connect to the Modbus server

## Data Flow

1. **HMI Data Flow**:
   - HMI_TCP_Server.py reads from Modbus TCP
   - Sends data to local data collector (port 5001)
   - Data collector inserts into SQLite database
   - Also writes to hmi_data.csv (original functionality)

2. **CSV Data Flow**:
   - CSV monitor checks files every 30 seconds
   - Detects new data by file modification time
   - Inserts new records into SQLite database
   - Prevents duplicate entries

3. **Database Merging**:
   - All data sources write to the same `merged_data` table
   - Each record is tagged with its `data_source`
   - Timestamps are preserved from original data
   - Index on timestamp for fast queries

## Performance Considerations

- The system uses file modification times to detect CSV changes
- Database queries are indexed on timestamp for performance
- CSV monitoring runs in a background thread
- HMI data is processed immediately when received
- Duplicate prevention uses timestamp + data_source combination 