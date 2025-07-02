# UVA Lab Software - Data Collection System

This project provides a comprehensive data collection and visualization system for laboratory equipment, supporting both local and distributed data acquisition scenarios.

## Project Structure

```
GUI-Webserver/
├── data_acquisition/          # Data acquisition components
│   ├── standalone_data_acquisition.py
│   ├── setup_data_acquisition.py
│   ├── config.py
│   └── requirements.txt
├── web_server/                # Web server and data collection
│   ├── data_collector.py
│   ├── start_data_collector.py
│   └── requirements.txt
├── database_utils/            # Database utilities and queries
│   ├── query_data.py
│   ├── test_system.py
│   ├── db.py
│   ├── schema.sql
│   └── requirements.txt
├── utils/                     # Utility scripts
│   ├── HMI_TCP_Sserver.py
│   ├── LabJack_Reader.py
│   ├── save_dava.py
│   └── gen.py
├── static/                    # Static web assets
│   ├── css/
│   ├── js/
│   └── csv/
├── templates/                 # HTML templates
├── docs/                      # Documentation
│   ├── README_Data_Acquisition.md
│   └── README_Data_Collector.md
└── __init__.py               # Main Flask application
```

## Quick Start

### Option 1: Local Data Collection (Single Machine)

If you want to run everything on one machine:

1. **Install dependencies:**
   ```bash
   pip install -r web_server/requirements.txt
   pip install -r database_utils/requirements.txt
   ```

2. **Start the data collector:**
   ```bash
   cd web_server
   python start_data_collector.py
   ```

3. **Start the HMI TCP server:**
   ```bash
   cd utils
   python HMI_TCP_Sserver.py
   ```

### Option 2: Distributed Data Collection (Two Machines)

If you want to run data acquisition on one machine and web server on another:

#### Machine A (Data Acquisition - Connected to Modbus devices):

1. **Copy data acquisition files to Machine A:**
   ```bash
   # Copy these files to Machine A
   data_acquisition/
   ```

2. **Setup and run:**
   ```bash
   cd data_acquisition
   python setup_data_acquisition.py
   python standalone_data_acquisition.py
   ```

#### Machine B (Web Server - Displays data):

1. **Install dependencies:**
   ```bash
   pip install -r web_server/requirements.txt
   pip install -r database_utils/requirements.txt
   ```

2. **Start the web server:**
   ```bash
   cd web_server
   python start_data_collector.py
   ```

## Components Overview

### Data Acquisition (`data_acquisition/`)

- **`standalone_data_acquisition.py`**: Reads data from Modbus devices and sends to remote server
- **`setup_data_acquisition.py`**: Interactive setup script for configuring remote server connection
- **`config.py`**: Configuration file for data acquisition settings

### Web Server (`web_server/`)

- **`data_collector.py`**: Flask server that receives and stores data
- **`start_data_collector.py`**: Startup script for the data collector
- **`requirements.txt`**: Dependencies for the web server

### Database Utilities (`database_utils/`)

- **`query_data.py`**: Command-line tool for querying and exporting data
- **`test_system.py`**: System testing and validation script
- **`db.py`**: Database connection and initialization utilities
- **`schema.sql`**: Database schema definition

### Utilities (`utils/`)

- **`HMI_TCP_Sserver.py`**: Modbus TCP client for reading device data
- **`LabJack_Reader.py`**: LabJack data acquisition utilities
- **`save_dava.py`**: Data saving utilities
- **`gen.py`**: Data generation utilities

## Configuration

### Data Acquisition Configuration

Edit `data_acquisition/config.py` to configure:
- Remote server URL
- Modbus device settings
- Data collection intervals
- Logging preferences

### Web Server Configuration

The web server runs on port 5000 by default. Modify `web_server/data_collector.py` to change:
- Server port
- Database location
- CSV monitoring intervals

## Data Flow

### Local Setup:
```
Modbus Devices → HMI_TCP_Server.py → Data Collector → SQLite Database → HTML Display
```

### Distributed Setup:
```
Modbus Devices → standalone_data_acquisition.py → Network → Data Collector → SQLite Database → HTML Display
```

## Monitoring and Maintenance

### View Data
```bash
cd database_utils
python query_data.py --summary
```

### Test System
```bash
cd database_utils
python test_system.py
```

### Export Data
```bash
cd database_utils
python query_data.py --export my_data.csv --limit 1000
```

## Documentation

- **Data Acquisition**: See `docs/README_Data_Acquisition.md`
- **Data Collector**: See `docs/README_Data_Collector.md`

## Troubleshooting

### Common Issues

1. **Cannot connect to Modbus devices**: Check IP address and network connectivity
2. **Cannot connect to remote server**: Verify server is running and network is accessible
3. **Database errors**: Check file permissions and disk space
4. **Port conflicts**: Change port numbers in configuration files

### Logs

- Data acquisition logs: `data_acquisition.log`
- Web server logs: Console output
- Database logs: Check SQLite database file

## Development

### Adding New Data Sources

1. Create new data acquisition script in `data_acquisition/`
2. Update database schema in `database_utils/schema.sql`
3. Modify data collector to handle new data format
4. Update HTML templates to display new data

### Adding New Utilities

1. Place utility scripts in `utils/`
2. Update documentation
3. Add to requirements if needed

## License

This project is part of the UVA Lab Software suite. 