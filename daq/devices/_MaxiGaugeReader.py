
import socket
import time
import logging
import asyncio
import mariadb
from datetime import datetime
import pytz

class MaxiGaugeReader:    
    
    def __init__(self, baudrate=9600, timeout=1, check_interval=1, connection_pool=None):
        self.baudrate = baudrate
        self.timeout = timeout
        self.socket = None
        self.running = False
        self.data_queue = [None] * 6  # Initialize with 6 None values
        self.check_interval = check_interval
        self.MAXIGAUGE_TCP_IP = "172.29.36.194"
        self.MAXIGAUGE_TCP_PORT = 8000
        self.connected = False
        self.last_connection_attempt = 0
        self.connection_retry_interval = 5  # seconds
        self.connection_pool = connection_pool
        self.EST = pytz.timezone('America/New_York')

        self.logger = logging.getLogger(__name__)

    def _socket_connection(self):
        """Connect to the MaxiGauge socket"""
        if self.connected and self.socket:
            return True
            
        # Don't retry too frequently
        current_time = time.time()
        if current_time - self.last_connection_attempt < self.connection_retry_interval:
            return False
            
        self.last_connection_attempt = current_time
        
        try:
            # Close existing socket if any
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
                self.connected = False
            
            # Create new socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.MAXIGAUGE_TCP_IP, self.MAXIGAUGE_TCP_PORT))
            self.connected = True
            self.logger.info(f"Successfully connected to MaxiGauge at {self.MAXIGAUGE_TCP_IP}:{self.MAXIGAUGE_TCP_PORT}")
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to MaxiGauge: {e}")
            self.connected = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            return False

    def _socket_read(self):
        """Read data from the MaxiGauge socket

        Send PRX command with proper protocol: PRX<CR><LF><ENQ>
        Response format: Channel,Status,Pressure,Unit,Channel,Status,Pressure,Unit,...
        
        """
        if not self._socket_connection():
            return None
            
        try:
            # Send PRX command with proper protocol: PRX<CR><LF><ENQ>
            # command = 'PRX\r\n'
            # logger.debug(f"Sending command: {repr(command)}")
            self.socket.send(b'PRX\r\n')
            time.sleep(0.1)
            self.socket.send(b'\x05')
    
            # Read the response
            data = self.socket.recv(1024)
            if not data:
                self.logger.warning("No data received from MaxiGauge!")
                self.connected = False
                return None
                
            ascii_data = data.decode('ascii', errors='ignore')
            self.logger.debug(f"Received ASCII data: {repr(ascii_data)}")
            
            # Clean up the data by removing control characters and extra whitespace
            # Remove \r\n\x06\r\n from the end and any other control characters
            ascii_data = ascii_data.replace('\r\n\x06\r\n', '').replace('\r\n', '').strip()
            self.logger.debug(f"Cleaned ASCII data: {repr(ascii_data)}")
            
            # Parse the response
            # Actual format: "3,+1.1000E+03,2,+1.1000E+03,5,+0.0000E+00,..."
            # Extract only the scientific notation values (pressure readings)
            if ascii_data:
                # Split by commas and extract all values
                parts = ascii_data.split(',')
                self.logger.debug(f"All parts after split: {parts}")
                pressure_values = []
                
                for i, part in enumerate(parts):
                    part = part.strip()
                    self.logger.debug(f"Processing part {i}: '{part}'")
                    # Check if the part is in scientific notation (contains 'E' or 'e')
                    if 'E' in part.upper() or 'e' in part:
                        try:
                            # Convert scientific notation to float
                            pressure_float = float(part)
                            pressure_values.append(pressure_float)
                            self.logger.debug(f"Added pressure value: {pressure_float}")
                        except (ValueError, IndexError) as e:
                            self.logger.debug(f"Failed to convert '{part}' to float: {e}")
                            continue
                
                self.logger.debug(f"Final extracted pressure values: {pressure_values}")
                return pressure_values if pressure_values else None
            else:
                self.logger.warning("Empty response from MaxiGauge")
                return None
                
        except socket.timeout:
            self.logger.debug("Socket timeout - no data available")
            return None
        except Exception as e:
            self.logger.error(f"Error reading data from MaxiGauge: {e}")
            self.connected = False
            return None

    def start(self):
        """Start the MaxiGauge reader and open the TCP connection."""
        self.running = True
        self.logger.info("Started MaxiGauge reader")
        return True

    def stop(self):
        """Stop the MaxiGauge reader and close the TCP connection."""
        self.logger.info("Stopping MaxiGauge reader")
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False

    def send_command(self, command):
        """Send a command to the MaxiGauge device with proper protocol
        
        Args:
            command (str): Command to send (e.g., 'PRX', 'TID', etc.)
            
        Returns:
            str: Response from the device or None if error
        """
        if not self._socket_connection():
            return None
            
        try:
            # Add proper protocol: command<CR><LF><ENQ>
            full_command = f"{command}\r\n\x05"
            self.logger.debug(f"Sending command to MaxiGauge: {repr(full_command)}")
            
            # Send command
            self.socket.send(full_command.encode('ascii'))
            
            # Wait for response
            time.sleep(0.2)
            
            # Read response
            data = self.socket.recv(1024)
            if data:
                response = data.decode('ascii', errors='ignore').strip()
                self.logger.debug(f"Command response from MaxiGauge: {repr(response)}")
                return response
            else:
                self.logger.warning("No response received for command from MaxiGauge")
                return None
                
        except socket.timeout:
            self.logger.debug("Socket timeout when sending command to MaxiGauge")
            return None
        except Exception as e:
            self.logger.error(f"Error sending command '{command}' to MaxiGauge: {e}")
            self.connected = False
            return None

    def get_latest_data(self):
        """Get the latest MaxiGauge data from the TCP connection"""
        try:
            data = self._socket_read()
            if data and isinstance(data, list):
                # Ensure we have exactly 6 values
                if len(data) >= 6:
                    self.data_queue = data[:6]  # Take first 6 values
                else:
                    # Pad with None if we have fewer than 6 values
                    padded_data = data + [None] * (6 - len(data))
                    self.data_queue = padded_data
                self.logger.debug(f"Updated MaxiGauge data queue: {self.data_queue}")
                return self.data_queue[:]  # Return a copy
            else:
                # If no fresh data, return cached data if available, otherwise return 6 None values
                if self.data_queue and len(self.data_queue) == 6:
                    return self.data_queue[:]
                else:
                    return [None] * 6
        except Exception as e:
            self.logger.error(f"Error getting latest MaxiGauge data: {e}")
            return [None] * 6
        
    def read_data(self):
        """Read data from MaxiGauge"""
        if not self.running:
            self.logger.error("Cannot read data - device not started")
            return False
            
        try:
            data = self._socket_read()
            if data and isinstance(data, list):
                # Ensure we have exactly 6 values
                if len(data) >= 6:
                    self.data_queue = data[:6]  # Take first 6 values
                else:
                    # Pad with None if we have fewer than 6 values
                    padded_data = data + [None] * (6 - len(data))
                    self.data_queue = padded_data
                self.logger.debug(f"Updated MaxiGauge data queue: {self.data_queue}")
                return True
            else:
                self.logger.debug("No data received from MaxiGauge")
                return False
        except Exception as e:
            self.logger.error(f"Error reading from Pfeiffer MaxiGauge: {e}")
            return False

    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def insert_maxigauge_data(self, data):
        """Insert MaxiGauge data into the maxigauge table"""
        timestamp = await self.get_current_est_time()
        await asyncio.sleep(0.1)  # Small delay for async operations
        return self._insert_maxigauge_data_sync(data, timestamp)

    def _insert_maxigauge_data_sync(self, data, timestamp):
        """Synchronous function to insert MaxiGauge data into the maxigauge table"""
        if not self.connection_pool:
            self.logger.warning("No database connection pool available")
            return False
            
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            if data and len(data) >= 6:
                cursor.execute(
                    """INSERT INTO maxigauge (timestamp, pressure1, pressure2, pressure3, 
                       pressure4, pressure5, pressure6) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (timestamp, data[0], data[1], data[2], data[3], data[4], data[5])
                )
                conn.commit()
                self.logger.debug(f"MaxiGauge data inserted: {data}")
                return True
            else:
                self.logger.warning("MaxiGauge data is invalid, skipping insertion")
                return False
                
        except Exception as e:
            self.logger.error(f"Error inserting MaxiGauge data: {e}")
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
            # Read data from MaxiGauge device
            data = self.get_latest_data()
            
            # Insert data into database if available
            if data is not None and self.connection_pool:
                await self.insert_maxigauge_data(data)
                return True
            else:
                self.logger.warning("No data to pipeline or no connection pool available")
                return False
        except Exception as e:
            self.logger.error(f"Error in MaxiGauge data pipeline: {e}")
            return False