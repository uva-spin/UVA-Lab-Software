# UVA Lab Software Suite

A comprehensive software ecosystem for the University of Virginia Physics Department's PTGroup laboratory, supporting particle physics research, NMR analysis, and laboratory automation.

## 🏗️ System Overview

This repository contains multiple integrated systems for laboratory operations:

- **Modern Data Acquisition System** (`GUI-Webserver/`) - Real-time monitoring and web visualization
- **Legacy NMR Control System** (`LANL-System/`) - LabVIEW-based NMR measurement and control
- **Database Utilities** - SQLite database management and monitoring
- **Discord Integration** - Automated alerts and system monitoring

## 🚀 Quick Start

### For New Users

1. **Choose Your System**:
   - **Data Acquisition & Monitoring**: Start with [GUI-Webserver README](GUI-Webserver/README.md)
   - **NMR Operations**: See [LANL System Guide](LANL-System/README.md)
   - **Database Access**: Check [Database Guide](docs/README_Database.md)
   - **Discord Monitoring**: See [Discord Bot Guide](docs/README_Discord_Bot.md)

2. **Prerequisites**:
   ```bash
   # Python 3.8+ required
   python --version
   
   # For NMR system: LabVIEW Runtime required
   # For data acquisition: Modbus devices accessible
   ```

3. **Quick Setup**:
   ```bash
   git clone https://github.com/your-username/UVA-Lab-Software.git
   cd UVA-Lab-Software
   
   # Follow specific component README for detailed setup
   ```

## 📁 Repository Structure

```
UVA-Lab-Software/
├── GUI-Webserver/              # Modern data acquisition system
│   ├── data_acquisition/       # Device readers and data collection
│   ├── web_server/            # Flask web interface
│   ├── static/                # Web assets (CSS, JS, images)
│   ├── templates/             # HTML templates
│   └── docs/                  # Component documentation
├── LANL-System/               # Legacy NMR control system
│   ├── rssmt/                 # NMR measurement software
│   ├── MKS/                   # MKS device control (LabVIEW)
│   ├── Documentation/         # Hardware manuals and guides
│   └── Rf switch/             # RF switching control
├── DatabaseReader.py          # Database utility class
├── Discord_Alert.py           # Discord monitoring bot
└── docs/                      # System-wide documentation
    ├── README_Architecture.md  # System architecture overview
    ├── README_Database.md      # Database schema and usage
    ├── README_Discord_Bot.md   # Discord bot setup and commands
    └── README_Hardware.md      # Hardware configuration guide
```

## 🔧 System Components

### 1. Data Acquisition System (GUI-Webserver)
**Purpose**: Real-time monitoring of laboratory equipment
- **Devices**: LabJack, Teledyne, MaxiGauge, LakeShore, IVC, QT PLC
- **Features**: Web dashboard, SQLite storage, multi-machine support
- **Status**: ✅ Active Development

### 2. NMR Control System (LANL-System) 
**Purpose**: Nuclear Magnetic Resonance measurements and control
- **Devices**: Netburner controllers, RF switches, MKS devices
- **Features**: LabVIEW interface, data logging, automated measurements
- **Status**: 🔒 Legacy (Stable)

### 3. Database & Monitoring
**Purpose**: Data storage and system health monitoring
- **Components**: SQLite database, Discord alerts, data export
- **Features**: Real-time alerts, data visualization, system status
- **Status**: ✅ Active

## 🎯 Common Use Cases

### Starting Data Collection
```bash
# Terminal 1: Start web server
cd GUI-Webserver/web_server
python start_data_collector.py

# Terminal 2: Start data acquisition
cd GUI-Webserver/data_acquisition/daq
python standalone_data_acquisition.py
```

### Monitoring System Health
```bash
# Check Discord bot status
python Discord_Alert.py

# Query database directly
python -c "from DatabaseReader import DatabaseReader; db = DatabaseReader('path/to/db'); print(db.list_tables())"
```

### Running Device Tests
```bash
cd GUI-Webserver/data_acquisition/device_testing
python run_all_daq_tests.py
```

## 📚 Documentation Guide

- **New to the lab?** → Start with [Architecture Overview](docs/README_Architecture.md)
- **Setting up data collection?** → [GUI-Webserver Guide](GUI-Webserver/README.md)
- **Working with NMR?** → [LANL System Guide](LANL-System/README.md)
- **Need data access?** → [Database Guide](docs/README_Database.md)
- **Want system alerts?** → [Discord Bot Guide](docs/README_Discord_Bot.md)
- **Hardware issues?** → [Hardware Guide](docs/README_Hardware.md)

## 🚨 Emergency Procedures

### System Down
1. Check Discord bot alerts
2. Verify database connectivity: `python DatabaseReader.py`
3. Restart data collection services
4. Contact lab administrator if issues persist

### Data Loss Prevention
- Database auto-backup enabled
- Local CSV backups in `data_logs/`
- Network storage backup on twist.phys.virginia.edu

## 👥 Support & Contact

- **Lab Administrator**: [Contact Info]
- **Technical Issues**: Open GitHub issue
- **Emergency**: Discord #lab-alerts channel
- **Documentation**: [Lab Wiki Link]

## 🔄 Recent Updates

- ✅ Async data acquisition improvements
- ✅ Comprehensive device testing suite
- ✅ Discord bot monitoring system
- ✅ Web interface enhancements
- 🔄 Documentation reorganization (in progress)

## 📄 License

MIT License - See LICENSE file for details

---

**⚠️ Important**: This system controls critical lab equipment. Always test changes in development environment first.
```

Now let me create the architecture overview document:

```markdown:/home/ptgroup/Documents/Devin/UVA-Lab-Software/docs/README_Architecture.md
# UVA Lab Software Architecture

## System Overview

The UVA Lab Software Suite is a hybrid system combining modern Python-based data acquisition with legacy LabVIEW NMR control systems. This document provides a high-level architectural overview for new users and developers.

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           UVA Lab Software Suite                                │
├─────────────────────────────┬───────────────────────────────────────────────────┤
│     Modern System           │              Legacy System                        │
│   (Python/Flask)            │            (LabVIEW/C++)                        │
├─────────────────────────────┼───────────────────────────────────────────────────┤
│                             │                                                   │
│  ┌─────────────────────────┐│  ┌─────────────────────────────────────────────┐ │
│  │   Data Acquisition      ││  │          NMR Control                        │ │
│  │                         ││  │                                             │ │
│  │  ┌─────────────────────┐││  │  ┌─────────────────────────────────────────┐│ │
│  │  │     Devices         │││  │  │        LabVIEW VIs                     ││ │
│  │  │                     │││  │  │                                         ││ │
│  │  │ • LabJack (USB)     │││  │  │ • NMR Measurement                      ││ │
│  │  │ • Teledyne (TCP)    │││  │  │ • RF Control                           ││ │
│  │  │ • MaxiGauge (TCP)   │││  │  │ • MKS Device Control                   ││ │
│  │  │ • LakeShore (Serial)│││  │  │ • Data Logging                         ││ │
│  │  │ • IVC (Serial)      │││  │  │                                         ││ │
│  │  │ • QT PLC (Modbus)   │││  │  └─────────────────────────────────────────┘│ │
│  │  └─────────────────────┘││  │                                             │ │
│  │           │              ││  │  ┌─────────────────────────────────────────┐│ │
│  │           ▼              ││  │  │      Hardware Control                  ││ │
│  │  ┌─────────────────────┐││  │  │                                         ││ │
│  │  │   Device Readers    │││  │  │ • Netburner Controllers                ││ │
│  │  │                     │││  │  │ • RF Switches                          ││ │
│  │  │ • _LabJackReader    │││  │  │ • FPGA Communication                   ││ │
│  │  │ • _TeledyneReader   │││  │  │ • VME Bus Control                      ││ │
│  │  │ • _MaxiGaugeReader  │││  │  └─────────────────────────────────────────┘│ │
│  │  │ • _LakeShoreReader  │││  │                                             │ │
│  │  │ • _IVCReader        │││  └─────────────────────────────────────────────┘ │
│  │  │ • _QTReader         │││                                                  │
│  │  └─────────────────────┘││                                                  │
│  │           │              ││                                                  │
│  │           ▼              ││                                                  │
│  │  ┌─────────────────────┐││                                                  │
│  │  │  Flask Web Server   │││                                                  │
│  │  │                     │││                                                  │
│  │  │ • HTTP Endpoints    │││                                                  │
│  │  │ • Data Collection   │││                                                  │
│  │  │ • Web Dashboard     │││                                                  │
│  │  └─────────────────────┘││                                                  │
│  │           │              ││                                                  │
│  └───────────┼──────────────┘│                                                  │
│              │               │                                                  │
└──────────────┼───────────────┼──────────────────────────────────────────────────┘
               │               │
               ▼               ▼
    ┌─────────────────────────────────────────────────────────┐
    │                 Shared Components                       │
    │                                                         │
    │  ┌─────────────────────┐  ┌─────────────────────────────┐│
    │  │   SQLite Database   │  │     Discord Bot             ││
    │  │                     │  │                             ││
    │  │ • HMI Data          │  │ • System Monitoring         ││
    │  │ • LabJack Data      │  │ • Alert System              ││
    │  │ • Device Readings   │  │ • Status Reports            ││
    │  │ • Timestamps        │  │ • Emergency Notifications   ││
    │  └─────────────────────┘  └─────────────────────────────┘│
    └─────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Modern System Data Flow
