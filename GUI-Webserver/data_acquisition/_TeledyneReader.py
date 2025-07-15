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

            ascii_data = data.decode('ascii', errors='ignore')
            logger.debug(f"Received ASCII data: {ascii_data}")

            # Find the READ: section
            match = re.search(r'READ:([^\r\n]*)', ascii_data)
            if not match:
                logger.warning("No 'READ:' found in received data")
                return [None, None, None]

            read_section = match.group(1)
            # Find all numbers (float or int, including negative and scientific notation)
            numbers = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', read_section)
            logger.debug(f"Extracted numbers: {numbers}")

            # Take the first three numbers, convert to float, fill with None if less than 3
            floats = []
            for n in numbers[:3]:
                try:
                    floats.append(float(n))
                except Exception:
                    floats.append(None)
            while len(floats) < 3:
                floats.append(None)

            logger.info(f"Successfully parsed values: {floats}")
            return floats

        except Exception as e:
            logger.error(f"Error in TCP connection: {e}")
            return [None, None, None]
        
    def _socket_connection(self):
        """Connect to the Teledyne THCD-401 socket"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.TELEDYNE_THCD_401_TCP_IP, self.TELEDYNE_THCD_401_TCP_PORT))
        except Exception as e:
            logger.error(f"Error connecting to Teledyne THCD-401: {e}")
            return None
        
    def _socket_read(self):
        """Read data from the Teledyne THCD-401 socket"""
        try:
            data = self.socket.recv(1024)
            return data
        except Exception as e:
            logger.error(f"Error reading data from Teledyne THCD-401: {e}")
            return None
        
    def _get_list_2comp(self, regs, bits=16):
        """Convert list of integer values to 2's complement"""
        converted = []
        max_value = 2 ** bits
        for reg in regs:
            if reg >= max_value:
                reg = reg - (2 ** bits)
            converted.append(reg)
        return converted
        
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
            
    def get_latest_data(self):
        """Get the latest teledyne data from TCP connection"""
        try:
            # Read directly from TCP connection
            values = self._tcp_connection()
            if values:
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
                # Read data from TCP connection
                values = self._tcp_connection()
                if values:
                    self.data_queue = values
                    logger.debug(f"Updated teledyne data queue: {self.data_queue}")
                else:
                    logger.warning("Failed to read data from TCP connection")
                    
            except Exception as e:
                logger.error(f"Error monitoring teledyne TCP: {e}")
                
            time.sleep(self.check_interval)


    