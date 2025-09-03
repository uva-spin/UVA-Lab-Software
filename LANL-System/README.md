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
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Modern Data Acquisition System                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Data Acquisition Layer                               │ │
│  │                                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │   LabJack   │ │  Teledyne   │ │ MaxiGauge   │ │ LakeShore   │          │ │
│  │  │   (USB)     │ │   (TCP)     │ │   (TCP)     │ │ (Serial)    │    ...   │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  │         │               │               │               │                  │ │
│  │         ▼               ▼               ▼               ▼                  │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │ LabJack     │ │ Teledyne    │ │ MaxiGauge   │ │ LakeShore   │          │ │
│  │  │ Reader      │ │ Reader      │ │ Reader      │ │ Reader      │    ...   │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  │                                       │                                    │ │
│  └───────────────────────────────────────┼────────────────────────────────────┘ │
│                                          │                                      │
│  ┌───────────────────────────────────────┼────────────────────────────────────┐ │
│  │                   Integration Layer   │                                    │ │
│  │                                       ▼                                    │ │
│  │                        ┌─────────────────────────────┐                    │ │
│  │                        │   Async Data Coordinator   │                    │ │
│  │                        │  (standalone_data_acq.py)  │                    │ │
│  │                        └─────────────────────────────┘                    │ │
│  │                                       │                                    │ │
│  └───────────────────────────────────────┼────────────────────────────────────┘ │
│                                          │                                      │
│  ┌───────────────────────────────────────┼────────────────────────────────────┐ │
│  │                    Web Server Layer   │                                    │ │
│  │                                       ▼                                    │ │
│  │                        ┌─────────────────────────────┐                    │ │
│  │                        │     Flask Web Server       │                    │ │
│  │                        │   (data_collector.py)      │                    │ │
│  │                        └─────────────────────────────┘                    │ │
│  │                                       │                                    │ │
│  │                                       ▼                                    │ │
│  │                        ┌─────────────────────────────┐                    │ │
│  │                        │      SQLite Database       │                    │ │
│  │                        │     (flaskr.sqlite)        │                    │ │
│  │                        └─────────────────────────────┘                    │ │
│  │                                       │                                    │ │
│  └───────────────────────────────────────┼────────────────────────────────────┘ │
│                                          │                                      │
│  ┌───────────────────────────────────────┼────────────────────────────────────┐ │
│  │                 Presentation Layer    │                                    │ │
│  │                                       ▼                                    │ │
│  │  ┌─────────────────┐                ┌─────────────────┐                   │ │
│  │  │  Web Dashboard  │                │  Discord Bot    │                   │ │
│  │  │  (index.html)   │                │  Monitoring     │                   │ │
│  │  └─────────────────┘                └─────────────────┘                   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
GUI-Webserver/
├── data_acquisition/           # Data acquisition components
│   ├── daq/                   # Device abstraction layer  
│   │   ├── _LabJackReader.py  # LabJack device interface
│   │   ├── _TeledyneReader.py # Teledyne flow meter interface
│   │   ├── _MaxiGaugeReader.py# MaxiGauge pressure interface
│   │   ├── _LakeShoreReader.py# LakeShore temperature interface
│   │   ├── _IVCReader.py      # IVC pressure interface
│   │   ├── _QTReader.py       # QT PLC interface
│   │   ├── config.py          # System configuration
│   │   ├── standalone_data_acquisition.py # Main acquisition script
│   │   └── setup_data_acquisition.py     # Setup utility
│   ├── device_testing/        # Device testing suite
│   │   ├── test_*.py          # Individual device tests
│   │   ├── run_all_daq_tests.py # Master test runner
│   │   └── docs/              # Testing documentation
│   └── data_logs/             # Local data backup
├── web_server/                # Web server components
│   ├── data_collector.py      # Flask application
│   ├── start_data_collector.py# Server startup script
│   ├── schema.sql             # Database schema
│   └── requirements.txt       # Python dependencies
├── static/                    # Web assets
│   ├── css/style.css          # Styling
│   ├── js/script.js           # JavaScript functionality
│   └── images/                # Static images
├── templates/                 # HTML templates
│   └── index.html             # Main dashboard
└── docs/                      # Documentation
    ├── README_Data_Acquisition.md
    ├── README_Data_Collector.md
    └── README_Testing.md
```

## 🚀 Quick Start Guide

### Option 1: Single Machine Setup (Recommended for Testing)

**Step 1: Install Dependencies**
```bash
# Install Python packages
pip install -r web_server/requirements.txt
pip install -r data_acquisition/daq/requirements.txt

# Required packages:
# - flask, sqlite3 (web server)
# - u3, numpy (LabJack)
# - pyModbusTCP (Modbus devices)
# - pyserial (serial devices)
```

**Step 2: Start Web Server**
```bash
cd web_server
python start_data_collector.py

# Expected output:
# ✅ Database initialized successfully
# 🌐 Data collector started on http://0.0.0.0:5000
# 📊 Web dashboard available at: http://localhost:5000
```

**Step 3: Start Data Acquisition**
```bash
# In a new terminal
cd data_acquisition/daq
python standalone_data_acquisition.py

# Expected output:
# 🚀 Starting UVA Lab Data Acquisition System
# ✅ QT reader initialized
# ✅ Teledyne data reader started
# ✅ LabJack data reader started
# 📊 Data collection active - sending to http://localhost:5000/data
```

**Step 4: Access Dashboard**
```
Open browser: http://localhost:5000
```

### Option 2: Distributed Setup (Production)

**Machine A (Data Acquisition)**:
```bash
# Copy data acquisition files to machine with device connections
cd data_acquisition/daq
python setup_data_acquisition.py