```
Hardware Devices → Device Readers → Flask Server → SQLite Database → Web Interface
                                                    ↓
                                            Discord Bot (Monitoring)
```

### Legacy System Data Flow
```
NMR Hardware → LabVIEW VIs → Data Files → Manual Analysis
```

## 🏢 Deployment Architecture

### Single Machine Setup (Development/Testing)
```
┌─────────────────────────────────────┐
│           Lab Computer              │
│                                     │
│  ┌─────────────────────────────────┐│
│  │     Data Acquisition            ││
│  │  • Device connections           ││
│  │  • standalone_data_acquisition  ││
│  └─────────────────────────────────┘│
│                │                    │
│                ▼                    │
│  ┌─────────────────────────────────┐│
│  │       Web Server                ││
│  │  • Flask application            ││
│  │  • SQLite database              ││
│  │  • Web dashboard                ││
│  └─────────────────────────────────┘│
│                │                    │
│                ▼                    │
│  ┌─────────────────────────────────┐│
│  │      Discord Bot                ││
│  │  • System monitoring            ││
│  │  • Alert notifications          ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### Distributed Setup (Production)
```
┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
│        Machine A (DAQ)              │    │        Machine B (Web)              │
│                                     │    │                                     │
│  ┌─────────────────────────────────┐│    │  ┌─────────────────────────────────┐│
│  │     Device Connections          ││    │  │       Web Server                ││
│  │  • LabJack (USB)                ││    │  │  • Flask application            ││
│  │  • Teledyne (TCP)               ││    │  │  • SQLite database              ││
│  │  • MaxiGauge (TCP)              ││    │  │  • Web dashboard                ││
│  │  • LakeShore (Serial)           ││    │  └─────────────────────────────────┘│
│  │  • IVC (Serial)                 ││    │                │                    │
│  │  • QT PLC (Modbus)              ││    │                ▼                    │
│  └─────────────────────────────────┘│    │  ┌─────────────────────────────────┐│
│                │                    │    │  │      Discord Bot                ││
│                ▼                    │    │  │  • System monitoring            ││
│  ┌─────────────────────────────────┐│    │  │  • Alert notifications          ││
│  │     Data Acquisition            ││    │  └─────────────────────────────────┘│
│  │  • standalone_data_acquisition  ││    │                                     │
│  │  • HTTP POST to Machine B       ││────┼─→ HTTP Endpoint                     │
│  └─────────────────────────────────┘│    └─────────────────────────────────────┘
└─────────────────────────────────────┘
```

## 🔧 Component Responsibilities

### Data Acquisition Layer
- **Device Readers**: Abstract device communication protocols
- **Data Collection**: Async polling and data aggregation
- **Error Handling**: Device disconnection and retry logic
- **Local Backup**: CSV file generation for data safety

### Web Server Layer
- **HTTP API**: RESTful endpoints for data submission and retrieval
- **Database Management**: SQLite operations and schema maintenance
- **Web Interface**: Real-time dashboard with data visualization
- **Authentication**: Basic security for data access

### Monitoring Layer
- **Discord Bot**: Automated alerts and system status
- **Health Checks**: Database connectivity and data freshness
- **Alert Logic**: Threshold-based notifications
- **Status Reports**: Scheduled system updates

### Legacy Integration
- **LabVIEW VIs**: NMR measurement and control interfaces
- **Hardware Control**: Direct device communication
- **Data Export**: CSV and database integration
- **Manual Operation**: Interactive measurement tools

## 🌐 Network Architecture

### IP Address Scheme
```
Laboratory Network: 172.29.36.0/24

Device Assignments:
├── QT PLC: 172.29.36.195 (Modbus TCP, Ports 502/503)
├── Teledyne: 172.29.36.192 (TCP, Port 101)
├── MaxiGauge: 172.29.36.194 (TCP, Port 8000)
├── Web Server: 128.143.231.224 (HTTP, Port 5000)
└── Network Storage: twist.phys.virginia.edu
```

### Communication Protocols
- **Modbus TCP**: QT PLC communication
- **TCP/IP**: Teledyne and MaxiGauge devices
- **Serial**: LakeShore and IVC controllers
- **USB**: LabJack data acquisition units
- **HTTP**: Web server API and dashboard

## 🔐 Security Considerations

### Network Security
- Internal network access only
- No external internet exposure
- Device-specific port restrictions

### Data Security
- SQLite database with file-level permissions
- Discord bot token protection
- Configuration file security

### Access Control
- Discord bot command restrictions
- Web interface basic authentication
- Database read-only access for monitoring

## 📊 Performance Characteristics

### Data Throughput
- **Sampling Rate**: 1-10 seconds per device
- **Data Points**: ~30 values per collection cycle
- **Storage Rate**: ~1MB per day (typical operation)
- **Web Updates**: Real-time via JavaScript polling

### System Resources
- **CPU Usage**: Low (async I/O optimized)
- **Memory**: <100MB typical operation
- **Disk Space**: Database grows ~1GB per year
- **Network**: Minimal bandwidth requirements

## 🔄 Integration Points

### Modern ↔ Legacy Integration
- Shared network storage for data exchange
- Common database schema for measurements
- Coordinated hardware access (mutual exclusion)

### External System Integration
- Discord API for notifications
- Network file system for data backup
- Web browser access for monitoring

## 🚀 Scalability Considerations

### Horizontal Scaling
- Multiple data acquisition machines
- Load-balanced web servers
- Distributed device monitoring

### Vertical Scaling
- Database optimization for large datasets
- Async processing for high-frequency data
- Memory-efficient data structures

---

This architecture supports both current operations and future expansion while maintaining compatibility with existing legacy systems.
```

Now let me create the database documentation:

