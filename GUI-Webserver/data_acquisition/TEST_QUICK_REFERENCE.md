# DAQ Test Quick Reference

## Test Files Summary

| Device | Test Script | Connection | Channels | Key Data |
|--------|-------------|------------|----------|----------|
| LabJack U3 | `test_labjack1.py` | USB | 6 | Pressure, Temperature |
| LabJack T4 | `test_labjack_t4.py` | USB | 2 | Flow Rates |
| Teledyne | `test_teledyne.py` | TCP | 3 | Flow Rates |
| MaxiGauge | `test_maxigauge.py` | TCP | 6 | Pressure |
| LakeShore | `test_lakeshore_comprehensive.py` | Serial | 1+ | Temperature |
| IVC | `test_ivc_comprehensive.py` | Serial | 1 | Pressure |
| QT | `test_qt_comprehensive.py` | Modbus TCP | 18 | Process Data |

## Quick Commands

### Run All Tests
```bash
python run_all_daq_tests.py
```

### Run Individual Tests
```bash
# LabJack devices
python test_labjack1.py
python test_labjack_t4.py

# Network devices
python test_teledyne.py
python test_maxigauge.py
python test_qt_comprehensive.py

# Serial devices
python test_lakeshore_comprehensive.py
python test_ivc_comprehensive.py
```

### Check Test Status
```bash
# View recent test logs
tail -f labjack1_test.log
tail -f teledyne_test.log
tail -f all_daq_tests.log
```

## Device IP Addresses

| Device | IP Address | Port | Protocol |
|--------|------------|------|----------|
| Teledyne | 172.29.36.192 | 101 | TCP |
| MaxiGauge | 172.29.36.194 | 8000 | TCP |
| QT PLC | 172.29.36.195 | 502/503 | Modbus TCP |

## Serial Ports

| Device | Default Port | Baud Rate |
|--------|--------------|-----------|
| LakeShore | COM4 | 9600 |
| IVC | COM7 | 9600 |

## Success Criteria

- **Connection Test**: Device initializes successfully
- **Data Reading**: ≥80% success rate over 10-15 seconds
- **Error Handling**: Graceful failure with invalid configs
- **Stress Test**: Stable through 3 start/stop cycles
- **Exit Code**: 0 = success, 1 = failure

## Common Issues

| Issue | Solution |
|-------|----------|
| Device not found | Check USB/network connections |
| Permission denied | Add user to dialout group (Linux) |
| Import errors | `pip install u3 numpy pyModbusTCP pyserial` |
| Network timeout | Check firewall and IP addresses |
| Serial errors | Verify COM port and baud rate |

## Log Files

Each test creates: `{device}_test.log`
Master suite creates: `all_daq_tests.log`

## Test Components

1. **Configuration** - Device settings validation
2. **Connection** - Basic communication test
3. **Data Reading** - Extended data collection
4. **Error Handling** - Invalid config testing
5. **Stress** - Start/stop cycle testing
6. **Processing** - Data conversion validation 