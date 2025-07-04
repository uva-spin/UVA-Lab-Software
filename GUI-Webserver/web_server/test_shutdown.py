#!/usr/bin/env python3
"""
Test script for the shutdown functionality
"""

import requests
import time
import sys

def test_shutdown_endpoint():
    """Test the shutdown endpoint"""
    try:
        print("🧪 Testing shutdown endpoint...")
        
        # First, test if server is running
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code != 200:
                print("❌ Server is not responding to health check")
                return False
        except requests.exceptions.RequestException:
            print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
            return False
        
        print("✅ Server is running and responding")
        
        # Test shutdown endpoint
        print("🛑 Sending shutdown request...")
        response = requests.post("http://localhost:5000/shutdown", timeout=10)
        
        if response.status_code == 200:
            print("✅ Shutdown request successful")
            print(f"Response: {response.json()}")
            
            # Wait a moment and check if server is actually shutting down
            time.sleep(2)
            try:
                requests.get("http://localhost:5000/health", timeout=2)
                print("⚠️  Server is still responding after shutdown request")
            except requests.exceptions.RequestException:
                print("✅ Server has successfully shut down")
                return True
        else:
            print(f"❌ Shutdown request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing shutdown: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("🛑 Data Collector Shutdown Test")
    print("=" * 50)
    
    if test_shutdown_endpoint():
        print("\n✅ All tests passed!")
        print("The shutdown functionality is working correctly.")
    else:
        print("\n❌ Tests failed!")
        print("Please check the server configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 