#!/usr/bin/env python3
"""
Test script for QTReader class
Tests reading QT data using the new QTReader class
"""

import sys
import time
import logging
from _QTReader import QTReader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_qt_reader():
    """Test QTReader class"""
    try:
        # Test configuration (you may need to adjust these values)
        plc_ip = "192.168.0.1"  # Default from config
        unit_id = 2
        int_port = 503
        float_port = 502
        num_reg_to_read = 36
        
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
            "TI523.AI.Value"
        ]
        
        logger.info("Initializing QTReader")
        qt_reader = QTReader(
            plc_ip=plc_ip,
            unit_id=unit_id,
            int_port=int_port,
            float_port=float_port,
            num_reg_to_read=num_reg_to_read,
            labels=labels
        )
        
        logger.info("Testing QT data reading")
        qt_data = qt_reader.read_qt_data()
        
        if qt_data is not None:
            logger.info(f"Successfully read QT data: {len(qt_data)} values")
            logger.info(f"First 3 values: {qt_data[:3]}")
            logger.info(f"Last 3 values: {qt_data[-3:]}")
            
            # Test with labels
            for i, (label, value) in enumerate(zip(labels, qt_data)):
                logger.info(f"{label}: {value}")
            
            return True
        else:
            logger.error("Failed to read QT data")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False
    finally:
        try:
            if 'qt_reader' in locals():
                qt_reader.close_connections()
                logger.info("QT reader connections closed")
        except Exception as e:
            logger.warning(f"Error closing connections: {e}")

if __name__ == "__main__":
    success = test_qt_reader()
    sys.exit(0 if success else 1) 