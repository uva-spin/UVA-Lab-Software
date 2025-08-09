# Comprehensive DAQ Test Suite

This directory contains comprehensive test scripts for all data acquisition devices in the UVA Lab Software system. Each test script validates connection, data reading, error handling, and proper cleanup for its respective device.

## Test Scripts Overview

### LabJack Devices
- **`test_labjack1.py`** - Tests LabJack U3 for pressure and temperature sensors (6 channels)
- **`test_labjack_t4.py`** - Tests LabJack T4 for flow meters (2 channels)

### Network-Based Devices
- **`test_teledyne.py`** - Tests Teledyne THCD-401 flow meter via TCP
- **`test_maxigauge.py`** - Tests Pfeiffer MaxiGauge pressure controller via TCP
- **`test_qt_comprehensive.py`** - Tests Modbus TCP PLC for QT data (18 values)

### Serial-Based Devices
- **`test_lakeshore_comprehensive.py`** - Tests LakeShore temperature controller via serial
- **`test_ivc_comprehensive.py`** - Tests IVC pressure controller via serial

### Master Test Runner
- **`run_all_daq_tests.py`** - Runs all tests sequentially and provides comprehensive summary

## Device Details

### LabJack1 (U3) - Pressure & Temperature
- **Channels**: 6 analog inputs
- **Data**: Root exhaust pressure, buffer pressure, magnet pressure, purifier inlet pressure, fridge vapor pressure, thermocouple
- **Units**: Torr, PSI, Celsius
- **Connection**: USB

### LabJack2 (T4) - Flow Meters
- **Channels**: 2 analog inputs  
- **Data**: Microwave flow meter, heat exchanger flow meter
- **Units**: SLM (Standard Liters per Minute)
- **Connection**: USB

### Teledyne THCD-401 - Flow Meter
- **Channels**: 3 flow rates
- **Data**: Flow rate measurements
- **Connection**: TCP/IP (172.29.36.192:101)

### MaxiGauge - Pressure Controller
- **Channels**: 6 pressure sensors
- **Data**: Pressure readings in scientific notation
- **Connection**: TCP/IP (172.29.36.194:8000)

### LakeShore - Temperature Controller
- **Data**: Temperature readings from sensors
- **Connection**: Serial (COM4 by default)
- **Protocol**: LakeShore serial protocol

### IVC - Pressure Controller
- **Data**: Pressure readings with status codes
- **Connection**: Serial (COM7 by default)
- **Protocol**: IVC serial protocol

### QT - Modbus TCP PLC
- **Data**: 18 QT data values (flow rates, pressures, temperatures)
- **Connection**: Modbus TCP (172.29.36.195)
- **Ports**: 502 (float), 503 (integer)

## Usage

### Running Individual Tests

```bash
# Navigate to the data_acquisition directory
cd GUI-Webserver/data_acquisition

# Run individual tests
python test_labjack1.py
python test_teledyne.py
python test_maxigauge.py
python test_lakeshore_comprehensive.py
python test_ivc_comprehensive.py
python test_qt_comprehensive.py
```

### Running All Tests

```bash
# Run the master test suite
python run_all_daq_tests.py
```

### Test Output

Each test produces:
- **Console output**: Real-time test progress and results
- **Log file**: Detailed logging (e.g., `labjack1_test.log`, `teledyne_test.log`)
- **Exit code**: 0 for success, 1 for failure

## Test Components

Each comprehensive test includes:

### 1. Configuration Test
- Validates device settings and parameters
- Displays network/serial configuration
- Tests scale factors and calibration values

### 2. Connection Test
- Tests basic device initialization
- Validates communication protocols
- Ensures proper resource cleanup

### 3. Data Reading Test
- Runs for 10-15 seconds collecting samples
- Calculates success rate (must be ≥80% to pass)
- Displays formatted readings with units

### 4. Error Handling Test
- Tests with invalid configurations
- Validates graceful failure handling
- Ensures proper exception management

### 5. Stress Test
- Performs rapid start/stop cycles
- Tests device stability under repeated initialization
- Validates resource management

### 6. Data Processing Test (where applicable)
- Tests data parsing and conversion
- Validates scale factor calculations
- Tests protocol-specific functionality

## Prerequisites

### Hardware Requirements
- LabJack U3 and T4 devices connected via USB
- Network connectivity to TCP-based devices
- Serial ports available for serial-based devices

### Software Requirements
```bash
pip install u3 numpy pyModbusTCP pyserial
```

### Network Configuration
Ensure devices are accessible at their configured IP addresses:
- Teledyne: 172.29.36.192:101
- MaxiGauge: 172.29.36.194:8000
- QT PLC: 172.29.36.195:502/503

### Serial Port Configuration
Adjust serial ports in test scripts as needed:
- LakeShore: COM4 (default)
- IVC: COM7 (default)

## Troubleshooting

### Common Issues

1. **Device Not Found**
   - Check USB connections for LabJack devices
   - Verify network connectivity for TCP devices
   - Ensure serial ports are available and correct

2. **Permission Errors**
   - On Linux, ensure user has access to USB devices
   - May need to add user to `dialout` group
   - Configure udev rules for persistent device access

3. **Import Errors**
   - Install required packages: `pip install u3 numpy pyModbusTCP pyserial`
   - Ensure LabJack Python library is properly installed

4. **Network Timeouts**
   - Check firewall settings
   - Verify device IP addresses and ports
   - Test network connectivity with ping/telnet

5. **Serial Communication Issues**
   - Verify correct COM port assignments
   - Check baud rate and serial settings
   - Ensure no other applications are using the port

### Success Criteria

A test is considered successful if:
- All test components pass
- Data reading success rate ≥80%
- No critical errors in log files
- Proper cleanup and resource management
- Exit code = 0

## Log Files

Each test creates detailed log files:
- `labjack1_test.log`
- `teledyne_test.log`
- `maxigauge_test.log`
- `lakeshore_comprehensive_test.log`
- `ivc_comprehensive_test.log`
- `qt_comprehensive_test.log`
- `all_daq_tests.log` (master test suite)

## Integration

These test scripts integrate with the existing data acquisition system:
- Follow the same patterns as existing test files
- Use consistent logging and error handling
- Maintain compatibility with the main data collection system
- Support the same configuration parameters

## Maintenance

### Regular Testing
- Run individual tests during device setup
- Use master test suite for system validation
- Monitor log files for performance trends

### Updates
- Update device IP addresses if network changes
- Modify serial ports if hardware changes
- Adjust scale factors if sensor calibration changes
- Add new test components as devices evolve

### Performance Monitoring
- Track success rates over time
- Monitor test execution times
- Review error patterns in logs
- Update test criteria as needed 