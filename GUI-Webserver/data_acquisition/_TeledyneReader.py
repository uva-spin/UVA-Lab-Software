import os
import threading
import time
import logging
import numpy as np
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import socket
import re

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class TeledyneDataReader:    
    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        self.data_queue = [None, None, None]
        self.running = False    
        self.thread = None
        self.TELEDYNE_THCD_401_TCP_PORT = 101
        self.TELEDYNE_THCD_401_TCP_IP = "172.29.36.192"
        self.TELEDYNE_THCD_401_TCP_UNIT_ID = 2
        self.socket = None
        self.connection_lock = threading.Lock()


    def _ensure_connection(self):
        """Ensure we have a valid TCP connection, reconnect if needed"""
        with self.connection_lock:
            try:
                if self.socket is None:
                    logger.info("Creating new TCP connection to Teledyne device")
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.settimeout(5)
                    self.socket.connect((self.TELEDYNE_THCD_401_TCP_IP, self.TELEDYNE_THCD_401_TCP_PORT))
                    logger.info("Successfully connected to Teledyne device")
                return True
            except Exception as e:
                logger.error(f"Error establishing TCP connection: {e}")
                self._close_connection()
                return False

    def _close_connection(self):
        """Close the TCP connection safely"""
        try:
            if self.socket:
                self.socket.close()
                logger.info("Closed TCP connection to Teledyne device")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")
        finally:
            self.socket = None

    def _read_data_persistent(self):
        """Read data from Teledyne device using persistent TCP connection"""
        try:
            if not self._ensure_connection():
                return [None, None, None]

            # Keep the socket open and wait for data
            # Set a longer timeout to wait for data
            self.socket.settimeout(10)
            
            # Try to read data from the persistent connection
            data = self.socket.recv(1024)
            
            if not data:
                logger.warning("No data received from device, connection may be idle")
                # Don't close connection, just return None values
                return [None, None, None]

            ascii_data = data.decode('ascii', errors='ignore')
            logger.debug(f"Received ASCII data: {ascii_data}")

            match = re.search(r'READ:([^\r\n]*)', ascii_data)
            if not match:
                logger.warning("No 'READ:' found in received data")
                return [None, None, None]

            read_section = match.group(1)
            # Split by comma and take the first 3 values
            values = read_section.split(',')[:3]
            logger.debug(f"First 3 values after READ:: {values}")

            # Convert to float, handling non-numeric values like !RANGE!
            floats = []
            for val in values:
                val = val.strip()
                try:
                    # Try to convert to float
                    floats.append(float(val))
                except (ValueError, TypeError):
                    # If conversion fails (like !RANGE!), set to None
                    logger.debug(f"Could not convert '{val}' to float, setting to None")
                    floats.append(None)
            
            while len(floats) < 3:
                floats.append(None)

            logger.info(f"Successfully parsed values: {floats}")
            return floats

        except socket.timeout:
            logger.debug("Socket timeout - no data available yet, keeping connection open")
            # Don't close connection on timeout, just return None values
            return [None, None, None]
        except Exception as e:
            logger.error(f"Error reading data from persistent connection: {e}")
            self._close_connection()
            return [None, None, None]

    def _send_command(self, command):
        """Send a command to the Teledyne device"""
        try:
            if not self._ensure_connection():
                return False
            
            # Send command with proper termination
            command_bytes = (command + '\r\n').encode('ascii')
            self.socket.send(command_bytes)
            logger.debug(f"Sent command: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")
            self._close_connection()
            return False

    def _request_data(self):
        """Request data from the Teledyne device"""
        # Try common commands that might trigger data output
        commands = ['READ', 'DATA', 'MEASURE', 'STATUS']
        for command in commands:
            if self._send_command(command):
                time.sleep(0.1)  # Small delay to allow device to respond
                # Try to read response
                try:
                    self.socket.settimeout(2)
                    data = self.socket.recv(1024)
                    if data:
                        ascii_data = data.decode('ascii', errors='ignore')
                        logger.debug(f"Response to {command}: {ascii_data}")
                        return ascii_data
                except socket.timeout:
                    logger.debug(f"No response to {command} command")
                    continue
                except Exception as e:
                    logger.error(f"Error reading response to {command}: {e}")
                    continue
        return None
        
    def _tcp_connection(self):
        """Legacy method - now uses persistent connection"""
        return self._read_data_persistent()
        
    def _socket_connection(self):
        """Connect to the Teledyne THCD-401 socket"""
        return self._ensure_connection()
        
    def _socket_read(self):
        """Read data from the Teledyne THCD-401 socket"""
        return self._read_data_persistent()
        
    def start(self):
        """Start the teledyne data reading thread"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_tcp, daemon=True)
        self.thread.start()
        logger.info("Started teledyne data monitoring via TCP")
        
    def stop(self):
        """Stop the teledyne data reading thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self._close_connection()
        logger.info("Stopped teledyne data monitoring")
            
    def get_latest_data(self):
        """Get the latest teledyne data from TCP connection"""
        try:
            # First try to read any available data
            values = self._read_data_persistent()
            
            # If no data available, try requesting it
            if not values or all(v is None for v in values):
                logger.debug("No data available, trying to request data from device")
                response = self._request_data()
                if response:
                    # Parse the response
                    match = re.search(r'READ:([^\r\n]*)', response)
                    if match:
                        read_section = match.group(1)
                        values = read_section.split(',')[:3]
                        floats = []
                        for val in values:
                            val = val.strip()
                            try:
                                floats.append(float(val))
                            except (ValueError, TypeError):
                                floats.append(None)
                        while len(floats) < 3:
                            floats.append(None)
                        values = floats
            
            if values and not all(v is None for v in values):
                self.data_queue = values
                logger.debug(f"Updated teledyne data queue: {self.data_queue}")
            return self.data_queue
        except Exception as e:
            logger.error(f"Error getting latest teledyne data: {e}")
            return [None] * 3
            
    def _monitor_tcp(self):
        """Monitor the TCP connection for new data"""
        
        while self.running:
            try:
                # Use the same logic as get_latest_data
                values = self._read_data_persistent()
                
                # If no data available, try requesting it
                if not values or all(v is None for v in values):
                    logger.debug("No data available in monitor, trying to request data from device")
                    response = self._request_data()
                    if response:
                        # Parse the response
                        match = re.search(r'READ:([^\r\n]*)', response)
                        if match:
                            read_section = match.group(1)
                            values = read_section.split(',')[:3]
                            floats = []
                            for val in values:
                                val = val.strip()
                                try:
                                    floats.append(float(val))
                                except (ValueError, TypeError):
                                    floats.append(None)
                            while len(floats) < 3:
                                floats.append(None)
                            values = floats
                
                if values and not all(v is None for v in values):
                    self.data_queue = values
                    logger.debug(f"Updated teledyne data queue: {self.data_queue}")
                else:
                    logger.debug("No valid data received from TCP connection")
                    
            except Exception as e:
                logger.error(f"Error monitoring teledyne TCP: {e}")
                
            time.sleep(self.check_interval)


    