#!/usr/bin/env python3
"""
Test script for teledyne data reading functionality
"""

import time
import os
import sys

# Add the current directory to the path so we can import from the main script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from standalone_data_acquisition import TeledyneDataReader

def test_teledyne_reader():
    """Test the teledyne data reader"""
    print("Testing Teledyne Data Reader...")
    
    # Create a test CSV file
    test_csv_path = "test_teledyne_flow.csv"
    
    # Write some test data
    with open(test_csv_path, 'w') as f:
        f.write("2025-02-20T14:30:15.123456,25.5,26.2,24.8\n")
        f.write("2025-02-20T14:30:20.234567,25.6,26.3,24.9\n")
    
    # Create and start the reader
    reader = TeledyneDataReader(test_csv_path, check_interval=0.5)
    reader.start()
    
    try:
        # Wait a moment for the reader to process initial data
        time.sleep(1)
        
        # Get the data
        data1 = reader.get_latest_data()
        data2 = reader.get_latest_data()
        
        print(f"First data point: {data1}")
        print(f"Second data point: {data2}")
        
        # Add more data to the file
        with open(test_csv_path, 'a') as f:
            f.write("2025-02-20T14:30:25.345678,25.7,26.4,25.0\n")
        
        # Wait for the reader to detect new data
        time.sleep(1)
        
        # Get the new data
        data3 = reader.get_latest_data()
        print(f"New data point: {data3}")
        
        # Test with no data
        no_data = reader.get_latest_data()
        print(f"No data available: {no_data}")
        
        print("Test completed successfully!")
        
    finally:
        reader.stop()
        # Clean up test file
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

if __name__ == "__main__":
    test_teledyne_reader() 