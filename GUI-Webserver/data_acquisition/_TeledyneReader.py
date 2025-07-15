import os
import threading
import time
import logging
import numpy as np
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import socket

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


    def _modbus_connection(self):
        """Read integer registers from Modbus TCP server and convert to ASCII"""

        client = ModbusClient(host=self.TELEDYNE_THCD_401_TCP_IP, port=self.TELEDYNE_THCD_401_TCP_PORT)
        client.connect()                               # connect to device

        int_regs = client.read_holding_registers(0, 1, unit=2)
        logger.debug(f"Modbus connection: {int_regs}")
        client.close()
        
        if not int_regs.isError():
            # Convert hex registers to ASCII/UTF-8 string
            hex_string = ''
            for reg in int_regs.registers:
                # Convert 16-bit register to hex and then to ASCII
                hex_val = format(reg & 0xFFFF, '04x')  # Ensure 4 hex digits
                hex_string += hex_val
            
            # Convert hex string to ASCII/UTF-8
            try:
                ascii_string = bytes.fromhex(hex_string).decode('ascii', errors='ignore')
                logger.debug(f"Converted ASCII string: {ascii_string}")
                
                # Parse the data values after "READ:"
                if "READ:" in ascii_string:
                    read_part = ascii_string.split("READ:")[1]
                    # Split by comma and take first 3 values
                    values = read_part.split(',')[:3]
                    
                    # Convert to float, handling any non-numeric values
                    parsed_values = []
                    for val in values:
                        try:
                            parsed_values.append(float(val.strip()))
                        except (ValueError, TypeError):
                            parsed_values.append(None)
                    
                    logger.info(f'Successfully parsed values: {parsed_values}')
                    return parsed_values
                else:
                    logger.warning("No 'READ:' found in ASCII string")
                    return [None] * 3
                    
            except Exception as e:
                logger.error(f"Error converting hex to ASCII: {e}")
                return [None] * 3
        else:
            logger.warning(f"Failed to read integer registers from {self.TELEDYNE_THCD_401_TCP_IP}:{self.TELEDYNE_THCD_401_TCP_PORT}")
            return [None] * 3
        
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
        self.thread = threading.Thread(target=self._monitor_modbus, daemon=True)
        self.thread.start()
        logger.info("Started teledyne data monitoring via Modbus")
        
    def stop(self):
        """Stop the teledyne data reading thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def get_latest_data(self):
        """Get the latest teledyne data from Modbus connection"""
        try:
            # Read directly from Modbus connection
            values = self._modbus_connection()
            if values:
                self.data_queue = values
                logger.debug(f"Updated teledyne data queue: {self.data_queue}")
            return self.data_queue
        except Exception as e:
            logger.error(f"Error getting latest teledyne data: {e}")
            return [None] * 3
            
    def _monitor_modbus(self):
        """Monitor the Modbus connection for new data"""
        
        while self.running:
            try:
                # Read data from Modbus connection
                values = self._modbus_connection()
                if values:
                    self.data_queue = values
                    logger.debug(f"Updated teledyne data queue: {self.data_queue}")
                else:
                    logger.warning("Failed to read data from Modbus connection")
                    
            except Exception as e:
                logger.error(f"Error monitoring teledyne Modbus: {e}")
                
            time.sleep(self.check_interval)


    