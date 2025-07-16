#!/usr/bin/env python3
"""
Comprehensive LakeShore Reader Test Script

This script demonstrates the LakeShore reader functionality by:
1. Creating a LakeShore reader instance
2. Starting the connection
3. Collecting data for a specified duration
4. Showing both raw and formatted output
5. Properly cleaning up resources

Usage:
    python test_lakeshore_comprehensive.py [port] [duration]

Examples:
    python test_lakeshore_comprehensive.py COM4 10
    python test_lakeshore_comprehensive.py /dev/ttyUSB0 30
"""

import sys
import time
import logging
from datetime import datetime
from _LakeShoreReader import LakeShoreReader

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('lakeshore_test.log')
    ]
)

def test_lakeshore_reader(port="COM4", duration=10):
    """
    Test the LakeShore reader with comprehensive output.
    
    Args:
        port (str): Serial port to use (e.g., "COM4", "/dev/ttyUSB0")
        duration (int): Duration to collect data in seconds
    """
    print("=" * 60)
    print("LAKESHORE READER COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Duration: {duration} seconds")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    reader = None
    try:
        # Create LakeShore reader instance
        print("\n1. Creating LakeShore reader instance...")
        reader = LakeShoreReader(port=port, baudrate=9600, timeout=2)
        print(f"   Reader created with port: {reader.port}")
        print(f"   Baudrate: {reader.baudrate}")
        print(f"   Timeout: {reader.timeout}")
        
        # Start the connection
        print("\n2. Starting LakeShore connection...")
        if reader.start():
            print("   ✓ Connection started successfully")
            print(f"   Connection status: {reader.is_connected()}")
        else:
            print("   ✗ Failed to start connection")
            return False
        
        # Start data streaming
        print("\n3. Starting data stream...")
        if reader.data_stream():
            print("   ✓ Data stream started successfully")
        else:
            print("   ✗ Failed to start data stream")
            return False
        
        # Collect data for specified duration
        print(f"\n4. Collecting data for {duration} seconds...")
        print("-" * 60)
        print("RAW DATA COLLECTION:")
        print("-" * 60)
        
        start_time = time.time()
        data_points = 0
        
        while time.time() - start_time < duration:
            try:
                # Get the latest data
                raw_data = reader.get_latest_data()
                formatted_data = reader.get_formatted_data()
                
                # Display raw data
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"[{timestamp}] Raw data: {raw_data}")
                
                # Display formatted data
                if formatted_data:
                    print(f"[{timestamp}] Formatted data:")
                    for channel, value in formatted_data.items():
                        print(f"           {channel}: {value:.3f}")
                
                data_points += 1
                time.sleep(0.5)  # Collect data every 0.5 seconds
                
            except KeyboardInterrupt:
                print("\n   Interrupted by user")
                break
            except Exception as e:
                print(f"   Error collecting data: {e}")
                break
        
        print("-" * 60)
        print(f"Data collection completed!")
        print(f"Total data points collected: {data_points}")
        print(f"Average collection rate: {data_points/duration:.1f} points/second")
        
        # Show final status
        print("\n5. Final status:")
        print(f"   Connection status: {reader.is_connected()}")
        print(f"   Thread alive: {reader.thread.is_alive() if reader.thread else False}")
        print(f"   Latest data: {reader.get_latest_data()}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        return False
        
    finally:
        # Cleanup
        print("\n6. Cleaning up...")
        if reader:
            reader.stop()
            print("   ✓ LakeShore reader stopped and cleaned up")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def test_raw_data_processing():
    """
    Test the raw data processing functionality with sample data.
    """
    print("\n" + "=" * 60)
    print("RAW DATA PROCESSING TEST")
    print("=" * 60)
    
    reader = LakeShoreReader()
    
    # Test with sample raw data (simulating what might come from the device)
    test_cases = [
        b'\xab\xb0\xb9\xb9\xae\xb9\xb9\r\n',  # Sample data from your test
        b'123.456,789.012,345.678,901.234\r\n',  # CSV format
        b'SRDG?\r\n',  # Command format
        b'\x00\x01\x02\x03\x04\x05\x06\x07',  # Binary data
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        print(f"Input: {test_data}")
        print(f"Input (hex): {test_data.hex()}")
        
        try:
            result = reader._clean_and_convert_data(test_data)
            print(f"Output: {result}")
            print(f"Output type: {type(result)}")
            print(f"Output length: {len(result)}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function to run the tests."""
    # Parse command line arguments
    port = "COM4"  # Default port
    duration = 10  # Default duration in seconds
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            duration = int(sys.argv[2])
        except ValueError:
            print("Error: Duration must be an integer")
            sys.exit(1)
    
    print("LakeShore Reader Comprehensive Test")
    print("This script will test the LakeShore reader and show both raw and formatted data.")
    print("Press Ctrl+C to stop early.")
    print()
    
    # Run the main test
    success = test_lakeshore_reader(port, duration)
    
    # Run raw data processing test
    test_raw_data_processing()
    
    if success:
        print("\n✓ All tests completed successfully!")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 