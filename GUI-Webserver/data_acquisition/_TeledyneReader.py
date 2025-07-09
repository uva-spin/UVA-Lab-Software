import os
import queue
import threading
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

class TeledyneDataReader:
    """Thread-safe class to read teledyne flow data in real-time"""
    
    def __init__(self, csv_path, check_interval=1):
        self.csv_path = csv_path
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None
        
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
            data1 = self.data_queue.get_nowait()
            data2 = self.data_queue.get_nowait()
            data3 = self.data_queue.get_nowait()
            return [data1, data2, data3]
        except queue.Empty:
            # Return the last known data or None values if no data yet
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
                                    # Clear queue before putting new data
                                    while not self.data_queue.empty():
                                        try:
                                            self.data_queue.get_nowait()
                                        except queue.Empty:
                                            break
                                            
                                    self.data_queue.put(flow_values[0])
                                    self.data_queue.put(flow_values[1])
                                    self.data_queue.put(flow_values[2])
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