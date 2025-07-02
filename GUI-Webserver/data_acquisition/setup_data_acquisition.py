#!/usr/bin/env python3
"""
Setup script for data acquisition machine
This script helps configure and run the data acquisition system.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['pyModbusTCP', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✓ All packages installed successfully")
        except subprocess.CalledProcessError:
            print("✗ Failed to install packages. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def configure_remote_server():
    """Configure the remote server URL"""
    print("\n=== Remote Server Configuration ===")
    print("Enter the IP address and port of your Flask server:")
    
    current_url = "http://172.29.36.50:5000/data"
    print(f"Current URL: {current_url}")
    
    new_ip = input("Enter IP address (or press Enter to keep current): ").strip()
    if not new_ip:
        new_ip = "172.29.36.50"
    
    new_port = input("Enter port (or press Enter to keep current): ").strip()
    if not new_port:
        new_port = "5000"
    
    new_url = f"http://{new_ip}:{new_port}/data"
    
    # Update config.py
    config_content = f'''# Configuration file for data acquisition system

# Remote Flask server configuration
REMOTE_SERVER_URL = "{new_url}"  # Change this to your Flask server's IP and port

# Local data storage
LOCAL_CSV_DIR = "data_logs"  # Directory to store local CSV backups

# Data acquisition settings
SLEEP_INTERVAL = 5  # Seconds between data readings
MAX_CONSECUTIVE_FAILURES = 10  # Stop after this many consecutive failures

# Modbus settings
PLC_IP = "192.168.0.1"
UNIT_ID = 2
INT_PORT = 503
FLOAT_PORT = 502
NUM_REG_TO_READ = 49

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data_acquisition.log"
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print(f"✓ Configuration updated: {new_url}")
    return new_url

def test_network_connectivity(server_url):
    """Test connectivity to the remote server"""
    print(f"\n=== Testing Network Connectivity ===")
    print(f"Testing connection to: {server_url}")
    
    try:
        import requests
        response = requests.get(server_url.replace('/data', '/health'), timeout=5)
        if response.status_code == 200 or response.status_code == 201:
            print("✓ Successfully connected to remote server")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to remote server: {e}")
        print("Make sure the Flask server is running on the remote machine")
        return False

def create_data_directory():
    """Create the data directory"""
    data_dir = Path("data_logs")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Data directory created: {data_dir.absolute()}")

def main():
    """Main setup function"""
    print("Data Acquisition Setup")
    print("=" * 40)
    print("This script will help you set up the data acquisition system")
    print("on the machine connected to your Modbus devices.")
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("Setup failed. Please install missing dependencies.")
        return
    
    # Configure remote server
    server_url = configure_remote_server()
    
    # Test connectivity
    if not test_network_connectivity(server_url):
        print("\n⚠️  Warning: Cannot connect to remote server.")
        print("You can still run the data acquisition, but data will only be saved locally.")
        response = input("Continue with setup? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Create data directory
    create_data_directory()
    
    print("\n" + "=" * 40)
    print("Setup Complete!")
    print("=" * 40)
    print("To start data acquisition, run:")
    print("python standalone_data_acquisition.py")
    print()
    print("The script will:")
    print("- Read data from Modbus devices")
    print("- Send data to the remote Flask server")
    print("- Save data locally as backup")
    print("- Log all activities to data_acquisition.log")
    print()
    print("Press Ctrl+C to stop the data acquisition.")

if __name__ == '__main__':
    main() 