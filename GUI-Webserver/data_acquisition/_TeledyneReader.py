import os
import threading
import time
import logging
import numpy as np
from pyModbusTCP.client import ModbusClient


logger = logging.getLogger(__name__)


class TeledyneDataReader:
    """Thread-safe class to read teledyne flow data in real-time"""
    
    def __init__(self, csv_path, check_interval=1):
        self.csv_path = csv_path
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = [None, None, None]
        self.running = False    
        self.thread = None
        self.TELEDYNE_THCD_401_TCP_PORT = 101
        self.TELEDYNE_THCD_401_TCP_IP = "192.168.1.180"
        self.TELEDYNE_THCD_401_TCP_UNIT_ID = 1


    def _read_integer_registers(self):
        """Read integer registers from Modbus TCP server"""
        try:
            client = ModbusClient(host=self.TELEDYNE_THCD_401_TCP_IP, port=self.TELEDYNE_THCD_401_TCP_PORT, unit_id=1)
            int_regs = client.read_holding_registers(0, 3)
            if int_regs:
                int_values = self._get_list_2comp(int_regs, 16)
                logger.info(f'Successfully read integer values: {int_values[:3]}... ({len(int_values)} values)')
                return int_values
            else:
                logger.warning(f"Failed to read integer registers from {self.TELEDYNE_THCD_401_TCP_IP}:{self.TELEDYNE_THCD_401_TCP_PORT}")
                return None
        except Exception as e:
            logger.error(f"Error reading integer registers from Teledyne THCD-401: {e}")
            return None
        
    def _read_float_registers(self):
        """Read float registers from Modbus TCP server"""
        try:
            client = ModbusClient(host=self.TELEDYNE_THCD_401_TCP_IP, port=self.TELEDYNE_THCD_401_TCP_PORT, unit_id=1)
            float_regs = client.read_holding_registers(3, 3)
            if float_regs:
                float_values = self._get_list_2comp(float_regs, 16)
                logger.info(f'Successfully read float values: {float_values[:3]}... ({len(float_values)} values)')
                return float_values
            else:
                logger.warning(f"Failed to read float registers from {self.TELEDYNE_THCD_401_TCP_IP}:{self.TELEDYNE_THCD_401_TCP_PORT}")
                return None
        except Exception as e:
            logger.error(f"Error reading float registers from Teledyne THCD-401: {e}")
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
        self.thread = threading.Thread(target=self._monitor_file, daemon=True)
        self.thread.start()
        logger.info(f"Started teledyne data monitoring for {self.csv_path}")
        
    def stop(self):
        """Stop the teledyne data reading thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def get_latest_data(self):
        """Get the latest teledyne data"""
        try:
            # Try to get latest data from queue
            print(f"DEBUG: Teledyne data queue: {self.data_queue[0]}, {self.data_queue[1]}, {self.data_queue[2]}")
            return [self.data_queue[0], self.data_queue[1], self.data_queue[2]]
        except Exception as e:
            # Return the last known data or None values if no data yet
            logger.error(f"Error getting latest teledyne data: {e}")
            return [None] * 3
            
    def _monitor_file(self):
        """Monitor the CSV file for new data"""
        header_skipped = False  # Flag to track if we've skipped the header
        
        while self.running:
            try:
                if os.path.exists(self.csv_path):
                    with open(self.csv_path, 'r') as file:
                        # Move to the last known position
                        file.seek(self.last_position)
                        
                        # Read new lines
                        new_lines = file.readlines()
                        
                        if new_lines:
                            # Update position for next read
                            self.last_position = file.tell()
                            
                            # Process new lines
                            for line in new_lines:
                                line = line.strip()
                                if not line:
                                    continue
                                    
                                # Skip header line
                                if not header_skipped:
                                    if line.lower().startswith('timestamp') or ',' in line and any(x.lower() in line.lower() for x in ['flow', 'time']):
                                        header_skipped = True
                                        continue
                                
                                try:
                                    data = line.split(',')
                                    timestamp = data[0].strip()
                                    flow_values = []
                                    
                                    # Parse flow values, replacing empty or invalid values with None
                                    for val in data[1:3]:
                                        try:
                                            flow_values.append(float(val.strip()))
                                        except (ValueError, TypeError):
                                            flow_values.append(None)

                                    # Check if flow values are all None
                                    if all(val is None for val in flow_values):
                                        logger.warning("All flow values are None. Returning None values...")
                                        return [None] * 3
                                    
                                    # Put data in queue, replacing old data if queue is full                                    
                                            
                                    self.data_queue[0] = flow_values[0] ### Seperator Flow 
                                    self.data_queue[1] = flow_values[1] ### Magnet Flow 
                                    self.data_queue[2] = flow_values[2] ### Main Flow 
                                    logger.debug(f"New teledyne data: {timestamp}, {flow_values[0]}, {flow_values[1]}, {flow_values[2]}")
                                    
                                except (ValueError, IndexError) as e:
                                    logger.warning(f"Error parsing teledyne data line: {line}, error: {e}")
                                    continue  # Skip this line and continue with the next

                else:
                    logger.warning(f"Teledyne CSV file not found: {self.csv_path}. Creating file...")
                    with open(self.csv_path, 'w') as file:
                        file.write("Timestamp,Flow_1,Flow_2,Flow_3\n")
                    self.last_position = 0
                    header_skipped = True  # We just wrote the header
                    continue
                    
            except Exception as e:
                logger.error(f"Error monitoring teledyne file: {e}")
                
            time.sleep(self.check_interval)


    