# Follow prompts to configure remote server URL
# Example: http://192.168.1.100:5000

python standalone_data_acquisition.py
```

**Machine B (Web Server)**:
```bash
cd web_server  
python start_data_collector.py
```

## 🔧 Device Configuration

### Supported Devices

#### Network Devices (TCP/IP)
| Device | IP Address | Port | Protocol | Data |
|--------|------------|------|----------|------|
| QT PLC | 172.29.36.195 | 502/503 | Modbus TCP | 18 process values |
| Teledyne | 172.29.36.192 | 101 | TCP | 3 flow rates |
| MaxiGauge | 172.29.36.194 | 8000 | TCP | 6 pressure readings |

#### USB Devices
| Device | Connection | Channels | Data |
|--------|------------|----------|------|
| LabJack U3 | USB | 6 analog | Pressure, temperature |
| LabJack T4 | USB | 2 analog | Flow rates |

#### Serial Devices  
| Device | Port | Protocol | Data |
|--------|------|----------|------|
| LakeShore | COM4/COM5 | LakeShore | Temperature |
| IVC | COM7 | Custom | Pressure |

### Configuration Files

**Main Configuration** (`data_acquisition/daq/config.py`):
```python
# Remote server configuration
REMOTE_SERVER_URL = "http://128.143.231.224:5000"
DATA_PATH = f"{REMOTE_SERVER_URL}/data"

# Device settings
PLC_IP = "172.29.36.195"
TELEDYNE_IP = "172.29.36.192"
MAXIGAUGE_IP = "172.29.36.194"

# Timing settings
SLEEP_INTERVAL = 5                    # Main loop interval
ASYNC_READ_INTERVAL = 1               # Device read interval
MAX_CONSECUTIVE_FAILURES = 10         # Error threshold
```

## 📊 Data Flow

### Real-time Data Collection
```
Hardware Devices → Device Readers → Async Coordinator → HTTP POST → Flask Server → SQLite Database
                                                                                         ↓
                                                                              Web Dashboard ← JavaScript
```

### Data Processing Pipeline
```python
# Simplified data flow
async def main_data_loop():
    while not shutdown_event.is_set():
        # 1. Collect data from all devices
        qt_data = await qt_reader.read_data()
        teledyne_data = await teledyne_reader.get_latest_data()
        labjack_data = await labjack_reader.get_latest_data()
        
        # 2. Merge data into unified format
        merged_data = merge_all_data(qt_data, teledyne_data, labjack_data)
        
        # 3. Send to web server
        await send_data_to_server(merged_data)
        
        # 4. Local backup
        save_local_backup(merged_data)
        
        await asyncio.sleep(SLEEP_INTERVAL)
```

## 🌐 Web Interface

### Dashboard Features
- **Real-time Graphs**: Live plotting of sensor data
- **Status Indicators**: Device connection status
- **Data Tables**: Recent measurements with timestamps  
- **Export Functions**: CSV download capabilities
- **System Health**: Database and network status

### API Endpoints

#### Data Submission
```http
POST /data
Content-Type: application/json

{
    "timestamp": "2024-01-15T14:30:00",
    "qt_data": {...},
    "teledyne_data": {...},
    "labjack_data": {...}
}
```

#### Data Retrieval
```http
GET /query_db?limit=100&table=HMI
```

#### System Status
```http
GET /status
```

### JavaScript Integration
```javascript
// Real-time data updates
function updateDashboard() {
    fetch('/query_db?limit=1')
        .then(response => response.json())
        .then(data => {
            updateGraphs(data);
            updateStatusIndicators(data);
        });
}

// Auto-refresh every 5 seconds
setInterval(updateDashboard, 5000);
```

## 🧪 Testing Framework

### Device Testing Suite

**Run All Tests**:
```bash
cd data_acquisition/device_testing
python run_all_daq_tests.py

# Output:
# 🧪 Starting comprehensive DAQ test suite...
# ✅ LabJack1 Test: PASSED (95% success rate)
# ✅ Teledyne Test: PASSED (100% success rate)  
# ✅ MaxiGauge Test: PASSED (90% success rate)
# ❌ LakeShore Test: FAILED (Device not found)
# 📊 Overall Result: 3/4 tests passed
```

**Individual Device Tests**:
```bash
# Test specific devices
python test_labjack1.py
python test_teledyne.py
python test_maxigauge.py
python test_lakeshore_comprehensive.py
python test_ivc_comprehensive.py
python test_qt_comprehensive.py
```

### Test Results Interpretation
- **✅ PASSED**: Device operational, >80% success rate
- **⚠️ WARNING**: Device operational, 60-80% success rate  
- **❌ FAILED**: Device not responding or <60% success rate

## 🔍 Monitoring & Maintenance

### Health Checks

**System Status Check**:
```python
from DatabaseReader import DatabaseReader

def check_system_health():
    db = DatabaseReader("flaskr.sqlite")
    
    # Check data freshness
    last_timestamp = db.get_last_timestamp("HMI")
    if last_timestamp:
        age = datetime.now() - last_timestamp
        print(f"Data age: {age}")
    
    # Check device status
    tables = db.list_tables()
    print(f"Active tables: {tables}")
    
    db.close()
```

**Log Monitoring**:
```bash
# Monitor data acquisition logs
tail -f data_acquisition/daq/logs/data_acquisition.log

# Monitor web server logs  
tail -f web_server/logs/data_collector.log
```

### Performance Metrics
- **
