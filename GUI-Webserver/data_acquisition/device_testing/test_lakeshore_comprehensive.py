#!/usr/bin/env python3
"""
Test script for LakeShoreReader (LakeShore Temperature Controller)
Tests connection, data reading, and proper cleanup for serial-based temperature controller:
- Temperature readings from various sensors
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
print(f"Added to path: {project_root}")
import time
import os
import logging
import traceback
from datetime import datetime
from data_acquisition.daq._LakeShoreReader import LakeShoreReader

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(os.path.dirname(current_dir), 'data_logs', 'lakeshore_debug.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logger.addHandler(logging.FileHandler(log_path))

def test_lakeshore_connection():
    """Test basic connection to LakeShore"""
    logger.info("=" * 60)
    logger.info("Testing LakeShore Connection")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing LakeShoreReader")
        reader = LakeShoreReader(port="COM4")  # Adjust port as needed
        
        logger.info("Starting LakeShoreReader")
        if not reader.start():
            logger.error("Failed to start LakeShoreReader")
            return False
        
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

def test_lakeshore_data_reading():
    """Test data reading from all channels"""
    logger.info("=" * 60)
    logger.info("Testing LakeShore Data Reading")
    logger.info("=" * 60)
    
    reader = None
    try:
        logger.info("Initializing LakeShoreReader for data reading test")
        reader = LakeShoreReader(port="COM4")  # Adjust port as needed
        
        logger.info("Starting LakeShoreReader")
        if not reader.start():
            logger.error("Failed to start LakeShoreReader")
            return False
        
        logger.info("Starting data stream")
        if not reader.data_stream():
            logger.error("Failed to start data stream")
            return False
        
        # Wait for initialization and first data collection
        logger.info("Waiting for device initialization and first data collection...")
        time.sleep(3)
        
        logger.info("Testing data reading for 15 seconds...")
        logger.info("Reading temperature data from LakeShore sensors")
        logger.info("-" * 60)
        
        successful_readings = 0
        total_readings = 0
        
        for i in range(15):
            try:
                data = reader.get_latest_data()
                total_readings += 1
                
                if data is not None:
                    successful_readings += 1
                    logger.info(f"Sample {i+1:2d}: Temperature = {data}")
                else:
                    logger.warning(f"Sample {i+1:2d}: No data received")
                
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

def test_lakeshore_serial_config():
    """Test serial configuration and settings"""
    logger.info("=" * 60)
    logger.info("Testing LakeShore Serial Configuration")
    logger.info("=" * 60)
    
    reader = LakeShoreReader(port="COM4")  # Adjust port as needed
    
    logger.info("Serial Configuration:")
    logger.info(f"  Port: {reader.port}")
    logger.info(f"  Baudrate: {reader.baudrate}")
    logger.info(f"  Timeout: {reader.timeout} seconds")
    logger.info(f"  Check Interval: {reader.check_interval} seconds")
    
    logger.info("Serial configuration test completed!")
    return True

def test_lakeshore_stress():
    """Stress test - rapid start/stop cycles"""
    logger.info("=" * 60)
    logger.info("Testing LakeShore Stress Test (Start/Stop Cycles)")
    logger.info("=" * 60)
    
    try:
        for cycle in range(3):
            logger.info(f"Stress test cycle {cycle + 1}/3")
            reader = LakeShoreReader(port="COM4", check_interval=0.5)  # Adjust port as needed
            
            try:
                if reader.start() and reader.data_stream():
                    time.sleep(2)
                    
                    # Get a few readings
                    for i in range(3):
                        data = reader.get_latest_data()
                        logger.info(f"  Cycle {cycle + 1}, Reading {i + 1}: {data}")
                        time.sleep(0.5)
                else:
                    logger.warning(f"  Cycle {cycle + 1}: Failed to start")
                    
            finally:
                reader.stop()
                time.sleep(1)  # Brief pause between cycles
        
        logger.info("Stress test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_lakeshore_error_handling():
    """Test error handling with invalid port"""
    logger.info("=" * 60)
    logger.info("Testing LakeShore Error Handling")
    logger.info("=" * 60)
    
    try:
        logger.info("Testing with invalid port...")
        reader = LakeShoreReader(port="INVALID_PORT")
        
        # This should fail gracefully
        if not reader.start():
            logger.info("Error handling test PASSED - correctly failed with invalid port")
            return True
        else:
            logger.warning("Error handling test FAILED - should have failed with invalid port")
            return False
            
    except Exception as e:
        logger.info(f"Error handling test PASSED - exception caught: {e}")
        return True

def main():
    """Run all LakeShore tests"""
    logger.info("Starting LakeShore Comprehensive Test Suite")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Serial Configuration Test", test_lakeshore_serial_config),
        ("Error Handling Test", test_lakeshore_error_handling),
        ("Connection Test", test_lakeshore_connection),
        ("Data Reading Test", test_lakeshore_data_reading),
        ("Stress Test", test_lakeshore_stress),
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
        logger.info("🎉 ALL TESTS PASSED! LakeShore is working correctly.")
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