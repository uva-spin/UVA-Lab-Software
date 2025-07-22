#!/usr/bin/env python3
"""
Quick IVC Reader Test

A simple script to quickly test IVC reader functionality.
Useful for basic connectivity and data reading verification.
"""

import time
from _IVCReader import IVCReader

def quick_test():
    """Quick test of IVC reader."""
    
    print("IVC Quick Test")
    print("=" * 30)
    
    # Create reader (adjust port as needed)
    reader = IVCReader(port="COM7")
    
    try:
        # Start connection
        print("Starting connection...")
        if not reader.start():
            print("Failed to start connection!")
            print("Check if the device is connected and the port is correct.")
            return
        
        print("Connection started successfully!")
        
        # Start data stream
        print("Starting data stream...")
        if not reader.data_stream():
            print("Failed to start data stream!")
            return
        
        print("Data stream started!")
        
        # Wait a moment for data to start flowing
        print("Waiting for data to start flowing...")
        time.sleep(2)
        
        # Collect a few data points
        print("\nCollecting data...")
        for i in range(5):
            data = reader.get_latest_data()
            
            if data is not None:
                print(f"Reading {i+1}: {data}")
            else:
                print(f"Reading {i+1}: No data received")
            
            time.sleep(1)
        
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        reader.stop()
        print("Done!")

if __name__ == "__main__":
    quick_test() 