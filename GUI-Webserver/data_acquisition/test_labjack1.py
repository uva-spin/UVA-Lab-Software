#!/usr/bin/env python3
"""
Test script for LabJackReader_1 (U3 model)
Tests connection, data reading, and proper cleanup for all 6 analog channels:
- AIN0: Root Exhaust Pressure (Torr)
- AIN1: Buffer Pressure (PSI)
- AIN2: Magnet Pressure (PSI)
- AIN3: Purifier Inlet Pressure (PSI)
- AIN4: Fridge Vapor Pressure (Torr)
- AIN6: Thermocouple (Celsius)
"""

import sys
import time
import logging
import traceback
from datetime import datetime
from _LabJackReader import LabJackReader_1

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('labjack1_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_labjack1_connection():
    """Test basic connection to LabJack U3"""
    logger.info("=" * 60)
    logger.info("Testing LabJack1 Connection")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing LabJackReader_1 for U3 model")
        reader = LabJackReader_1(check_interval=1)
        
        logger.info("Starting LabJackReader_1")
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

def test_labjack1_data_reading():
    """Test data reading from all channels"""
    logger.info("=" * 60)
    logger.info("Testing LabJack1 Data Reading")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing LabJackReader_1 for data reading test")
        reader = LabJackReader_1(check_interval=1)
        
        logger.info("Starting LabJackReader_1")
        reader.start()
        
        # Wait for initialization and first data collection
        logger.info("Waiting for device initialization and first data collection...")
        time.sleep(3)
        
        logger.info("Testing data reading for 15 seconds...")
        logger.info("Channel mapping:")
        logger.info("  [0] Root Exhaust Pressure (Torr)")
        logger.info("  [1] Buffer Pressure (PSI)")
        logger.info("  [2] Magnet Pressure (PSI)")
        logger.info("  [3] Purifier Inlet Pressure (PSI)")
        logger.info("  [4] Fridge Vapor Pressure (Torr)")
        logger.info("  [5] Thermocouple (Celsius)")
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
                                  f"Root Exhaust={data[0]:8.3f} Torr, "
                                  f"Buffer={data[1]:8.3f} PSI, "
                                  f"Magnet={data[2]:8.3f} PSI, "
                                  f"Purifier={data[3]:8.3f} PSI, "
                                  f"Fridge Vapor={data[4]:8.3f} Torr, "
                                  f"Thermocouple={data[5]:8.3f} C")
                    else:
                        logger.warning(f"Sample {i+1:2d}: All values are None")
                else:
                    logger.warning(f"Sample {i+1:2d}: Invalid data format - {data}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error reading sample {i+1}: {e}")
        
        logger.info("-" * 60)
        logger.info(f"Data reading test completed:")
        logger.info(f"  Total readings: {total_readings}")
        logger.info(f"  Successful readings: {successful_readings}")
    
            
    except Exception as e:
        logger.error(f"Data reading test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        if reader:
            logger.info("Cleaning up data reading test")
            reader.stop()

def test_labjack1_stress():
    """Stress test - rapid start/stop cycles"""
    logger.info("=" * 60)
    logger.info("Testing LabJack1 Stress Test (Start/Stop Cycles)")
    logger.info("=" * 60)
    
    try:
        for cycle in range(3):
            logger.info(f"Stress test cycle {cycle + 1}/3")
            reader = LabJackReader_1(check_interval=0.5)
            
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

def main():
    """Run all LabJack1 tests"""
    logger.info("Starting LabJack1 Comprehensive Test Suite")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Connection Test", test_labjack1_connection),
        ("Data Reading Test", test_labjack1_data_reading),
        ("Stress Test", test_labjack1_stress),
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
        logger.info("🎉 ALL TESTS PASSED! LabJack1 is working correctly.")
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