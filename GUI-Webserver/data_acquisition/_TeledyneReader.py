import os
import threading
import time
import logging
import numpy as np
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import socket
import re
import errno

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

    def _decode_data(self, data, context=""):
        """Decode data from various formats to ASCII"""
        if not data:
            return None
            
        logger.debug(f"Raw data {context}: {data}")
        logger.debug(f"Raw data as hex {context}: {data.hex()}")
        
        # Try different decoding approaches
        ascii_data = None
        
        # Method 1: Direct ASCII decode
        try:
            ascii_data = data.decode('ascii', errors='ignore')
            logger.debug(f"Direct ASCII decode {context}: {ascii_data}")
        except Exception as e:
            logger.warning(f"Direct ASCII decode failed {context}: {e}")
        
        # Method 2: If direct decode doesn't work, try treating as hex string
        if not ascii_data or not ascii_data.strip():
            try:
                # Check if data looks like hex string
                hex_string = data.hex()
                # Try to decode as if it's a hex representation of ASCII
                ascii_data = bytes.fromhex(hex_string).decode('ascii', errors='ignore')
                logger.debug(f"Hex to ASCII decode {context}: {ascii_data}")
            except Exception as e:
                logger.warning(f"Hex to ASCII decode failed {context}: {e}")
                # Fallback to original data
                try:
                    ascii_data = data.decode('ascii', errors='ignore')
                except:
                    ascii_data = None
        
        if not ascii_data:
            logger.error(f"Failed to decode data in any format {context}")
            return None
            
        return ascii_data


        
    def _tcp_connection(self):
        """Read data from Teledyne device using raw TCP socket and extract first three numbers after READ:"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.TELEDYNE_THCD_401_TCP_IP, self.TELEDYNE_THCD_401_TCP_PORT))

            # Send a command if needed, or just try to read
            sock.send(b"READ\r\n")
            data = sock.recv(1024)
            sock.close()

            if not data:
                logger.warning("No data received from device")
                return [None, None, None]

            # Decode the data using the helper method
            ascii_data = self._decode_data(data, "from TCP connection")
            if not ascii_data:
                return [None, None, None]

            # Find the READ: section
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
            
            # Ensure we always have exactly 3 values
            while len(floats) < 3:
                floats.append(None)

            logger.info(f"Successfully parsed values: {floats}")
            return floats

        except Exception as e:
            logger.error(f"Error in TCP connection: {e}")
            return [None, None, None]
        
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
        logger.info("Stopped teledyne data monitoring")
            
    def get_latest_data(self):
        """Get the latest teledyne data from TCP connection"""
        try:
            # Use the simple TCP connection approach
            values = self._tcp_connection()
            
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
                # Use the simple TCP connection approach
                values = self._tcp_connection()
                
                if values and not all(v is None for v in values):
                    self.data_queue = values
                    logger.debug(f"Updated teledyne data queue: {self.data_queue}")
                else:
                    logger.debug("No valid data received from TCP connection")
                    
            except Exception as e:
                logger.error(f"Error monitoring teledyne TCP: {e}")
                
            time.sleep(self.check_interval)


    