```markdown:/home/ptgroup/Documents/Devin/UVA-Lab-Software/docs/README_Database.md
# Database System Guide

## Overview

The UVA Lab Software uses SQLite as its primary database for storing real-time laboratory data. This guide covers database schema, access patterns, and maintenance procedures.

## 📊 Database Schema

### Core Tables

#### HMI Table
Stores data from the QT PLC system (18 values)
```sql
CREATE TABLE HMI (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    pt501_ai REAL,      -- Dewar Pressure
    pt502_ai REAL,      -- Inlet Pressure  
    ti501_ai REAL,      -- ColdHead Temp 1
    ti502_ai REAL,      -- ColdHead Temp 2
    ti503_ai REAL,      -- ColdHead Temp 3
    ti504_ai REAL,      -- ColdHead Temp 4
    ti505_ai REAL,      -- ColdHead Temp 5
    fc501_ai REAL,      -- Inlet Flow
    fc502_ai REAL,      -- Outlet Flow
    lit501_ai REAL,     -- Liquid Helium Level
    ait501_ai REAL,     -- Helium Purity
    -- Additional HMI channels...
);
```

#### Labjack Table
Stores data from LabJack devices (pressure/temperature sensors)
```sql
CREATE TABLE Labjack (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    root_exhaust_pressure REAL,    -- Torr
    buffer_pressure REAL,          -- PSI
    magnet_pressure REAL,          -- PSI
    purifier_inlet_pressure REAL,  -- PSI
    fridge_vapor_pressure REAL,    -- PSI
    thermocouple REAL              -- Volts (LN2 level)
);
```

#### Teledyne Table
Stores flow meter data from Teledyne device
```sql
CREATE TABLE Teledyne (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    flow_rate_1 REAL,    -- SLM
    flow_rate_2 REAL,    -- SLM
    flow_rate_3 REAL     -- SLM
);
```

#### MaxiGauge Table
Stores pressure readings from Pfeiffer MaxiGauge
```sql
CREATE TABLE MaxiGauge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    pressure_1 REAL,     -- mbar
    pressure_2 REAL,     -- mbar
    pressure_3 REAL,     -- mbar
    pressure_4 REAL,     -- mbar
    pressure_5 REAL,     -- mbar
    pressure_6 REAL      -- mbar
);
```

#### LakeShore Table
Stores temperature data from LakeShore controllers
```sql
CREATE TABLE LakeShore (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    port TEXT NOT NULL,           -- COM port identifier
    temperature REAL,             -- Kelvin
    sensor_status TEXT            -- Status string
);
```

#### IVC Table
Stores pressure data from IVC controller
```sql
CREATE TABLE IVC (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    pressure REAL,                -- Torr
    unit TEXT,                    -- Unit string
    status TEXT                   -- Status string
);
```

## 🔧 Database Access

### Using DatabaseReader Class

```python
from DatabaseReader import DatabaseReader

# Initialize database connection
db = DatabaseReader("path/to/flaskr.sqlite")

# List all tables
tables = db.list_tables()
print(f"Available tables: {tables}")

# Get table schema
schema = db.get_schema("HMI")
print(f"HMI table columns: {schema}")

# Get latest values
latest_pressure = db.get_latest_value("HMI", "pt501_ai")
latest_temp = db.get_latest_value("Labjack", "thermocouple")

# Get last timestamp
last_update = db.get_last_timestamp("HMI")

# Close connection
db.close()
```

### Direct SQL Access

```python
import sqlite3

# Connect to database (read-only)
conn = sqlite3.connect("file:flaskr.sqlite?mode=ro", uri=True)
cursor = conn.cursor()

# Query recent data
cursor.execute("""
    SELECT timestamp, pt501_ai, pt502_ai 
    FROM HMI 
    ORDER BY timestamp DESC 
    LIMIT 10
""")
results = cursor.fetchall()

# Close connection
conn.close()
```

## 📈 Data Patterns and Queries

### Common Query Patterns

#### Latest System Status
```sql
SELECT 
    h.timestamp,
    h.pt501_ai as dewar_pressure,
    h.pt502_ai as inlet_pressure,
    (h.ti501_ai + h.ti502_ai + h.ti503_ai + h.ti504_ai + h.ti505_ai)/5 as avg_coldhead_temp,
    h.fc501_ai as inlet_flow,
    h.fc502_ai as outlet_flow,
    h.lit501_ai as helium_level,
    l.thermocouple as ln2_level
FROM HMI h
LEFT JOIN Labjack l ON l.id = (SELECT MAX(id) FROM Labjack)
ORDER BY h.timestamp DESC
LIMIT 1;
```

#### Historical Trends (Last 24 Hours)
```sql
SELECT 
    datetime(timestamp) as time,
    pt501_ai as dewar_pressure,
    lit501_ai as helium_level
FROM HMI 
WHERE timestamp >= datetime('now', '-1 day')
ORDER BY timestamp;
```

#### Alert Conditions
```sql
-- Check for critical conditions
SELECT 
    'LN2_LOW' as alert_type,
    timestamp,
    thermocouple as value
FROM Labjack 
WHERE thermocouple >= 2.5  -- Threshold for LN2 refill
ORDER BY timestamp DESC
LIMIT 1;

SELECT 
    'COLDHEAD_TEMP' as alert_type,
    timestamp,
    ti501_ai, ti502_ai, ti503_ai, ti504_ai, ti505_ai
FROM HMI 
WHERE ti501_ai < 3.0 OR ti501_ai > 5.0
   OR ti502_ai < 3.0 OR ti502_ai > 5.0
   OR ti503_ai < 3.0 OR ti503_ai > 5.0
   OR ti504_ai < 3.0 OR ti504_ai > 5.0
   OR ti505_ai < 3.0 OR ti505_ai > 5.0
ORDER BY timestamp DESC
LIMIT 1;
```

## 🔄 Data Export and Backup

### Export to CSV
```python
import sqlite3
import csv
from datetime import datetime, timedelta

def export_recent_data(db_path, hours=24):
    """Export recent data to CSV file"""
    conn = sqlite3.connect(db_path)
    
    # Calculate time threshold
    threshold = datetime.now() - timedelta(hours=hours)
    
    # Query data
    query = """
    SELECT h.timestamp, h.pt501_ai, h.pt502_ai, h.lit501_ai,
           l.thermocouple, t.flow_rate_1, m.pressure_1
    FROM HMI h
    LEFT JOIN Labjack l ON date(h.timestamp) = date(l.timestamp)
    LEFT JOIN Teledyne t ON date(h.timestamp) = date(t.timestamp)  
    LEFT JOIN MaxiGauge m ON date(h.timestamp) = date(m.timestamp)
    WHERE h.timestamp >= ?
    ORDER BY h.timestamp
    """
    
    cursor = conn.execute(query, (threshold.isoformat(),))
    
    # Write to CSV
    with open(f'lab_data_{datetime.now().strftime("%Y%m%d_%H%M")}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'dewar_pressure', 'inlet_pressure', 
                        'helium_level', 'ln2_level', 'flow_rate', 'pressure'])
        writer.writerows(cursor.fetchall())
    
    conn.close()
```

### Automated Backup
```bash
#!/bin/bash
# Database backup script
DB_PATH="/path/to/flaskr.sqlite"
BACKUP_DIR="/backup/database"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
sqlite3 "$DB_PATH" ".backup $BACKUP_DIR/flaskr_backup_$DATE.sqlite"

# Compress backup
gzip "$BACKUP_DIR/flaskr_backup_$DATE.sqlite"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "flaskr_backup_*.sqlite.gz" -mtime +30 -delete

echo "Backup completed: flaskr_backup_$DATE.sqlite.gz"
```

## 🔍 Database Maintenance

### Check Database Health
```python
def check_database_health(db_path):
    """Perform database health checks"""
    db = DatabaseReader(db_path)
    
    # Check table existence
    tables = db.list_tables()
    expected_tables = ['HMI', 'Labjack', 'Teledyne', 'MaxiGauge', 'LakeShore', 'IVC']
    missing_tables = set(expected_tables) - set(tables)
    
    if missing_tables:
        print(f"⚠️ Missing tables: {missing_tables}")
    
    # Check data freshness
    for table in tables:
        last_timestamp = db.get_last_timestamp(table)
        if last_timestamp:
            age = datetime.now() - last_timestamp
            if age.total_seconds() > 300:  # 5 minutes
                print(f"⚠️ {table} data is stale: {age}")
            else:
                print(f"✅ {table} data is fresh")
        else:
            print(f"❌ {table} has no data")
    
    db.close()
```

### Database Optimization
```sql
-- Vacuum database to reclaim space
VACUUM;

