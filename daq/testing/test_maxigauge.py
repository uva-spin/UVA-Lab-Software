#!/usr/bin/env python3
"""
Test script for MaxiGaugeReader (Pfeiffer MaxiGauge Pressure Controller)
Tests connection, data reading, and proper cleanup for TCP-based pressure gauge:
- Channel 1-6: Pressure readings from various sensors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')))
import time
import logging
import traceback
from datetime import datetime
from devices._MaxiGaugeReader import MaxiGaugeReader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('maxigauge_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_maxigauge_connection():
    """Test basic connection to MaxiGauge"""
    logger.info("=" * 60)
    logger.info("Testing MaxiGauge Connection")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing MaxiGaugeReader")
        reader = MaxiGaugeReader(check_interval=1)
        
        logger.info("Starting MaxiGaugeReader")
        reader.start()
        
        logger.info("Connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        if reader:
            logger.info("Cleaning up connection test")
            reader.stop()

def test_maxigauge_data_reading():
    """Test data reading from all channels"""
    logger.info("=" * 60)
    logger.info("Testing MaxiGauge Data Reading")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing MaxiGaugeReader for data reading test")
        reader = MaxiGaugeReader(check_interval=1)
        
        logger.info("Starting MaxiGaugeReader")
        reader.start()
        
        # Wait for initialization and first data collection
        logger.info("Waiting for device initialization and first data collection...")
        time.sleep(3)
        
        logger.info("Testing data reading for 15 seconds...")
        logger.info("Channel mapping:")
        logger.info("  [0] Pressure Sensor 1")
        logger.info("  [1] Pressure Sensor 2")
        logger.info("  [2] Pressure Sensor 3")
        logger.info("  [3] Pressure Sensor 4")
        logger.info("  [4] Pressure Sensor 5")
        logger.info("  [5] Pressure Sensor 6")
        logger.info("-" * 60)
        
        successful_readings = 0
        total_readings = 0
        
        for i in range(15):
            try:
                data = reader.get_latest_data()
                total_readings += 1
                
                if data and len(data) == 6:
                    # Check if we have valid data (not all None)
                    if any(val is not None for val in data):
                        successful_readings += 1
                        logger.info(f"Sample {i+1:2d}: "
                                  f"P1={data[0]:10.2e}, "
                                  f"P2={data[1]:10.2e}, "
                                  f"P3={data[2]:10.2e}, "
                                  f"P4={data[3]:10.2e}, "
                                  f"P5={data[4]:10.2e}, "
                                  f"P6={data[5]:10.2e}")
                    else:
                        logger.warning(f"Sample {i+1:2d}: All values are None")
                else:
                    logger.warning(f"Sample {i+1:2d}: Invalid data format - {data}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error reading sample {i+1}: {e}")
        
        success_rate = (successful_readings / total_readings) * 100 if total_readings > 0 else 0
        logger.info("-" * 60)
        logger.info(f"Data reading test completed:")
        logger.info(f"  Total readings: {total_readings}")
        logger.info(f"  Successful readings: {successful_readings}")
        logger.info(f"  Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("Data reading test PASSED!")
            return True
        else:
            logger.warning("Data reading test FAILED - Success rate below 80%")
            return False
            
    except Exception as e:
        logger.error(f"Data reading test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        if reader:
            logger.info("Cleaning up data reading test")
            reader.stop()

def test_maxigauge_network_config():
    """Test network configuration and settings"""
    logger.info("=" * 60)
    logger.info("Testing MaxiGauge Network Configuration")
    logger.info("=" * 60)
    
    reader = MaxiGaugeReader()
    
    logger.info("Network Configuration:")
    logger.info(f"  TCP IP: {reader.MAXIGAUGE_TCP_IP}")
    logger.info(f"  TCP Port: {reader.MAXIGAUGE_TCP_PORT}")
    logger.info(f"  Baudrate: {reader.baudrate}")
    logger.info(f"  Timeout: {reader.timeout} seconds")
    logger.info(f"  Check Interval: {reader.check_interval} seconds")
    logger.info(f"  Connection Retry Interval: {reader.connection_retry_interval} seconds")
    
    logger.info("Network configuration test completed!")
    return True

def test_maxigauge_stress():
    """Stress test - rapid start/stop cycles"""
    logger.info("=" * 60)
    logger.info("Testing MaxiGauge Stress Test (Start/Stop Cycles)")
    logger.info("=" * 60)
    
    try:
        for cycle in range(3):
            logger.info(f"Stress test cycle {cycle + 1}/3")
            reader = MaxiGaugeReader(check_interval=0.5)
            
            try:
                reader.start()
                time.sleep(2)
                
                # Get a few readings
                for i in range(3):
                    data = reader.get_latest_data()
                    logger.info(f"  Cycle {cycle + 1}, Reading {i + 1}: {data}")
                    time.sleep(0.5)
                    
            finally:
                reader.stop()
                time.sleep(1)  # Brief pause between cycles
        
        logger.info("Stress test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_maxigauge_socket_read():
    """Test direct socket reading functionality"""
    logger.info("=" * 60)
    logger.info("Testing MaxiGauge Direct Socket Reading")
    logger.info("=" * 60)
    
    reader = MaxiGaugeReader()
    
    try:
        logger.info("Testing direct socket read...")
        data = reader._socket_read()
        
        if data and isinstance(data, list):
            logger.info(f"Direct socket read successful: {len(data)} pressure values")
            logger.info(f"First 3 values: {data[:3]}")
            return True
        else:
            logger.warning(f"Direct socket read returned invalid data: {data}")
            return False
            
    except Exception as e:
        logger.error(f"Direct socket read failed: {e}")
        return False

def test_maxigauge_commands():
    """Test MaxiGauge command functionality"""
    logger.info("=" * 60)
    logger.info("Testing MaxiGauge Commands")
    logger.info("=" * 60)
    
    reader = None
    try:
        reader = MaxiGaugeReader()
        
        # Test connection first
        if not reader._socket_connection():
            logger.warning("Cannot test commands - no connection")
            return False
        
        # Test various commands
        commands = ['PRX', 'TID', 'VER']
        
        for command in commands:
            logger.info(f"Testing command: {command}")
            response = reader.send_command(command)
            
            if response:
                logger.info(f"  Command '{command}' successful: {response[:50]}...")
            else:
                logger.warning(f"  Command '{command}' failed or no response")
        
        logger.info("Command test completed!")
        return True
        
    except Exception as e:
        logger.error(f"Command test failed: {e}")
        return False
    finally:
        if reader:
            reader.stop()

def main():
    """Run all MaxiGauge tests"""
    logger.info("Starting MaxiGauge Comprehensive Test Suite")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Network Configuration Test", test_maxigauge_network_config),
        ("Connection Test", test_maxigauge_connection),
        ("Direct Socket Read Test", test_maxigauge_socket_read),
        ("Command Test", test_maxigauge_commands),
        ("Data Reading Test", test_maxigauge_data_reading),
        ("Stress Test", test_maxigauge_stress),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"Tests passed: {passed}/{total}")
    logger.info(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! MaxiGauge is working correctly.")
        return True
    else:
        logger.error(f"❌ {total - passed} test(s) failed. Please check the logs.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1) 