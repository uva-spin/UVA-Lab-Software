import os
import queue
import threading
import time
import logging

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
        """Get the latest teledyne data from the queue"""
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None
            
    def _monitor_file(self):
        """Monitor the CSV file for new data"""
        while self.running:
            try:
                print(f"Checking if file exists: {self.csv_path}")
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
                                if line:
                                    try:
                                        # Parse CSV line
                                        data = line.split(',')
                                        if len(data) >= 4:  # timestamp + 3 flow values
                                            teledyne_data = {
                                                'timestamp': data[0],
                                                'flow_1': float(data[1]),
                                                'flow_2': float(data[2]),
                                                'flow_3': float(data[3])
                                            }
                                            self.data_queue.put(teledyne_data)
                                            logger.debug(f"New teledyne data: {teledyne_data}")
                                    except (ValueError, IndexError) as e:
                                        logger.warning(f"Error parsing teledyne data line: {line}, error: {e}")
                else:
                    logger.warning(f"Teledyne CSV file not found: {self.csv_path}. Creating file...")
                    with open(self.csv_path, 'w') as file:
                        file.write("Timestamp,Flow_1,Flow_2,Flow_3\n")
                    self.last_position = 0
                    continue
                    
            except Exception as e:
                logger.error(f"Error monitoring teledyne file: {e}")
                
            time.sleep(self.check_interval)