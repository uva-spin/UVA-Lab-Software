#!/usr/bin/env python3
"""
Startup script for running the entire data collection system locally.
This script starts both the data collector and the HMI TCP server.
"""

import subprocess
import sys
import time
import threading
import signal
import os
from pathlib import Path

# Global variables to track processes
data_collector_process = None
hmi_server_process = None
running = True

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global running
    print("\nShutting down...")
    running = False
    
    if data_collector_process:
        data_collector_process.terminate()
    if hmi_server_process:
        hmi_server_process.terminate()

def start_data_collector():
    """Start the data collector"""
    global data_collector_process
    print("Starting data collector...")
    
    try:
        data_collector_process = subprocess.Popen([
            sys.executable, "web_server/start_data_collector.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"Data collector started with PID: {data_collector_process.pid}")
        return True
    except Exception as e:
        print(f"Failed to start data collector: {e}")
        return False

def start_hmi_server():
    """Start the HMI TCP server"""
    global hmi_server_process
    print("Starting HMI TCP server...")
    
    try:
        hmi_server_process = subprocess.Popen([
            sys.executable, "utils/HMI_TCP_Sserver.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"HMI TCP server started with PID: {hmi_server_process.pid}")
        return True
    except Exception as e:
        print(f"Failed to start HMI TCP server: {e}")
        return False

def monitor_processes():
    """Monitor running processes"""
    while running:
        time.sleep(5)
        
        # Check data collector
        if data_collector_process and data_collector_process.poll() is not None:
            print("Data collector stopped unexpectedly")
            break
            
        # Check HMI server
        if hmi_server_process and hmi_server_process.poll() is not None:
            print("HMI TCP server stopped unexpectedly")
            break

def main():
    """Main startup function"""
    print("UVA Lab Software - Local Data Collection System")
    print("=" * 50)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if we're in the right directory
    if not Path("web_server").exists() or not Path("utils").exists():
        print("Error: Please run this script from the GUI-Webserver directory")
        sys.exit(1)
    
    # Start data collector
    if not start_data_collector():
        print("Failed to start data collector. Exiting.")
        sys.exit(1)
    
    # Wait a moment for data collector to start
    time.sleep(3)
    
    # Start HMI server
    if not start_hmi_server():
        print("Failed to start HMI TCP server. Exiting.")
        if data_collector_process:
            data_collector_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("System is running!")
    print("Data collector: http://localhost:5000")
    print("Press Ctrl+C to stop all services")
    print("=" * 50)
    
    # Monitor processes
    try:
        monitor_processes()
    except KeyboardInterrupt:
        pass
    
    # Cleanup
    print("\nStopping services...")
    if data_collector_process:
        data_collector_process.terminate()
        data_collector_process.wait()
    if hmi_server_process:
        hmi_server_process.terminate()
        hmi_server_process.wait()
    
    print("All services stopped.")

if __name__ == '__main__':
    main() 