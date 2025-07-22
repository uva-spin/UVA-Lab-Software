#!/usr/bin/env python3
"""
Quick LakeShore Reader Test

A simple script to quickly test LakeShore reader functionality.
Useful for basic connectivity and data reading verification.
"""

import time
from _LakeShoreReader import LakeShoreReader

def quick_test():
    """Quick test of LakeShore reader."""
    
    print("LakeShore Quick Test")
    print("=" * 30)
    
    # Create reader (adjust port as needed)
    reader = LakeShoreReader(port="COM4")
    
    try:
        # Start connection
        print("Starting connection...")
        if not reader.start():
            print("Failed to start connection!")
            return
        
        print("Connection started successfully!")
        
        # Start data stream
        print("Starting data stream...")
        if not reader.data_stream():
            print("Failed to start data stream!")
            return
        
        print("Data stream started!")
        
        # Collect a few data points
        print("\nCollecting data...")
        for i in range(5):
            data = reader.get_latest_data()
            
            print(f"Reading {i+1}: {data}")
            
            print()
            
            time.sleep(1)
        
        print("Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up...")
        reader.stop()
        print("Done!")

if __name__ == "__main__":
    quick_test() 