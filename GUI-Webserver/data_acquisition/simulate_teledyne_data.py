#!/usr/bin/env python3
"""
Simulate real-time teledyne flow data being written to the CSV file
This script can be used to test the data acquisition system
"""

import time
import csv
from datetime import datetime
import os

def simulate_teledyne_data():
    """Simulate writing teledyne flow data to the CSV file"""
    
    # Path to the teledyne flow CSV file
    csv_path = "../static/csv/teledyne_flow.csv"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    print(f"Simulating teledyne flow data to: {csv_path}")
    print("Press Ctrl+C to stop...")
    
    # Initial values
    flow_1 = 25.0
    flow_2 = 26.0
    flow_3 = 24.0
    
    try:
        while True:
            # Generate timestamp
            timestamp = datetime.now().isoformat()
            
            # Add some variation to the flow values
            flow_1 += 0.1
            flow_2 += 0.15
            flow_3 += 0.05
            
            # Keep values in reasonable range
            flow_1 = flow_1 % 30.0 + 20.0
            flow_2 = flow_2 % 30.0 + 20.0
            flow_3 = flow_3 % 30.0 + 20.0
            
            # Write to CSV file
            with open(csv_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, round(flow_1, 2), round(flow_2, 2), round(flow_3, 2)])
            
            print(f"Added data: {timestamp}, {round(flow_1, 2)}, {round(flow_2, 2)}, {round(flow_3, 2)}")
            
            # Wait 2 seconds before adding next data point
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")

if __name__ == "__main__":
    simulate_teledyne_data() 