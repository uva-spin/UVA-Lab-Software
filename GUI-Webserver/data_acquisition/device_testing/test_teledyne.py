#!/usr/bin/env python3
"""
Test script for TeledyneReader (Teledyne THCD-401 Flow Meter)
Tests connection, data reading, and proper cleanup for TCP-based flow meter:
- Channel 1: Flow rate 1
- Channel 2: Flow rate 2  
- Channel 3: Flow rate 3
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
print(f"Added to path: {project_root}")
import time
import logging
import traceback
from datetime import datetime
from data_acquisition.daq._TeledyneReader import TeledyneDataReader

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(os.path.dirname(current_dir), 'data_logs', 'teledyne_debug.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logger.addHandler(logging.FileHandler(log_path))

def test_teledyne_connection():
    """Test basic connection to Teledyne THCD-401"""
    logger.info("=" * 60)
    logger.info("Testing Teledyne Connection")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing TeledyneDataReader")
        reader = TeledyneDataReader(check_interval=1)
        
        logger.info("Starting TeledyneDataReader")
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

def test_teledyne_data_reading():
    """Test data reading from all channels"""
    logger.info("=" * 60)
    logger.info("Testing Teledyne Data Reading")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing TeledyneDataReader for data reading test")
        reader = TeledyneDataReader(check_interval=1)
        
        logger.info("Starting TeledyneDataReader")
        reader.start()
        
        # Wait for initialization and first data collection
        logger.info("Waiting for device initialization and first data collection...")
        time.sleep(3)
        
        logger.info("Testing data reading for 15 seconds...")
        logger.info("Channel mapping:")
        logger.info("  [0] Flow Rate 1")
        logger.info("  [1] Flow Rate 2")
        logger.info("  [2] Flow Rate 3")
        logger.info("-" * 60)
        
        successful_readings = 0
        total_readings = 0
        
        for i in range(15):
            try:
                data = reader.get_latest_data()
                total_readings += 1
                
                if data and len(data) == 3:
                    # Check if we have valid data (not all None)
                    if any(val is not None for val in data):
                        successful_readings += 1
                        logger.info(f"Sample {i+1:2d}: "
                                  f"Flow1={data[0]:8.3f}, "
                                  f"Flow2={data[1]:8.3f}, "
                                  f"Flow3={data[2]:8.3f}")
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

def test_teledyne_network_config():
    """Test network configuration and settings"""
    logger.info("=" * 60)
    logger.info("Testing Teledyne Network Configuration")
    logger.info("=" * 60)
    
    reader = TeledyneDataReader()
    
    logger.info("Network Configuration:")
    logger.info(f"  TCP IP: {reader.TELEDYNE_THCD_401_TCP_IP}")
    logger.info(f"  TCP Port: {reader.TELEDYNE_THCD_401_TCP_PORT}")
    logger.info(f"  Unit ID: {reader.TELEDYNE_THCD_401_TCP_UNIT_ID}")
    logger.info(f"  Check Interval: {reader.check_interval} seconds")
    
    logger.info("Network configuration test completed!")
    return True

def test_teledyne_stress():
    """Stress test - rapid start/stop cycles"""
    logger.info("=" * 60)
    logger.info("Testing Teledyne Stress Test (Start/Stop Cycles)")
    logger.info("=" * 60)
    
    try:
        for cycle in range(3):
            logger.info(f"Stress test cycle {cycle + 1}/3")
            reader = TeledyneDataReader(check_interval=0.5)
            
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

def test_teledyne_socket_read():
    """Test direct socket reading functionality"""
    logger.info("=" * 60)
    logger.info("Testing Teledyne Direct Socket Reading")
    logger.info("=" * 60)
    
    reader = TeledyneDataReader()
    
    try:
        logger.info("Testing direct socket read...")
        data = reader._socket_read()
        
        if data and len(data) == 3:
            logger.info(f"Direct socket read successful: {data}")
            return True
        else:
            logger.warning(f"Direct socket read returned invalid data: {data}")
            return False
            
    except Exception as e:
        logger.error(f"Direct socket read failed: {e}")
        return False

def main():
    """Run all Teledyne tests"""
    logger.info("Starting Teledyne Comprehensive Test Suite")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Network Configuration Test", test_teledyne_network_config),
        ("Connection Test", test_teledyne_connection),
        ("Direct Socket Read Test", test_teledyne_socket_read),
        ("Data Reading Test", test_teledyne_data_reading),
        ("Stress Test", test_teledyne_stress),
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
        logger.info("🎉 ALL TESTS PASSED! Teledyne is working correctly.")
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