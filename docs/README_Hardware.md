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
