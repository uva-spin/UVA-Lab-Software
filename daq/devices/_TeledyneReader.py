import socket
import time
import logging
import re
import os
import asyncio
import mariadb
from datetime import datetime
import pytz

class TeledyneDataReader:  
    """
    TeledyneDataReader class for reading data from Teledyne THCD-401 flow meter
    """

    logger = logging.getLogger(__name__)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))


    def __init__(self, check_interval=1, connection_pool=None, ip_address="172.29.36.192", tcp_port=101):
        self.check_interval = check_interval
        self.data_queue = [None, None, None]
        self.running = False
        self.TELEDYNE_THCD_401_TCP_PORT = tcp_port
        self.TELEDYNE_THCD_401_TCP_IP = ip_address
        self.TELEDYNE_THCD_401_TCP_UNIT_ID = 2
        self.socket = None
        self.connected = False
        self.timeout = 3
        self.last_connection_attempt = 0
        self.connection_retry_interval = 3  # seconds
        self.read_command = b"ar\r\n"
        self.connection_pool = connection_pool
        self.EST = pytz.timezone('America/New_York')


    def _socket_read(self):
        """Read data from Teledyne device using raw TCP socket and extract first three numbers after READ:"""
        if not self._socket_connection():
            return [None, None, None]

        try:
            # Send a command to request latest values.
            ## a: address
            ## r: read
            ## \r\n: end of command
            self.socket.sendall(self.read_command)
            data = self.socket.recv(1024)

            if not data:
                self.logger.warning("No data received from Teledyne Flow Meter!")
                self._close_socket()
                return [None, None, None]

            ascii_data = data.decode('ascii', errors='ignore')
            self.logger.debug(f"Received ASCII data: {ascii_data}")

            # Find the READ: section
            match = re.search(r'READ:([^\r\n]*)', ascii_data)
            if not match:
                self.logger.warning("No 'READ:' found in received data")
                return [None, None, None]

            read_section = match.group(1)
            # Split by comma and take the first 3 values
            values = read_section.split(',')[:3]
            self.logger.debug(f"First 3 values after READ:: {values}")

            # Convert to float, handling non-numeric values like !RANGE!
            floats = []
            for val in values:
                val = val.strip()
                try:
                    floats.append(float(val))
                except (ValueError, TypeError):
                    # If conversion fails (like !RANGE!), set to None
                    self.logger.debug(f"Could not convert '{val}' to float, setting to None")
                    floats.append(None)
            
            # Ensure we always have exactly 3 values
            while len(floats) < 3:
                floats.append(None)

            self.logger.info(f"Successfully parsed values: {floats}")
            return floats

        except socket.timeout:
            self.logger.warning("Teledyne socket timed out waiting for response")
            return [None, None, None]
        except Exception as e:
            self.logger.error(f"Error in TCP connection: {e}")
            self._close_socket()
            return [None, None, None]
        
    def _socket_connection(self):
        """Connect to the Teledyne THCD-401 socket"""
        if self.connected and self.socket:
            return True

        current_time = time.time()
        if current_time - self.last_connection_attempt < self.connection_retry_interval:
            return False

        self.last_connection_attempt = current_time
        try:
            self._close_socket()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.TELEDYNE_THCD_401_TCP_IP, self.TELEDYNE_THCD_401_TCP_PORT))
            self.connected = True
            self.logger.info(
                f"Connected to Teledyne at {self.TELEDYNE_THCD_401_TCP_IP}:{self.TELEDYNE_THCD_401_TCP_PORT}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to Teledyne THCD-401: {e}")
            self._close_socket()
            return False

    def _close_socket(self):
        """Close and clear the current Teledyne socket."""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
        self.socket = None
        self.connected = False
        
    def start(self):
        """Start the teledyne data reading"""
        self.running = True
        self.logger.info("Started teledyne data monitoring via TCP")
        self._socket_connection()
        return True
        
    def stop(self):
        """Stop the teledyne data reading"""
        self.logger.info("Stopping teledyne flow meter reader")
        self.running = False
        self._close_socket()
            
    def get_latest_data(self):
        """Get the latest teledyne data from TCP connection"""
        try:
            # Read directly from TCP connection
            values = self._socket_read()
            if values:
                self.data_queue = values
                self.logger.debug(f"Updated teledyne data queue: {self.data_queue}")
            return self.data_queue
        except Exception as e:
            self.logger.error(f"Error getting latest teledyne data: {e}")
            return [None] * 3
            
    def read_data(self):
        """Read data from Teledyne device"""
        if not self.running:
            self.logger.error("Cannot read data - device not started")
            return False
            
        try:
            # Read data from TCP connection
            values = self._socket_read()
            if values:
                self.data_queue = values
                self.logger.debug(f"Updated teledyne data queue: {self.data_queue}")
                return True
            else:
                self.logger.warning("Failed to read data from TCP connection")
                return False
                
        except Exception as e:
            self.logger.error(f"Error reading from teledyne TCP: {e}")
            return False

    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def insert_teledyne_data(self, flow_data):
        """Insert Teledyne data into the flow_rates table"""
        timestamp = await self.get_current_est_time()
        await asyncio.sleep(0.1)  # Small delay for async operations
        return self._insert_teledyne_data_sync(flow_data, timestamp)

    def _insert_teledyne_data_sync(self, flow_data, timestamp):
        """Synchronous function to insert Teledyne data into the flow_rates table"""
        if not self.connection_pool:
            self.logger.warning("No database connection pool available")
            return False
            
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            if flow_data and len(flow_data) >= 3:
                cursor.execute(
                    "INSERT INTO flow_rates (timestamp, flow1, flow2, flow3) VALUES (?, ?, ?, ?)",
                    (timestamp, flow_data[0], flow_data[1], flow_data[2])
                )
                conn.commit()
                self.logger.debug(f"Teledyne data inserted: {flow_data}")
                return True
            else:
                self.logger.warning("Teledyne data is invalid, skipping insertion")
                return False
                
        except Exception as e:
            self.logger.error(f"Error inserting Teledyne data: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def set_connection_pool(self, connection_pool):
        """Set the database connection pool"""
        self.connection_pool = connection_pool

    async def pipeline_data(self):
        """Pipeline method: read data and insert into database"""
        try:
            # Read data from Teledyne device
            data = self.get_latest_data()
            
            # Insert data into database if available
            if data is not None and self.connection_pool:
                await self.insert_teledyne_data(data)
                return True
            else:
                self.logger.warning("No data to pipeline or no connection pool available")
                return False
        except Exception as e:
            self.logger.error(f"Error in Teledyne data pipeline: {e}")
            return False


    