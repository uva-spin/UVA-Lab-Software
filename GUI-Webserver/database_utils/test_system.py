#!/usr/bin/env python3
"""
Test script to verify the data collection system is working.
"""

import requests
import json
import time
import sqlite3
from datetime import datetime

def test_data_collector_endpoint():
    """Test if the data collector is running and responding"""
    try:
        response = requests.get("http://172.29.36.50/health", timeout=5)
        if response.status_code == 200:
            print("✓ Data collector is running")
            return True
        else:
            print(f"✗ Data collector returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to data collector: {e}")
        return False

def test_hmi_data_endpoint():
    """Test sending HMI data to the collector"""
    # Sample HMI data (18 values as expected)
    sample_data = [100.0, 50.0, 200.0, 75.0, 25.0, 300.0, 400.0, 500.0, 600.0, 
                   95.5, 98.2, 150.0, 75.5, 80.2, 85.1, 90.3, 95.7, 88.9]
    
    try:
        response = requests.post(
            "http://172.29.36.50/data",
            json=sample_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✓ HMI data endpoint is working")
            return True
        else:
            print(f"✗ HMI data endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot send HMI data: {e}")
        return False

def test_database_connection():
    """Test if the database exists and is accessible"""
    try:
        conn = sqlite3.connect("../instance/flaskr.sqlite")
        cursor = conn.cursor()
        
        # Check if merged_data table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='merged_data'
        """)
        
        if cursor.fetchone():
            print("✓ Database and merged_data table exist")
            
            # Check record count
            cursor.execute("SELECT COUNT(*) FROM merged_data")
            count = cursor.fetchone()[0]
            print(f"✓ Database contains {count} records")
            
            conn.close()
            return True
        else:
            print("✗ merged_data table does not exist")
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_csv_files():
    """Test if CSV files exist"""
    csv_files = [
        "static/csv/Test_data.csv",
        "static/csv/r_values.csv", 
        "static/csv/hmi_data.csv"
    ]
    
    all_exist = True
    for file_path in csv_files:
        try:
            with open(file_path, 'r') as f:
                print(f"✓ {file_path} exists")
        except FileNotFoundError:
            print(f"✗ {file_path} not found")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("Testing Data Collection System...")
    print("=" * 40)
    
    tests = [
        ("Data Collector Endpoint", test_data_collector_endpoint),
        ("HMI Data Endpoint", test_hmi_data_endpoint),
        ("Database Connection", test_database_connection),
        ("CSV Files", test_csv_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the setup.")

if __name__ == '__main__':
    main() 