#!/usr/bin/env python3
"""
Test script for MaxiGauge TCP connection
"""

import time
import logging
from _MaxiGaugeReader import MaxiGaugeReader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_maxigauge_connection():
    """Test the MaxiGauge TCP connection"""
    print("Testing MaxiGauge TCP connection...")
    
    # Create MaxiGauge reader instance
    reader = MaxiGaugeReader(timeout=2, check_interval=1)
    
    try:
        # Test connection
        print(f"Attempting to connect to {reader.MAXIGAUGE_TCP_IP}:{reader.MAXIGAUGE_TCP_PORT}")
        
        # Try to establish connection
        if reader._socket_connection():
            print("✓ Connection established successfully!")
            
            # Try to read data
            print("Attempting to read data...")
            data = reader._socket_read()
            
            if data:
                print(f"✓ Data received: {data}")
            else:
                print("⚠ No data received (this might be normal if device is not sending data)")
                
        else:
            print("✗ Failed to establish connection")
            return False
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        return False
    finally:
        # Clean up
        reader.stop()
        
    return True

def test_continuous_monitoring():
    """Test continuous monitoring for a short period"""
    print("\nTesting continuous monitoring for 10 seconds...")
    
    reader = MaxiGaugeReader(timeout=2, check_interval=1)
    
    try:
        reader.start()
        
        # Monitor for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            data = reader.get_latest_data()
            if data:
                print(f"Data: {data}")
            else:
                print("No data available")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        reader.stop()
        print("Test completed")

if __name__ == "__main__":
    print("MaxiGauge TCP Connection Test")
    print("=" * 40)
    
    # Test basic connection
    if test_maxigauge_connection():
        print("\nBasic connection test passed!")
        
        # Ask if user wants to test continuous monitoring
        response = input("\nDo you want to test continuous monitoring? (y/n): ")
        if response.lower() in ['y', 'yes']:
            test_continuous_monitoring()
    else:
        print("\nBasic connection test failed!")
        print("\nTroubleshooting tips:")
        print("1. Check if the MaxiGauge device is powered on")
        print("2. Verify the IP address and port are correct")
        print("3. Check network connectivity to the device")
        print("4. Ensure no firewall is blocking the connection")
        print("5. Check if the device is configured for TCP communication") 