#!/usr/bin/env python3
"""
Test script for QTReader (Modbus TCP PLC Reader)
Tests connection, data reading, and proper cleanup for Modbus TCP-based PLC:
- Integer and float register readings
- 18 QT data values
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
from data_acquisition.daq._QTReader import QTReader

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(os.path.dirname(current_dir), 'data_logs', 'qt_debug.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logger.addHandler(logging.FileHandler(log_path))

def test_qt_connection():
    """Test basic connection to QT PLC"""
    logger.info("=" * 60)
    logger.info("Testing QT Connection")
    logger.info("=" * 60)
    
    try:
        logger.info("Initializing QTReader")
        reader = QTReader(
            plc_ip="172.29.36.195",  # From config
            unit_id=2,
            int_port=503,
            float_port=502,
            num_reg_to_read=36
        )
        
        logger.info("Testing QT data reading")
        qt_data = reader.read_qt_data()
        
        if qt_data is not None:
            logger.info("Connection test successful!")
            return True
        else:
            logger.error("Connection test failed - no data received")
            return False
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_qt_data_reading():
    """Test data reading from all registers"""
    logger.info("=" * 60)
    logger.info("Testing QT Data Reading")
    logger.info("=" * 60)
    
    try:
        logger.info("Initializing QTReader for data reading test")
        reader = QTReader(
            plc_ip="172.29.36.195",  # From config
            unit_id=2,
            int_port=503,
            float_port=502,
            num_reg_to_read=36
        )
        
        logger.info("Testing data reading for 10 iterations...")
        logger.info("Reading 18 QT data values from Modbus registers")
        logger.info("-" * 60)
        
        successful_readings = 0
        total_readings = 0
        
        for i in range(10):
            try:
                qt_data = reader.read_qt_data()
                total_readings += 1
                
                if qt_data is not None and len(qt_data) == 18:
                    successful_readings += 1
                    logger.info(f"Sample {i+1:2d}: {len(qt_data)} values read")
                    logger.info(f"  First 3 values: {qt_data[:3]}")
                    logger.info(f"  Last 3 values: {qt_data[-3:]}")
                else:
                    logger.warning(f"Sample {i+1:2d}: Invalid data - {qt_data}")
                
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

def test_qt_network_config():
    """Test network configuration and settings"""
    logger.info("=" * 60)
    logger.info("Testing QT Network Configuration")
    logger.info("=" * 60)
    
    reader = QTReader(
        plc_ip="172.29.36.195",
        unit_id=2,
        int_port=503,
        float_port=502,
        num_reg_to_read=36
    )
    
    logger.info("Network Configuration:")
    logger.info(f"  PLC IP: {reader.plc_ip}")
    logger.info(f"  Unit ID: {reader.unit_id}")
    logger.info(f"  Integer Port: {reader.int_port}")
    logger.info(f"  Float Port: {reader.float_port}")
    logger.info(f"  Number of Registers: {reader.num_reg_to_read}")
    
    logger.info("Network configuration test completed!")
    return True

def test_qt_stress():
    """Stress test - rapid connection cycles"""
    logger.info("=" * 60)
    logger.info("Testing QT Stress Test (Connection Cycles)")
    logger.info("=" * 60)
    
    try:
        for cycle in range(3):
            logger.info(f"Stress test cycle {cycle + 1}/3")
            reader = QTReader(
                plc_ip="172.29.36.195",
                unit_id=2,
                int_port=503,
                float_port=502,
                num_reg_to_read=36
            )
            
            try:
                # Get a few readings
                for i in range(3):
                    qt_data = reader.read_qt_data()
                    if qt_data:
                        logger.info(f"  Cycle {cycle + 1}, Reading {i + 1}: {len(qt_data)} values")
                    else:
                        logger.warning(f"  Cycle {cycle + 1}, Reading {i + 1}: No data")
                    time.sleep(0.5)
                    
            finally:
                reader.close_connections()
                time.sleep(1)  # Brief pause between cycles
        
        logger.info("Stress test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_qt_data_processing():
    """Test data processing and conversion"""
    logger.info("=" * 60)
    logger.info("Testing QT Data Processing")
    logger.info("=" * 60)
    
    reader = QTReader(
        plc_ip="172.29.36.195",
        unit_id=2,
        int_port=503,
        float_port=502,
        num_reg_to_read=36
    )
    
    # Test 2's complement conversion
    test_regs = [0, 32767, 32768, 65535]  # Test various register values
    converted = reader._get_list_2comp(test_regs, 16)
    
    logger.info("2's Complement Conversion Test:")
    for i, (original, converted_val) in enumerate(zip(test_regs, converted)):
        logger.info(f"  Register {i}: {original} -> {converted_val}")
    
    logger.info("Data processing test completed!")
    return True

def test_qt_labels():
    """Test QT data with labels"""
    logger.info("=" * 60)
    logger.info("Testing QT Data with Labels")
    logger.info("=" * 60)
    
    # Define labels for QT data
    labels = [
        "FC501.AI.Value",
        "FC501_OUT.Value", 
        "FC502.AI.Value",
        "FC502_OUT.Value",
        "LIT501.AI.Value",
        "PT501.AI.Value",
        "PT502.AI.Value",
        "PT503.AI.Value",
        "PT504.AI.Value",
        "AIT501.AI.Value",
        "TI501.AI.Value",
        "TI502.AI.Value",
        "TI503.AI.Value",
        "TI504.AI.Value",
        "TI505.AI.Value",
        "TI523.AI.Value",
        "Value_17",
        "Value_18"
    ]
    
    reader = QTReader(
        plc_ip="172.29.36.195",
        unit_id=2,
        int_port=503,
        float_port=502,
        num_reg_to_read=36,
        labels=labels
    )
    
    try:
        qt_data = reader.read_qt_data()
        
        if qt_data and len(qt_data) >= 16:
            logger.info("QT Data with Labels:")
            for i, (label, value) in enumerate(zip(labels[:16], qt_data[:16])):
                logger.info(f"  {label}: {value}")
            return True
        else:
            logger.warning("No data received for label test")
            return False
            
    except Exception as e:
        logger.error(f"Label test failed: {e}")
        return False
    finally:
        reader.close_connections()

def test_qt_error_handling():
    """Test error handling with invalid configuration"""
    logger.info("=" * 60)
    logger.info("Testing QT Error Handling")
    logger.info("=" * 60)
    
    try:
        logger.info("Testing with invalid IP...")
        reader = QTReader(
            plc_ip="192.168.1.999",  # Invalid IP
            unit_id=2,
            int_port=503,
            float_port=502,
            num_reg_to_read=36
        )
        
        # This should fail gracefully
        qt_data = reader.read_qt_data()
        if qt_data is None:
            logger.info("Error handling test PASSED - correctly failed with invalid IP")
            return True
        else:
            logger.warning("Error handling test FAILED - should have failed with invalid IP")
            return False
            
    except Exception as e:
        logger.info(f"Error handling test PASSED - exception caught: {e}")
        return True

def main():
    """Run all QT tests"""
    logger.info("Starting QT Comprehensive Test Suite")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Network Configuration Test", test_qt_network_config),
        ("Data Processing Test", test_qt_data_processing),
        ("Error Handling Test", test_qt_error_handling),
        ("Connection Test", test_qt_connection),
        ("Data Reading Test", test_qt_data_reading),
        ("Labels Test", test_qt_labels),
        ("Stress Test", test_qt_stress),
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
        logger.info("🎉 ALL TESTS PASSED! QT is working correctly.")
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