-- Analyze tables for query optimization
ANALYZE;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_hmi_timestamp ON HMI(timestamp);
CREATE INDEX IF NOT EXISTS idx_labjack_timestamp ON Labjack(timestamp);
CREATE INDEX IF NOT EXISTS idx_teledyne_timestamp ON Teledyne(timestamp);
CREATE INDEX IF NOT EXISTS idx_maxigauge_timestamp ON MaxiGauge(timestamp);
```

### Data Retention Policy
```python
def cleanup_old_data(db_path, days_to_keep=365):
    """Remove data older than specified days"""
    conn = sqlite3.connect(db_path)
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    tables = ['HMI', 'Labjack', 'Teledyne', 'MaxiGauge', 'LakeShore', 'IVC']
    
    for table in tables:
        cursor = conn.execute(f"""
            DELETE FROM {table} 
            WHERE timestamp < ?
        """, (cutoff_date.isoformat(),))
        
        print(f"Deleted {cursor.rowcount} old records from {table}")
    
    conn.commit()
    conn.close()
```

## 🚨 Monitoring and Alerts

### Database Monitoring Queries
```python
def monitor_database_status(db_path):
    """Monitor database for alert conditions"""
    db = DatabaseReader(db_path)
    
    alerts = []
    
    # Check LN2 level
    ln2_level = db.get_latest_value("Labjack", "thermocouple")
    if ln2_level and ln2_level >= 2.5:
        alerts.append(f"LN2 level critical: {ln2_level:.3f}V")
    
    # Check coldhead temperatures
    coldhead_sensors = ["ti501_ai", "ti502_ai", "ti503_ai", "ti504_ai", "ti505_ai"]
    for sensor in coldhead_sensors:
        temp = db.get_latest_value("HMI", sensor)
        if temp and (temp < 3.0 or temp > 5.0):
            alerts.append(f"Coldhead {sensor} out of range: {temp:.2f}V")
    
    # Check data freshness
    last_update = db.get_last_timestamp("HMI")
    if last_update:
        age = datetime.now() - last_update
        if age.total_seconds() > 300:
            alerts.append(f"Data stale: {age}")
    
    db.close()
    return alerts
```

## 🔧 Troubleshooting

### Common Issues

#### Database Locked
```bash
# Check for processes using the database
lsof /path/to/flaskr.sqlite

# If needed, kill processes and restart services
sudo systemctl restart data-collector
```

#### Corrupted Database
```bash
# Check database integrity
sqlite3 flaskr.sqlite "PRAGMA integrity_check;"

# Repair if needed
sqlite3 flaskr.sqlite ".recover" | sqlite3 flaskr_recovered.sqlite
```

#### Performance Issues
```sql
-- Check table sizes
SELECT name, COUNT(*) as row_count 
FROM sqlite_master, (SELECT name FROM sqlite_master WHERE type='table') 
GROUP BY name;

-- Check query performance
EXPLAIN QUERY PLAN SELECT * FROM HMI WHERE timestamp > '2024-01-01' ORDER BY timestamp DESC LIMIT 10;
```

## 📊 Database Location

### Production Database
```
Path: Z:\spin\instance\flaskr.sqlite
Network: \\twist.phys.virginia.edu\www\spin\instance\flaskr.sqlite
Local: /var/lib/lab-software/flaskr.sqlite
```

### Development Database
```
Path: GUI-Webserver/Testing/instance/flaskr.sqlite
```

---

For additional database support, check the Discord bot commands or contact the lab administrator.
```

Now let me create the Discord bot documentation:

```markdown:/home/ptgroup/Documents/Devin/UVA-Lab-Software/docs/README_Discord_Bot.md
# Discord Bot Monitoring System

## Overview

The Discord bot provides automated monitoring and alerting for the UVA lab systems. It continuously monitors database health, equipment status, and sends real-time alerts to Discord channels.

## 🤖 Bot Features

### Real-time Monitoring
- **LN2 Level Monitoring**: Alerts when liquid nitrogen needs refilling
- **Temperature Monitoring**: Coldhead temperature range checks
- **Data Freshness**: Alerts when data collection stops
- **System Health**: Periodic status updates

### Interactive Commands
- **Status Queries**: Get current system readings
- **Data Checks**: Verify database connectivity
- **Manual Updates**: Trigger status reports
- **Help System**: List available commands

## 🚀 Quick Start

### Prerequisites
```bash
# Required Python packages
pip install discord.py python-dotenv pytz apscheduler

# Discord bot token (from Discord Developer Portal)
# Channel IDs for notifications
```

### Environment Setup
Create a `.env` file in the root directory:
```env
# Discord Configuration
DISCORD_TOKEN=your_bot_token_here
BOT_CHANNEL_ID=1234567890123456789
UVALAB_CHANNEL_ID=1234567890123456789

# Alert Thresholds
LN2_THRESHOLD=2.5
ColdHead_TEMP_HIGH=5.0
ColdHead_TEMP_LOW=3.0
```

### Running the Bot
```bash
# Start the Discord bot
python Discord_Alert.py

# Expected output:
# ✅ Bot is online as LabBot#1234
# 👁️👄👁️ Always watching...
```

## 📱 Discord Commands

### Basic Commands

#### `!Commands`
Shows list of available bot commands
```
📖 **Available Commands**:
• !LN2 – Show the current LN2 thermocouple voltage
• !ShutDown – Shut down the bot (restricted access)
• !Update – Give a status report
• !Commands – Show this help message
```

#### `!Update`
Provides comprehensive system status
```
📊 **Automated System Status Update** 📊
• Dewar Pressure: 1.23 PSI
• Inlet Pressure: 4.56 PSI  
• Avg ColdHead Temp: 4.12V
• Inlet Flow: 2.34 SLM
• Outlet Flow: 2.11 SLM
• Liquid Helium: 87.5%
• Helium Purity: 99.987%
• ColdHead Alert: False
• LN2 Alert: False
```

#### `!LN2`
Shows current liquid nitrogen thermocouple reading
```
🌡️ LN2 Thermocouple Reading:
• Raw Voltage: 1.847 V
```

#### `!Data`
Shows timestamp of last database entry
```
🕒 Last data entry: 2024-01-15 14:23:45
```

### Administrative Commands

#### `!ShutDown`
Shuts down the bot (restricted to authorized users)
```
⚠️ Shutting down bot...
:wave: Bye~ :skull:
```

### Fun Commands

#### `!Devin`, `!Dima`, `!Jay`
Interactive greetings between lab members
```
!Devin → "Hello Dima."
!Dima → "Hello Jay."  
!Jay → "Hello Devin."
```

## 🚨 Automated Alerts

### LN2 Level Alert
**Trigger**: Thermocouple voltage ≥ 2.5V
**Frequency**: Once per alert condition
**Message**: 
```
🚨 **ALERT:** Purifier needs to be refilled!
```

### Coldhead Temperature Alert  
**Trigger**: Any coldhead sensor < 3.0V or > 5.0V
**Frequency**: Once per alert condition
**Message**:
```
🚨 **ColdHead Temp ALERT** 🚨
• ti501_ai = 2.15 V 🥶 Too Cold!
• ti503_ai = 5.67 V 🥵 Too Hot!

Any value < 3.0 or > 5.0 is considered unsafe!
```

### Data Staleness Alert
**Trigger**: No new data for > 5 minutes
**Frequency**: Once per alert condition  
**Message**:
```
🚨 **ALERT:** The database could be down!
Last data timestamp: 2024-01-15 14:18:32
```

## ⚙️ Configuration

### Alert Thresholds
```python
# Environment variables (in .env file)
LN2_THRESHOLD = 2.5           # Volts - LN2 refill needed
ColdHead_TEMP_HIGH = 5.0      # Volts - Too hot
ColdHead_TEMP_LOW = 3.0       # Volts - Too cold

# Timing settings
CHECK_INTERVAL = 60           # Seconds between checks
DATA_STALE_THRESHOLD = 300    # Seconds (5 minutes)
```

### Channel Configuration
```python
# Discord channel IDs
BOT_CHANNEL_ID = 1234567890123456789      # Bot commands and alerts
UVALAB_CHANNEL_ID = 1234567890123456789   # Status updates
```

### Database Configuration
```python
# Database path (modify as needed)
db_path = r"Z:\spin\instance\flaskr.sqlite"
# Alternative: "/var/lib/lab-software/flaskr.sqlite"
```

## 🔧 Technical Details

### Bot Architecture
```python
# Core components
@bot.event
async def on_ready():
    # Bot startup initialization
    check_thermocouple.start()
    check_ColdHeads.start()  
    check_data_staleness.start()

