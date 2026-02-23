#!/usr/bin/env python3
"""
Test script for LabJackReader_2 with T4 model
Tests reading from AIN1 and AIN2 channels
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')))
import time
import logging
from devices._LabJackReader import LabJackReader_2

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(os.path.dirname(current_dir), 'data_logs', 'labjack_debug.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logger.addHandler(logging.FileHandler(log_path))

def test_labjack_t4():
    """Test LabJackReader_2 with T4 model"""
    reader = None
    try:
        logger.info("Initializing LabJackReader_2 for T4 model")
        reader = LabJackReader_2(check_interval=1)
        
        logger.info("Starting LabJackReader_2")
        reader.start()
        
        # Wait a moment for initialization
        time.sleep(2)
        
        logger.info("Testing data reading for 10 seconds...")
        for i in range(10):
            data = reader.get_latest_data()
            logger.info(f"Sample {i+1}: AIN1 (Flow Meter 1) = {data[0]:.6f}, AIN2 (Flow Meter 2) = {data[1]:.6f}")
            time.sleep(1)
            
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False
    finally:
        if reader:
            logger.info("Stopping LabJackReader_2")
            reader.stop()
    
    return True

if __name__ == "__main__":
    success = test_labjack_t4()
    sys.exit(0 if success else 1) 