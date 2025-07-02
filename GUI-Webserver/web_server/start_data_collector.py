#!/usr/bin/env python3
"""
Start script for the data collector
"""

import os
import sys
import subprocess
import time
import signal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import sqlite3
        import requests
        logger.info("✓ All required dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.error("Please install required packages: pip install flask requests")
        return False

def check_database_directory():
    """Ensure the database directory exists"""
    db_dir = "../instance"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created database directory: {db_dir}")
    else:
        logger.info(f"Database directory exists: {db_dir}")

def start_data_collector():
    """Start the data collector Flask application"""
    if not check_dependencies():
        return False
    
    check_database_directory()
    
    logger.info("Starting Data Collector...")
    logger.info("The data collector will receive data via HTTP endpoints:")
    logger.info("  - POST /receive_hmi_data - for HMI data (18 values)")
    logger.info("  - POST /data - for merged data (18+ values)")
    logger.info("  - GET /query_db - for querying stored data")
    logger.info("  - GET /health - for health checks")
    logger.info("")
    logger.info("Press Ctrl+C to stop the data collector")
    
    try:
        # Import and run the data collector
        from data_collector import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Data collector stopped by user")
    except Exception as e:
        logger.error(f"Error starting data collector: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_data_collector() 