@tasks.loop(seconds=60.0)
async def check_thermocouple():
    # Monitor LN2 levels
    
@tasks.loop(seconds=60.0)  
async def check_ColdHeads():
    # Monitor coldhead temperatures
    
@tasks.loop(seconds=60.0)
async def check_data_staleness():
    # Check database connectivity
```

### Database Integration
```python
from DatabaseReader import DatabaseReader

# Database queries
reader = DatabaseReader(db_path)
ln2_level = reader.get_latest_value("Labjack", "thermocouple")
last_timestamp = reader.get_last_timestamp("HMI")
coldhead_temp = reader.get_latest_value("HMI", "ti501_ai")
reader.close()
```

### Error Handling
```python
try:
    # Database operations
    reader = DatabaseReader(db_path)
    value = reader.get_latest_value("table", "column")
    reader.close()
except Exception as e:
    print(f"[Monitor Error] {e}")
    # Continue monitoring without crashing
```

## 🛠️ Setup Instructions

### 1. Discord Bot Creation
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Go to "Bot" section
4. Create bot and copy token
5. Enable necessary intents:
   - Message Content Intent
   - Server Members Intent (if needed)

### 2. Server Setup
1. Invite bot to Discord server with appropriate permissions:
   - Send Messages
   - Read Message History
   - Use Slash Commands (optional)
2. Note channel IDs for configuration

### 3. Environment Configuration
```bash
# Create .env file
cat > .env << EOF
DISCORD_TOKEN=your_actual_bot_token
BOT_CHANNEL_ID=your_bot_channel_id
UVALAB_CHANNEL_ID=your_lab_channel_id
LN2_THRESHOLD=2.5
ColdHead_TEMP_HIGH=5.0
ColdHead_TEMP_LOW=3.0
EOF
```

### 4. Database Access
Ensure bot has read access to the SQLite database:
```bash
# Check database permissions
ls -la /path/to/flaskr.sqlite

# If needed, adjust permissions
chmod 644 /path/to/flaskr.sqlite
```

### 5. Service Setup (Optional)
Create systemd service for automatic startup:
```bash
sudo tee /etc/systemd/system/discord-bot.service << EOF
[Unit]
Description=Lab Discord Bot
After=network.target

[Service]
Type=simple
User=labuser
WorkingDirectory=/path/to/UVA-Lab-Software
ExecStart=/usr/bin/python3 Discord_Alert.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```

## 📊 Monitoring Dashboard

### Bot Status Check
```python
# Check if bot is running
import psutil

def check_bot_status():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'Discord_Alert.py' in ' '.join(proc.info['cmdline'] or []):
            return f"Bot running (PID: {proc.info['pid']})"
    return "Bot not running"
```

### Alert History
The bot maintains internal state to prevent alert spam:
```python
# Global alert state variables
alert_triggered = False              # LN2 alert
alert_triggered_ColdHeads = False    # Temperature alert  
alert_triggered_stale_data = False   # Data freshness alert
```

## 🔍 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check bot process
ps aux | grep Discord_Alert.py

# Check logs
tail -f /var/log/discord-bot.log

# Restart bot
sudo systemctl restart discord-bot
```

#### Database Connection Issues
```python
# Test database access
from DatabaseReader import DatabaseReader
try:
    db = DatabaseReader("path/to/flaskr.sqlite")
    tables = db.list_tables()
    print(f"Database OK: {tables}")
    db.close()
except Exception as e:
    print(f"Database Error: {e}")
```

#### Discord API Issues
```python
# Check Discord connection
import discord
import asyncio

async def test_connection():
    client = discord.Client()
    try:
        await client.login('your_token')
        print("Discord connection OK")
    except Exception as e:
        print(f"Discord Error: {e}")
    finally:
        await client.close()

asyncio.run(test_connection())
```

#### Permission Issues
```bash
# Check file permissions
ls -la flaskr.sqlite
ls -la .env

# Fix permissions if needed
chmod 644 flaskr.sqlite
chmod 600 .env  # Keep token secure
```

### Debug Mode
Enable debug logging by modifying the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"[DEBUG] LN2 Level: {ln2_level}")
print(f"[DEBUG] Alert State: {alert_triggered}")
```

## 🔒 Security Considerations

### Token Security
- Store Discord token in `.env` file
- Never commit tokens to version control
- Restrict file permissions: `chmod 600 .env`
- Rotate tokens periodically

### Access Control
```python
# Authorized users for administrative commands
allowed_user_ids = [274700280409489409, 1319339525385752661, 940096349586743328]

@bot.command(name='ShutDown')
async def shutdown_bot(ctx):
    if ctx.author.id not in allowed_user_ids:
        await ctx.send("❌ You are not authorized to shut me down.")
        return
```

### Channel Restrictions
```python
# Restrict commands to specific channels
if ctx.channel.id != BOT_CHANNEL_ID:
    return  # Ignore commands from other channels
```

## 📈 Usage Statistics

### Command Usage Tracking
```python
import json
from datetime import datetime

