#!/usr/bin/env python3
"""
Test script for LabJackReader_2 with T4 model
Tests reading from AIN1 and AIN2 channels
"""

import sys
import time
import logging
from _LabJackReader import LabJackReader_2

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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