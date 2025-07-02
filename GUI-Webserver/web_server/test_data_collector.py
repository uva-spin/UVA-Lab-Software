#!/usr/bin/env python3
"""
Test script for the data collector endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
DATA_COLLECTOR_URL = "http://172.29.36.50:5000"
TEST_DATA = [
    10.5, 20.3, 15.7, 25.1, 30.2,  # FC501_ai, FC501_out, FC502_ai, FC502_out, LIT501_ai
    40.1, 50.8, 60.3, 70.9, 80.4,  # PT501_ai, PT502_ai, PT503_ai, PT504_ai, purity_downstream
    90.2, 100.1, 110.5, 120.8, 130.3,  # purity_upstream, AIT501_ai, TI501_ai, TI502_ai, TI503_ai
    140.7, 150.2, 160.9  # TI504_ai, TI505_ai, TI523_ai
]

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{DATA_COLLECTOR_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
            return True
        else:
            print(f"✗ Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
        return False

def test_hmi_data_endpoint():
    """Test the HMI data endpoint"""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f"{DATA_COLLECTOR_URL}/receive_hmi_data",
            data=json.dumps(TEST_DATA),
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✓ HMI data endpoint working")
            return True
        else:
            print(f"✗ HMI data endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ HMI data endpoint failed: {e}")
        return False

def test_data_endpoint():
    """Test the general data endpoint"""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f"{DATA_COLLECTOR_URL}/data",
            data=json.dumps(TEST_DATA),
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✓ Data endpoint working")
            return True
        else:
            print(f"✗ Data endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Data endpoint failed: {e}")
        return False

def test_query_endpoint():
    """Test the database query endpoint"""
    try:
        # Query for recent HMI data
        params = {
            'keys': 'fc501_ai,fc501_out,fc502_ai,ti501_ai,ti502_ai',
            'start_time': '2024-01-01 00:00:00',
            'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = requests.get(f"{DATA_COLLECTOR_URL}/query_db", params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Query endpoint working - returned {len(data.get('data', []))} records")
            return True
        else:
            print(f"✗ Query endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Query endpoint failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Data Collector Endpoints...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("HMI Data Endpoint", test_hmi_data_endpoint),
        ("Data Endpoint", test_data_endpoint),
        ("Query Endpoint", test_query_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Data collector is working correctly.")
    else:
        print("✗ Some tests failed. Please check the data collector setup.")

if __name__ == "__main__":
    main() 