def log_command_usage(command, user, channel):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'command': command,
        'user': str(user),
        'channel': str(channel)
    }
    
    with open('bot_usage.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

### Alert Frequency Analysis
```python
def analyze_alert_frequency():
    # Parse log files to analyze alert patterns
    # Useful for adjusting thresholds and timing
    pass
```

---

For Discord bot support, ping @admin in the #lab-alerts channel or check the bot logs.
```

Now let me create the hardware configuration guide:

```markdown:/home/ptgroup/Documents/Devin/UVA-Lab-Software/docs/README_Hardware.md
# Hardware Configuration Guide

## Overview

This guide covers the physical hardware setup, network configuration, and device connections for the UVA Lab Software system. It includes both modern data acquisition devices and legacy NMR control hardware.

## 🔧 Hardware Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Laboratory Network                                    │
│                         172.29.36.0/24                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   Data Acq PC   │    │   Web Server    │    │   NMR System    │            │
│  │  172.29.36.100  │    │  128.143.231.224│    │  172.29.36.101  │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           ├─USB────────────────────┼─TCP/IP────────────────┼─Serial/VME        │
│           │                       │                       │                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │  LabJack U3/T4  │    │   QT PLC        │    │  Netburner      │            │
│  │  (USB)          │    │ 172.29.36.195   │    │  Controllers    │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│                                 │                                               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   Teledyne      │    │   MaxiGauge     │    │   MKS Devices   │            │
│  │ 172.29.36.192   │    │ 172.29.36.194   │    │   (LabVIEW)     │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                                   │
│  │   LakeShore     │    │      IVC        │                                   │
│  │   (COM4/5)      │    │    (COM7)       │                                   │
│  └─────────────────┘    └─────────────────┘                                   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🖥️ Computer Systems

### Data Acquisition Computer
**Purpose**: Interface with laboratory devices
**OS**: Windows 10/11 or Linux
**Requirements**:
- USB ports for LabJack devices
- Serial ports (COM4, COM5, COM7) for serial devices
- Network connectivity for TCP devices
- Python 3.8+ environment

**Software**:
```bash
# Required Python packages
pip install u3 numpy pyModbusTCP pyserial asyncio
```

### Web Server Computer  
**Purpose**: Data collection, storage, and visualization
**OS**: Linux (preferred) or Windows
**Requirements**:
- Network connectivity
- SQLite database storage
- Web server capabilities
- Discord bot hosting

**Software**:
```bash
# Required packages
pip install flask sqlite3 discord.py python-dotenv
```

### NMR Control Computer
**Purpose**: LabVIEW-based NMR measurements
**OS**: Windows (LabVIEW required)
**Requirements**:
- LabVIEW Runtime Engine
- VME bus interface cards
- Serial communication ports
- Network connectivity

## 📡 Network Devices

### QT PLC (172.29.36.195)
**Device**: Programmable Logic Controller
**Protocol**: Modbus TCP
**Ports**: 502 (floating point), 503 (integer)
**Data**: 18 process values (pressure, temperature, flow, level)

**Configuration**:
```python
PLC_IP = "172.29.36.195"
UNIT_ID = 2
INT_PORT = 503
FLOAT_PORT = 502
NUM_REG_TO_READ = 36
```

**Network Test**:
```bash
# Test connectivity
ping 172.29.36.195
telnet 172.29.36.195 502
telnet 172.29.36.195 503
```

### Teledyne THCD-401 (172.29.36.192)
**Device**: Flow Meter Controller
**Protocol**: TCP/IP
**Port**: 101
**Data**: 3 flow rate channels (SLM)

**Configuration**:
```python
TELEDYNE_IP = "172.29.36.192"
TELEDYNE_PORT = 101
```

**Network Test**:
```bash
ping 172.29.36.192
telnet 172.29.36.192 101
```

### Pfeiffer MaxiGauge (172.29.36.194)
**Device**: Multi-Channel Pressure Controller  
**Protocol**: TCP/IP
**Port**: 8000
**Data**: 6 pressure sensors (mbar, scientific notation)

**Configuration**:
```python
MAXIGAUGE_IP = "172.29.36.194"
MAXIGAUGE_PORT = 8000
```

**Network Test**:
```bash
ping 172.29.36.194
telnet 172.29.36.194 8000
```

## 🔌 USB Devices

### LabJack U3 (Device 1)
**Purpose**: Pressure and temperature sensors
**Connection**: USB
**Channels**: 6 analog inputs
**Data**:
- Root exhaust pressure (Torr)
- Buffer pressure (PSI)
- Magnet pressure (PSI)
- Purifier inlet pressure (PSI)
- Fridge vapor pressure (PSI)
- Thermocouple voltage (LN2 level)

**Device Detection**:
```python
import u3
try:
    device = u3.U3()
    print(f"LabJack U3 found: {device.configU3()}")
    device.close()
except:
    print("LabJack U3 not found")
```

### LabJack T4 (Device 2)  
**Purpose**: Flow meter inputs
**Connection**: USB
**Channels**: 2 analog inputs
**Data**:
- Microwave flow meter (SLM)
- Heat exchanger flow meter (SLM)

**Device Detection**:
```python
from labjack import ljm
try:
    handle = ljm.openS("T4", "USB", "ANY")
    info = ljm.getHandleInfo(handle)
    print(f"LabJack T4 found: {info}")
    ljm.close(handle)
except:
    print("LabJack T4 not found")
```

## 📻 Serial Devices

### LakeShore Temperature Controllers
**Purpose**: Cryogenic temperature monitoring
**Connection**: Serial (RS-232)
**Ports**: COM4, COM5
**Protocol**: LakeShore serial protocol
**Data**: Temperature readings (Kelvin)

**Configuration**:
```python
# COM4 - Target stick temperature
LAKESHORE_PORT_1 = "COM4"
BAUD_RATE = 9600
DATA_BITS = 8
STOP_BITS = 1
PARITY = "N"

# COM5 - Fridge temperature  
LAKESHORE_PORT_2 = "COM5"
```

**Serial Test**:
```python
import serial
try:
    ser = serial.Serial("COM4", 9600, timeout=1)
    ser.write(b"KRDG?\r\n")  # Read temperature
    response = ser.readline()
    print(f"LakeShore response: {response}")
    ser.close()
except:
    print("LakeShore not responding on COM4")
```

### IVC Pressure Controller
**Purpose**: Vacuum pressure monitoring
**Connection**: Serial (RS-232)
**Port**: COM7
**Protocol**: Custom IVC protocol
**Data**: Pressure readings (Torr)

**Configuration**:
```python
IVC_PORT = "COM7"
BAUD_RATE = 9600
```

**Serial Test**:
```python
import serial
try:
    ser = serial.Serial("COM7", 9600, timeout=1)
    ser.write(b"?P\r")  # Query pressure
    response = ser.readline()
    print(f"IVC response: {response}")
    ser.close()
except:
    print("IVC not responding on COM7")
```

## 🏗️ Legacy NMR Hardware

### Netburner Controllers
**Purpose**: NMR measurement control
**Connection**: Ethernet + VME bus
**Protocol**: Custom TCP protocol
**Features**:
- 4-channel DAC control
- 4-channel ADC reading
- RF attenuation control
- Digital I/O control

**VME Bus Configuration**:
```cpp
// VME bus pin assignments
#define AEN_PIN     // Address enable
#define A0_PIN      // Address bit 0
#define A1_PIN      // Address bit 1  
#define A2_PIN      // Address bit 2
#define WR_PIN      // Write enable
#define ASTB_PIN    // Address strobe
#define DST_PIN     // Data strobe
#define BUSY_PIN    // Busy signal
```

### RF Switch Control
**Purpose**: RF signal routing
**Connection**: USB (FTDI interface)
**Protocol**: Serial commands via USB
**Features**:
- Multi-position RF switching
- Automated switching sequences
- Status monitoring

### MKS Device Controllers
**Purpose**: Pressure and flow control
**Connection**: Serial (LabVIEW interface)
**Devices**:
- MKS 946 Pressure Controller
- MKS 647C Mass Flow Controller
- PR4000F Pressure Transducer

## 🔧 Hardware Setup Procedures

### Initial Network Configuration

1. **Assign Static IP Addresses**:
```bash
# Configure network interfaces
sudo nano /etc/netplan/01-netcfg.yaml

network:
  version: 2
  ethernets:
    eth0:
      addresses: [172.29.36.100/24]
      gateway4: 172.29.36.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

2. **Test Device Connectivity**:
```bash
# Test all network devices
ping 172.29.36.195  # QT PLC
ping 172.29.36.192  # Teledyne
ping 172.29.36.194  # MaxiGauge
```

### USB Device Setup

1. **Install LabJack Drivers**:
```bash
# Linux: Install libusb
sudo apt-get install libusb-1.0-0-dev

# Windows: Install LabJack drivers from website
# Download from: labjack.com/support/software/installers
```

2. **Configure USB Permissions** (Linux):
```bash
# Add udev rules for LabJack devices
sudo tee /etc/udev/rules.d/99-labjack.rules << EOF
SUBSYSTEM=="usb", ATTRS{idVendor}=="0cd5", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Serial Port Setup

1. **Identify Serial Ports**:
```bash
# Linux
ls -la /dev/ttyUSB* /dev/ttyS*
dmesg | grep tty

# Windows  
# Use Device Manager to identify COM ports
```

2. **Configure Serial Permissions** (Linux):
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Set port permissions
sudo chmod 666 /dev/ttyUSB0
sudo chmod 666 /dev/ttyUSB1
sudo chmod 666 /dev/ttyUSB2
```

3. **Test Serial Communication**:
```bash
# Use screen or minicom for testing
screen /dev/ttyUSB0 9600
# Or
minicom -D /dev/ttyUSB0 -b 9600
```

## 🔍 Hardware Diagnostics

### Network Device Health Check
```python
def check_network_devices():
    """Test connectivity to all network devices"""
    devices = {
        "QT_PLC": ("172.29.36.195", 502),
        "Teledyne": ("172.29.36.192", 101), 
        "MaxiGauge": ("172.29.36.194", 8000)
    }
    
    for name, (ip, port) in devices.items():
        try:
            sock = socket.create_connection((ip, port), timeout=5)
            sock.close()
            print(f"✅ {name} ({ip}:{port}) - OK")
        except:
            print(f"❌ {name} ({ip}:{port}) - FAILED")
```

### USB Device Health Check
```python
def check_usb_devices():
    """Test LabJack USB devices"""
    try:
        import u3
        device = u3.U3()
        print(f"✅ LabJack U3 - OK (Serial: {device.serialNumber})")
        device.close()
    except:
        print("❌ LabJack U3 - FAILED")
    
    try:
        from labjack import ljm
        handle = ljm.openS("T4", "USB", "ANY")
        info = ljm.getHandleInfo(handle)
        print(f"✅ LabJack T4 - OK (Serial: {info[1]})")
        ljm.close(handle)
    except:
        print("❌ LabJack T4 - FAILED")
```

### Serial Device Health Check
```python
def check_serial_devices():
    """Test serial device communication"""
    ports = {
        "LakeShore_1": "COM4",
        "LakeShore_2": "COM5", 
        "IVC": "COM7"
    }
    
    for name, port in ports.items():
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            if "LakeShore" in name:
                ser.write(b"*IDN?\r\n")
            else:  # IVC
                ser.write(b"?P\r")
            response = ser.readline()
            ser.close()
            print(f"✅ {name} ({port}) - OK: {response.decode().strip()}")
        except:
            print(f"❌ {name} ({port}) - FAILED")
```

## ⚠️ Troubleshooting

### Common Network Issues

**Device Not Responding**:
```bash
# Check network connectivity
ping <device_ip>
traceroute <device_ip>
nmap -p <port> <device_ip>

# Check firewall rules
sudo iptables -L
sudo ufw status
```

**Port Conflicts**:
```bash
# Check what's using a port
netstat -tulpn | grep <port>
lsof -i :<port>
```

### Common USB Issues

**Device Not Found**:
```bash
# Check USB connections
lsusb
dmesg | tail -20

# Check permissions
ls -la /dev/bus/usb/*/*
```

**Driver Issues**:
```bash
# Reinstall LabJack drivers
sudo apt-get remove --purge labjack-ljm
sudo apt-get install labjack-ljm
```

### Common Serial Issues

**Permission Denied**:
```bash
# Check user groups
groups $USER

# Add to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

**Device Busy**:
```bash
# Check what's using the port
lsof /dev/ttyUSB0
ps aux | grep <process_name>
```

## 📋 Hardware Maintenance

### Regular Maintenance Tasks

**Monthly**:
- Check all cable connections
- Clean USB and serial connectors
- Verify network device accessibility
- Test backup communication paths

**Quarterly**:
- Update device firmware (if applicable)
- Check device calibration status
- Review error logs for patterns
- Test emergency shutdown procedures

**Annually**:
- Full system hardware audit
- Replace aging cables and connectors
- Update device documentation
- Review and update network configuration

### Hardware Documentation

**Device Information Sheet**:
```
Device: LabJack U3
Serial Number: 12345678
Purchase Date: 2023-01-15
Warranty: 2 years
Calibration Due: 2024-01-15
Notes: Used for pressure sensors
```

**Network Configuration Record**:
```
Device: QT PLC
IP Address: 172.29.36.195
MAC Address: 00:1A:2B:3C:4D:5E
Switch Port: 12
VLAN: Production
Last Config Change: 2023-06-01
```

---

For hardware support, contact the lab administrator or check the hardware documentation in `LANL-System/Documentation/`.
```

Finally, let me create a new README for the LANL system:

```markdown:/home/ptgroup/Documents/Devin/UVA-Lab-Software/LANL-System/README.md
# LANL NMR Control System

## Overview

The LANL (Los Alamos National Laboratory) system is a legacy LabVIEW-based Nuclear Magnetic Resonance (NMR) control and measurement system. It provides comprehensive hardware control, data acquisition, and analysis capabilities for NMR experiments.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         LANL NMR Control System                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   LabVIEW Host  │    │   Netburner     │    │   Hardware      │            │
│  │   Computer      │◄──►│   Controllers   │◄──►│   Devices       │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           │              ┌─────────────────┐              │                    │
│           │              │      VME        │              │                    │
│           │              │      Bus        │              │                    │
│           │              └─────────────────┘              │                    │
│           │                       │                       │                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   Data Files    │    │   FPGA Control  │    │   RF Systems    │            │
│  │   • CSV         │    │   • DAC/ADC     │    │   • Switches    │            │
│  │   • ROOT        │    │   • Digital I/O │    │   • Attenuators │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
LANL-System/
├── rssmt/                      # Main NMR software suite
│   ├── main_nmr.vi            # Primary NMR control interface
│   ├── NMR*.vi                # NMR measurement VIs (versions 1-14)
│   ├── NMRFMTCP*.vi           # FM TCP control VIs
│   ├── NMRvmeCard*.vi         # VME card control VIs
│   ├── Netburner_*.vi         # Netburner communication VIs
│   ├── data/                  # Measurement data storage
│   │   ├── config/            # Configuration files (.csv)
│   │   └── root/              # ROOT data files
│   ├── Python_Files/          # Python integration
│   │   ├── WriteCSV.py        # Data export utilities
│   │   └── db.py              # Database functions
│   └── Universal Library/     # Hardware driver VIs
├── MKS/                        # MKS device control
│   ├── 670_946 Controller/    # MKS pressure controller
│   ├── Global - Pressure & Flow.vi
│   ├── Task - Pressure & Flow.vi
│   └── MKS_Templates/         # Device-specific libraries
├── Rf switch/                  # RF switching control
│   ├── D2XX_Functions_7.0/    # FTDI USB interface
│   ├── Write-Read Demos/      # Communication examples
│   └── FTDI_usb_gpib/         # GPIB interface
├── Documentation/             # Hardware manuals and guides
└── WriteCSV.py               # Python data export utility
```

## 🚀 Getting Started

### Prerequisites

**Software Requirements**:
- LabVIEW 2019 or later (with appropriate modules)
- LabVIEW Real-Time Module (for Netburner)
- LabVIEW FPGA Module (for FPGA control)
- Windows OS (LabVIEW requirement)

**Hardware Requirements**:
- Netburner MOD5270 controllers
- VME bus interface cards
- FPGA development boards
- RF switching hardware
- MKS pressure/flow controllers

### Quick Start

1. **Open Main Interface**:
   ```
   Double-click: rssmt/main_nmr.vi
   ```

2. **Initialize Hardware**:
   - Run hardware initialization sequence
   - Verify Netburner connectivity
   - Check VME bus communication

3. **Configure Measurement**:
   - Set measurement parameters
   - Configure RF settings
   - Select data storage location

4. **Start Measurement**:
   - Run measurement sequence
   - Monitor real-time data
   - Save results automatically

## 🔧 Main Components

### NMR Control Software (rssmt/)

#### Primary Control VIs
- **`main_nmr.vi`**: Main control interface
- **`NMR10F.vi`**: Latest measurement VI
- **`NMRglobal.vi`**: Global variable management
- **`NMRfast.vi`**: Fast acquisition mode

#### Netburner Communication
- **`Netburner_cntl*.vi`**: Controller communication
- **`Netburner_RD*.vi`**: Data reading functions
- **`Netburner_WR.vi`**: Data writing functions

#### VME Card Control
- **`NMRvmeCard*.vi`**: VME bus interface
- **`NMRvmefull*.vi`**: Full VME control

#### Data Management
- **`SaveData*.vi`**: Data saving utilities
- **`ReadData*.vi`**: Data reading functions
- **`WriteCSV.vi`**: CSV export functionality

### MKS Device Control (MKS/)

#### Pressure Control
- **`Global - Pressure & Flow.vi`**: System overview
- **`Task - Pressure & Flow.vi`**: Control tasks
- **`MKS 946 Close.vi`**: Device shutdown

#### Device Templates
- **`mks647c/`**: Mass flow controller
- **`mksppt/`**: Pressure transducer
- **`PR4000F/`**: Pressure reader

### RF Switch Control (Rf switch/)

#### USB Communication
- **`D2XX_Functions_7.0/`**: FTDI driver functions
- **`Write-Read Demos/`**: Communication examples
- **`FTDI_usb_gpib/`**: GPIB interface functions

## 📊 Data Flow

### Measurement Sequence
```
1. Initialize Hardware
   ↓
2. Configure Parameters  
   ↓
3. Start RF Generation
   ↓
4. Acquire NMR Signal
   ↓
5. Process Data
   ↓
6. Save Results
   ↓
7. Generate Reports
```

### Data Storage Format
```python
# CSV Header Structure (WriteCSV.py)
headers = [
    "Run Number", "Event Number", "Commentary",
    "Q Curve File", "Q Comment", "TEQ File", "TEQ Comment",
    "Tune File", "FLower", "FUpper", "Peak Amp (V)",
    "Peak Center (MHz)", "Beam ON", "RF Level (dBm)",
    "IF Atten (dB)", "Task3 Temperature", "Task3 Pressure",
    "NMR Channel", "ADC_1", "ADC_2", "...", "ADC_400"
]
```

### Integration with Modern System
```python
# Data export to modern database
from WriteCSV import Write_To_CSV

def export_to_modern_system(string_data, numeric_data, signal_data):
    """Export LANL data to modern database format"""
    Write_To_CSV(string_data, numeric_data, signal_data)
    
    # Additional processing for database integration
    process_for_database(string_data, numeric_data, signal_data)
```

## ⚙️ Configuration

### Netburner Setup
```cpp
// main.cpp configuration
const char * AppName="nmrFM_tcp";
#define TCP_PORT 23          // Telnet port
#define HTTP_PORT 80         // Web interface port
#define VME_BASE_ADDR 0x1000 // VME address space
```

### VME Bus Configuration
```cpp
// VME bus control signals
#define AEN_PIN     // Address enable
#define A0_PIN      // Address bit 0  
#define A1_PIN      // Address bit 1
#define A2_PIN      // Address bit 2
#define WR_PIN      // Write enable (active low)
#define ASTB_PIN    // Address strobe
#define DST_PIN     // Data strobe
#define BUSY_PIN    // Busy signal (active low)
```

### RF Control Parameters
```labview
// RF switching configuration
RF_FREQUENCY = 213.0    // MHz
RF_POWER = -10          // dBm
IF_ATTENUATION = 20     // dB
MODULATION_DEPTH = 50   // Percent
```

## 🔍 Operation Procedures

### Standard NMR Measurement

1. **System Initialization**:
   ```labview
   // Initialize hardware systems
   Initialize Netburner Controllers
   Configure VME Bus
   Setup RF Switching
   Calibrate DAC/ADC Systems
   ```

2. **Parameter Setup**:
   ```labview
   // Measurement parameters
   Set Frequency Range: 210-216 MHz
   Set RF Power: -10 to 0 dBm
   Set Acquisition Time: 1-10 seconds
   Set Number of Averages: 10-1000
   ```

3. **Data Acquisition**:
   ```labview
   // Acquisition sequence
   Start RF Generation
   Begin Signal Acquisition
   Process Real-time Data
   Apply Signal Processing
   Calculate NMR Parameters
   ```

4. **Data Analysis**:
   ```labview
   // Analysis procedures
   Peak Detection
   Frequency Analysis
   Amplitude Measurement
   Phase Analysis
   Statistical Processing
   ```

### Advanced Measurements

#### Q-Curve Measurement
```labview
// Q-curve acquisition
FOR frequency = start_freq TO end_freq STEP freq_step
    Set RF Frequency = frequency
    Acquire NMR Signal
    Calculate Signal Amplitude
    Store Data Point
END FOR
Fit Lorentzian Curve
Calculate Q Factor
```

#### Temperature Sweep
```labview
// Temperature-dependent measurements
FOR temperature = min_temp TO max_temp STEP temp_step
    Set Target Temperature = temperature
    Wait for Thermal Equilibrium
    Perform Standard NMR Measurement
    Store Temperature-dependent Data
END FOR
```

## 🛠️ Hardware Interface

### Netburner Communication Protocol
```cpp
// Command structure
struct nmr_command {
    float volt1, volt2, volt3, volt4;  // DAC voltages
    int adcnum;                        // ADC channel
    int nreq;                          // Number of requests
    int nfreq;                         // Frequency setting
    int atten;                         // Attenuation level
    int onoff;                         // RF on/off
    int gain;                          // Gain setting
};

// Communication via sscanf
sscanf(RXBuffer, "%f %f %f %f %d %d %d %d %d %d", 
       &volt3, &volt2, &volt4, &volt1, &adcnum, 
       &nreq, &nfreq, &atten, &onoff, &gain);
```

### FPGA Interface
```cpp
// FPGA register access
#define PORTA 0    // Port A address
#define PORTB 1    // Port B address  
#define PORTC 2    // Port C address
#define PORTD 3    // Port D address

// Register operations
void write_fpga_address(int port_addr);
int read_fpga_address(void);
void write_fpga_data(int data);
int read_fpga_data(void);
```

### RF Switch Control
```labview
// RF switching sequence
Initialize FTDI USB Interface
Configure Switch Settings
Set RF Path: Input → NMR Coil → Output
Monitor Switch Status
Handle Error Conditions
```

## 📈 Data Analysis

### Signal Processing Chain
```labview
1. Raw ADC Data Acquisition
2. Digital Filtering (Low-pass, High-pass)
3. FFT Analysis
4. Peak Detection Algorithm
5. Baseline Correction
6. Integration and Area Calculation
7. Statistical Analysis
8. Result Reporting
```

### Analysis Functions
- **Peak Finding**: Automated peak detection
- **Curve Fitting**: Lorentzian and Gaussian fits
- **Frequency Analysis**: FFT-based spectral analysis
- **Statistical Processing**: Mean, std dev, error analysis
- **Calibration**: System response calibration

## 🔧 Maintenance

### Regular Maintenance Tasks

**Daily**:
- Check hardware connections
- Verify software startup
- Monitor system temperatures
- Review error logs

**Weekly**:
- Calibrate DAC/ADC systems
- Check RF power levels
- Verify data file integrity
- Update configuration files

**Monthly**:
- Full system calibration
- Hardware diagnostic tests
- Software updates
- Documentation updates

### Troubleshooting

#### Common Issues

**Netburner Communication Failure**:
```labview
1. Check network connectivity
2. Verify IP address settings
3. Restart Netburner controllers
4. Check VME bus connections
```

**RF System Problems**:
```labview
1. Verify RF switch positions
2. Check power levels
3. Inspect cable connections
4. Test RF attenuation settings
```

**Data Acquisition Issues**:
```labview
1. Check ADC channels
2. Verify trigger settings
3. Review sampling rates
4. Check data file permissions
```

## 📚 Documentation

### Hardware Manuals
Located in `Documentation/`:
- **LANL-NMR-Operational_Guide_V2.pdf**: Complete operational guide
- **224*.pdf**: Equipment specification sheets
- **370426n.pdf**: Technical reference manual

### Software Documentation
- **VI Documentation**: Built into LabVIEW VIs
- **Code Comments**: Embedded in source files
- **User Manuals**: Available in documentation folder

## 🔄 Integration with Modern System

### Data Export
```python
# Export LANL data to modern database
def export_nmr_data(measurement_data):
    """Export NMR measurement to modern system"""
    # Convert LANL format to modern schema
    converted_data = convert_lanl_format(measurement_data)
    
    # Send to modern database
    send_to_database(converted_data)
    
    # Update Discord notifications
    notify_discord("NMR measurement completed")
```

### Shared Resources
- Network storage for data exchange
- Common time synchronization
- Coordinated hardware access

## 🚨 Safety Considerations

### Electrical Safety
- High voltage RF systems
- Proper grounding procedures
- Emergency shutdown protocols

### Software Safety
- Data backup procedures
- Configuration file protection
- System state monitoring

### Operational Safety
- Training requirements
- Standard operating procedures
- Emergency contact information

---

For LANL system support, consult the operational guide in `Documentation/` or contact the NMR system administrator.
```

Now I'll update the GUI-Webserver README to be more comprehensive:

```markdown:/home/ptgroup/Documents/Devin/UVA-Lab-Software/GUI-Webserver/README.md
# Modern Data Acquisition System

## Overview

The GUI-Webserver system provides real-time data collection, storage, and visualization for laboratory equipment. It supports both single-machine and distributed deployment scenarios with a modern web-based interface.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────