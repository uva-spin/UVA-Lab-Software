# LakeShore Reader Testing

This directory contains several test scripts for the LakeShore temperature controller reader.

## Test Scripts

### 1. `TestLakeshore.py` - Main Test Script
The primary test script that provides comprehensive testing of the LakeShore reader.

**Features:**
- Connection testing
- Data streaming verification
- Real-time data collection (10 seconds)
- Data parsing tests with various formats
- Proper error handling and cleanup

**Usage:**
```bash
python TestLakeshore.py
```

**Output:**
- Connection status
- Real-time data collection with timestamps
- Both raw and formatted data display
- Data parsing test results
- Performance metrics

### 2. `test_lakeshore_quick.py` - Quick Test
A simple script for basic connectivity and data reading verification.

**Features:**
- Basic connection test
- Quick data collection (5 readings)
- Minimal output for fast verification

**Usage:**
```bash
python test_lakeshore_quick.py
```

**Output:**
- Connection status
- 5 data readings with formatted output
- Simple pass/fail indication

### 3. `test_lakeshore_simple.py` - Simple Test
Demonstrates the difference between raw and formatted data.

**Features:**
- Raw vs formatted data comparison
- 10-second data collection
- Data processing tests with sample data

**Usage:**
```bash
python test_lakeshore_simple.py
```

**Output:**
- Raw data display with type and length information
- Formatted data with channel labels
- Data processing test results

### 4. `test_lakeshore_comprehensive.py` - Comprehensive Test
The most detailed test script with extensive functionality.

**Features:**
- Command-line argument support for port and duration
- Detailed logging to file
- Comprehensive error handling
- Performance metrics
- Raw data processing tests

**Usage:**
```bash
# Default: COM4 port, 10 seconds
python test_lakeshore_comprehensive.py

# Custom port and duration
python test_lakeshore_comprehensive.py COM3 30
python test_lakeshore_comprehensive.py /dev/ttyUSB0 60
```

**Output:**
- Detailed connection and streaming status
- Real-time data with timestamps
- Performance statistics
- Log file creation (`lakeshore_test.log`)

## Configuration

### Port Configuration
All test scripts use `COM4` as the default port. To change this:

1. **Windows:** Use `COM1`, `COM2`, `COM3`, etc.
2. **Linux/Mac:** Use `/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.

### Serial Parameters
The LakeShore reader uses these default serial parameters:
- **Baudrate:** 9600
- **Data bits:** 7
- **Parity:** Odd
- **Stop bits:** 1
- **Timeout:** 2 seconds

## Troubleshooting

### Common Issues

1. **Port Not Found**
   - Verify the correct port name for your system
   - Check if the device is connected
   - Ensure no other application is using the port

2. **Connection Failed**
   - Check serial cable connections
   - Verify device power
   - Confirm serial parameters match device settings

3. **No Data Received**
   - Check device communication protocol
   - Verify the `SRDG?` command is supported
   - Check device manual for correct commands

4. **Permission Errors (Linux/Mac)**
   - Add user to dialout group: `sudo usermod -a -G dialout $USER`
   - Set proper permissions: `sudo chmod 666 /dev/ttyUSB0`

### Debug Information
All test scripts include logging that can help diagnose issues:
- Connection attempts and failures
- Data parsing errors
- Thread status information

## Data Format

The LakeShore reader expects data in CSV format:
```
123.456,234.567,345.678,456.789,567.890,678.901,789.012,890.123\r\n
```

The reader returns 8 temperature values (one for each channel) and handles:
- Incomplete data (fills with zeros)
- Invalid data (converts to 0.0)
- Empty responses (returns all zeros)

## Integration

These test scripts can be used to:
- Verify hardware connectivity
- Test data acquisition before integration
- Debug communication issues
- Validate data parsing logic
- Performance testing

## Dependencies

Required Python packages:
- `pyserial` - Serial communication
- `threading` - Multi-threading (built-in)
- `logging` - Logging (built-in)
- `time` - Time functions (built-in)
- `datetime` - Date/time handling (built-in) 