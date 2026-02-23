# LabJack1 Test Documentation

## Overview

The `test_labjack1.py` script provides comprehensive testing for the `LabJackReader_1` class, which interfaces with a LabJack U3 device to read pressure and temperature data from 6 analog channels.

## Channel Mapping

The LabJack1 reads data from the following channels:

| Channel | Signal | Units | Scale Factor |
|---------|--------|-------|--------------|
| AIN0 | Root Exhaust Pressure | Torr | 0.7928388747 |
| AIN1 | Buffer Pressure | PSI | 17.46031746 |
| AIN2 | Magnet Pressure | PSI | 1.0 |
| AIN3 | Purifier Inlet Pressure | PSI | 1.0 |
| AIN4 | Fridge Vapor Pressure | Torr | 52.55102041 |
| AIN6 | Thermocouple | Celsius | 1.0 |

## Test Components

### 1. Connection Test
- Tests basic device initialization and connection
- Verifies the LabJack U3 can be opened and configured
- Ensures proper cleanup after connection

### 2. Scale Factors Test
- Validates PSI to Torr conversion function
- Displays all configured scale factors
- Ensures calibration values are accessible

### 3. Data Reading Test
- Runs for 15 seconds collecting data samples
- Tests all 6 analog channels
- Calculates success rate (must be ≥80% to pass)
- Displays formatted readings with units

### 4. Stress Test
- Performs 3 rapid start/stop cycles
- Tests device stability under repeated initialization
- Validates proper resource cleanup

## Usage

### Prerequisites
- LabJack U3 device connected via USB
- Required Python packages installed:
  - `u3` (LabJack Python library)
  - `numpy`
  - `threading`
  - `logging`

### Running the Test

```bash
# Navigate to the data_acquisition directory
cd GUI-Webserver/data_acquisition

# Run the test script
python test_labjack1.py

# Or run directly (if executable)
./test_labjack1.py
```

### Expected Output

The test will produce detailed logging output including:

```
2024-01-XX XX:XX:XX - __main__ - INFO - Starting LabJack1 Comprehensive Test Suite
2024-01-XX XX:XX:XX - __main__ - INFO - ==================== Connection Test ====================
2024-01-XX XX:XX:XX - __main__ - INFO - Initializing LabJackReader_1 for U3 model
2024-01-XX XX:XX:XX - __main__ - INFO - Starting LabJackReader_1
2024-01-XX XX:XX:XX - __main__ - INFO - Connection test successful!
...
```

### Log Files

The test creates a log file `labjack1_test.log` in the same directory with detailed test results and any error messages.

## Troubleshooting

### Common Issues

1. **Device Not Found**
   - Ensure LabJack U3 is properly connected via USB
   - Check device drivers are installed
   - Verify device appears in Device Manager (Windows) or `lsusb` (Linux)

2. **Permission Errors**
   - On Linux, ensure user has access to USB devices
   - May need to add user to `dialout` group or configure udev rules

3. **Import Errors**
   - Install required packages: `pip install u3 numpy`
   - Ensure LabJack Python library is properly installed

4. **Data Quality Issues**
   - Check sensor connections and wiring
   - Verify scale factors are correct for your sensors
   - Ensure proper grounding and shielding

### Success Criteria

The test is considered successful if:
- All 4 test components pass
- Data reading success rate ≥80%
- No critical errors in log files
- Proper cleanup and resource management

## Integration

This test script follows the same patterns as other test files in the data acquisition system:
- `test_labjack_t4.py` - Tests LabJack T4 model
- `testLakeshore.py` - Tests LakeShore temperature controller
- `testIVC.py` - Tests IVC pressure controller

## Maintenance

- Update scale factors if sensor calibration changes
- Modify test duration or success criteria as needed
- Add additional channel tests if new sensors are added
- Review log files regularly for performance trends 