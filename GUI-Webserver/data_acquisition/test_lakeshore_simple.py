#!/usr/bin/env python3
"""
Simple LakeShore Reader Test - Raw vs Formatted Data

This script demonstrates the difference between raw and formatted data
from the LakeShore reader in a simple, easy-to-understand format.
"""

import time
import logging
from _LakeShoreReader import LakeShoreReader

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_raw_vs_formatted():
    """Test and display raw vs formatted data from LakeShore reader."""
    
    print("LakeShore Reader - Raw vs Formatted Data Test")
    print("=" * 50)
    
    # Create reader (adjust port as needed)
    reader = LakeShoreReader(port="COM4")
    
    try:
        # Start the reader
        print("Starting LakeShore reader...")
        if not reader.start():
            print("Failed to start reader!")
            return
        
        # Start data streaming
        print("Starting data stream...")
        if not reader.data_stream():
            print("Failed to start data stream!")
            return
        
        print("\nCollecting data for 10 seconds...")
        print("Press Ctrl+C to stop early\n")
        
        # Collect data for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                # Get both raw and formatted data
                raw_data = reader.get_latest_data()
                formatted_data = reader.get_formatted_data()
                
                # Display timestamp
                timestamp = time.strftime("%H:%M:%S")
                
                # Display raw data
                print(f"[{timestamp}] RAW DATA:")
                print(f"  Type: {type(raw_data)}")
                print(f"  Length: {len(raw_data)}")
                print(f"  Values: {raw_data}")
                
                # Display formatted data
                print(f"[{timestamp}] FORMATTED DATA:")
                if formatted_data:
                    for channel, value in formatted_data.items():
                        print(f"  {channel}: {value:.3f}")
                else:
                    print("  No formatted data available")
                
                print("-" * 40)
                
                time.sleep(1)  # Wait 1 second between readings
                
            except KeyboardInterrupt:
                print("\nStopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                break
    
    finally:
        # Clean up
        print("\nStopping LakeShore reader...")
        reader.stop()
        print("Test completed!")

def test_data_processing():
    """Test the data processing with sample data."""
    
    print("\n" + "=" * 50)
    print("DATA PROCESSING TEST")
    print("=" * 50)
    
    reader = LakeShoreReader()
    
    # Test with the sample data you showed in the terminal
    sample_data = b'\xab\xb0\xb9\xb9\xae\xb9\xb9\r\n'
    
    print(f"Sample raw data: {sample_data}")
    print(f"Sample data (hex): {sample_data.hex()}")
    print(f"Sample data (repr): {repr(sample_data)}")
    
    # Process the data
    processed = reader._clean_and_convert_data(sample_data)
    
    print(f"\nProcessed data: {processed}")
    print(f"Processed data type: {type(processed)}")
    print(f"Processed data length: {len(processed)}")
    
    # Show what each byte becomes
    print("\nByte-by-byte conversion:")
    for i, byte in enumerate(sample_data):
        if byte != b'\r' and byte != b'\n':
            ord_val = ord(byte)
            print(f"  Byte {i}: {byte} (hex: {byte.hex()}) -> ord() = {ord_val}")

if __name__ == "__main__":
    # Run the simple test
    test_raw_vs_formatted()
    
    # Run the data processing test
    test_data_processing() 