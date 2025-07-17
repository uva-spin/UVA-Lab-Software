#!/usr/bin/env python3
"""
LakeShore Reader Test Script

This script tests the LakeShore reader functionality with comprehensive output
and proper error handling.
"""

import time
import logging
from datetime import datetime
from _LakeShoreReader import LakeShoreReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_lakeshore_connection():
    """Test basic LakeShore connection and data reading."""
    
    print("=" * 60)
    print("LAKESHORE READER TEST")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create reader instance (adjust port as needed for your system)
    reader = LakeShoreReader(port="COM4", baudrate=9600, timeout=2)
    
    try:
        # Start the connection
        print("\n1. Starting LakeShore connection...")
        if reader.start():
            print("   ✓ Connection started successfully")
            print(f"   Connection status: {reader.is_connected()}")
        else:
            print("   ✗ Failed to start connection")
            return False
        
        # Start data streaming
        print("\n2. Starting data stream...")
        if reader.data_stream():
            print("   ✓ Data stream started successfully")
        else:
            print("   ✗ Failed to start data stream")
            return False
        
        # Collect data for 10 seconds
        print("\n3. Collecting data for 10 seconds...")
        print("-" * 60)
        print("DATA COLLECTION:")
        print("-" * 60)
        
        start_time = time.time()
        data_points = 0
        
        while time.time() - start_time < 10:
            try:
                # Get the latest data
                raw_data = reader.get_latest_data()
                formatted_data = reader.get_formatted_data()
                
                # Display timestamp
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                # Display raw data
                print(f"[{timestamp}] Raw data: {raw_data}")
                
                # Display formatted data
                if formatted_data:
                    print(f"[{timestamp}] Formatted data:")
                    for channel, value in formatted_data.items():
                        print(f"           {channel}: {value:.3f}")
                else:
                    print(f"[{timestamp}] No formatted data available")
                
                print("-" * 40)
                
                data_points += 1
                time.sleep(1)  # Collect data every second
                
            except KeyboardInterrupt:
                print("\n   Interrupted by user")
                break
            except Exception as e:
                print(f"   Error collecting data: {e}")
                break
        
        print("-" * 60)
        print(f"Data collection completed!")
        print(f"Total data points collected: {data_points}")
        print(f"Average collection rate: {data_points/10:.1f} points/second")
        
        # Show final status
        print("\n4. Final status:")
        print(f"   Connection status: {reader.is_connected()}")
        print(f"   Thread alive: {reader.thread.is_alive() if reader.thread else False}")
        print(f"   Latest data: {reader.get_latest_data()}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        return False
        
    finally:
        # Cleanup
        print("\n5. Cleaning up...")
        reader.stop()
        print("   ✓ LakeShore reader stopped and cleaned up")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def test_data_parsing():
    """Test the data parsing functionality with sample data."""
    
    print("\n" + "=" * 60)
    print("DATA PARSING TEST")
    print("=" * 60)
    
    reader = LakeShoreReader()
    
    # Test cases with different data formats
    test_cases = [
        b'123.456,234.567,345.678,456.789,567.890,678.901,789.012,890.123\r\n',
        b'100.0,200.0,300.0,400.0,500.0,600.0,700.0,800.0\r\n',
        b'0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0\r\n',
        b'123.456\r\n',  # Incomplete data
        b'\r\n',  # Empty data
        b'invalid,data,here\r\n',  # Invalid data
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        print(f"Input: {test_data}")
        print(f"Input (hex): {test_data.hex()}")
        
        try:
            result = reader._parse_lakeshore_data(test_data)
            print(f"Output: {result}")
            print(f"Output type: {type(result)}")
            print(f"Output length: {len(result)}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function to run the tests."""
    
    print("LakeShore Reader Test")
    print("This script will test the LakeShore reader and show both raw and formatted data.")
    print("Press Ctrl+C to stop early.")
    print()
    
    # Run the main connection test
    success = test_lakeshore_connection()
    
    # Run data parsing test
    test_data_parsing()
    
    if success:
        print("\n✓ All tests completed successfully!")
    else:
        print("\n✗ Some tests failed!")

if __name__ == "__main__":
    main()


