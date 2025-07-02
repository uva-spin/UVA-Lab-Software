#!/usr/bin/env python3
"""
Startup script for the data collection system.
This script initializes the database and starts the data collector.
"""

import os
import sys
import sqlite3
from pathlib import Path

def ensure_instance_directory():
    """Ensure the instance directory exists"""
    instance_dir = Path("../instance")
    instance_dir.mkdir(exist_ok=True)
    print(f"Instance directory ready: {instance_dir.absolute()}")

def initialize_database():
    """Initialize the database with the schema"""
    db_path = "../instance/flaskr.sqlite"
    
    # Import the data collector to set up the database
    from data_collector import DataCollector
    
    collector = DataCollector(db_path=db_path)
    print(f"Database initialized: {db_path}")
    
    return collector

def main():
    """Main startup function"""
    print("Starting Data Collection System...")
    
    # Ensure instance directory exists
    ensure_instance_directory()
    
    # Initialize database
    collector = initialize_database()
    
    # Start CSV monitoring
    collector.start_csv_monitoring(interval=30)
    
    # Import and start the Flask app
    from data_collector import app
    
    print("Data collector ready!")
    print("HMI data endpoint: http://localhost:5000/receive_hmi_data")
    print("Health check endpoint: http://localhost:5000/health")
    print("CSV monitoring interval: 30 seconds")
    print("\nStarting Flask server...")
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main() 