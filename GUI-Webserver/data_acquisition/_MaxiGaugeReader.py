import threading
import time
import socket
import logging
import re

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('data_logs/maxigauge_debug.log'))

class MaxiGaugeReader:
    def __init__(self, baudrate=9600, timeout=1, check_interval=1):
        self.baudrate = baudrate
        self.timeout = timeout
        self.socket = None
        self.running = False
        self.thread = None
        self.data_queue = [None] * 6  # Initialize with 6 None values
        self.check_interval = check_interval
        self.MAXIGAUGE_TCP_IP = "172.29.36.194"
        self.MAXIGAUGE_TCP_PORT = 8000
        self.connected = False
        self.last_connection_attempt = 0
        self.connection_retry_interval = 5  # seconds

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
            logger.info(f"Successfully connected to MaxiGauge at {self.MAXIGAUGE_TCP_IP}:{self.MAXIGAUGE_TCP_PORT}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to MaxiGauge: {e}")
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
                logger.warning("No data received from MaxiGauge!")
                self.connected = False
                return None
                
            ascii_data = data.decode('ascii', errors='ignore')
            logger.debug(f"Received ASCII data: {repr(ascii_data)}")
            
            # Clean up the data by removing control characters and extra whitespace
            # Remove \r\n\x06\r\n from the end and any other control characters
            ascii_data = ascii_data.replace('\r\n\x06\r\n', '').replace('\r\n', '').strip()
            logger.debug(f"Cleaned ASCII data: {repr(ascii_data)}")
            
            # Parse the response
            # Actual format: "3,+1.1000E+03,2,+1.1000E+03,5,+0.0000E+00,..."
            # Extract only the scientific notation values (pressure readings)
            if ascii_data:
                # Split by commas and extract all values
                parts = ascii_data.split(',')
                logger.debug(f"All parts after split: {parts}")
                pressure_values = []
                
                for i, part in enumerate(parts):
                    part = part.strip()
                    logger.debug(f"Processing part {i}: '{part}'")
                    # Check if the part is in scientific notation (contains 'E' or 'e')
                    if 'E' in part.upper() or 'e' in part:
                        try:
                            # Convert scientific notation to float
                            pressure_float = float(part)
                            pressure_values.append(pressure_float)
                            logger.debug(f"Added pressure value: {pressure_float}")
                        except (ValueError, IndexError) as e:
                            logger.debug(f"Failed to convert '{part}' to float: {e}")
                            continue
                
                logger.debug(f"Final extracted pressure values: {pressure_values}")
                return pressure_values if pressure_values else None
            else:
                logger.warning("Empty response from MaxiGauge")
                return None
                
        except socket.timeout:
            logger.debug("Socket timeout - no data available")
            return None
        except Exception as e:
            logger.error(f"Error reading data from MaxiGauge: {e}")
            self.connected = False
            return None

    def start(self):
        """Start the MaxiGauge reader and open the TCP connection."""
        self.running = True
        try:
            self.thread = threading.Thread(target=self._monitor_tcp, daemon=True)
            self.thread.start()
            logger.info("Started MaxiGauge reader")
        except Exception as e:
            logger.error(f"Error starting MaxiGauge reader: {e}")
            return False

    def stop(self):
        """Stop the MaxiGauge reader and close the TCP connection."""
        logger.info("Stopping MaxiGauge reader")
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        if self.thread:
            self.thread.join(timeout=2)

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
            logger.debug(f"Sending command to MaxiGauge: {repr(full_command)}")
            
            # Send command
            self.socket.send(full_command.encode('ascii'))
            
            # Wait for response
            time.sleep(0.2)
            
            # Read response
            data = self.socket.recv(1024)
            if data:
                response = data.decode('ascii', errors='ignore').strip()
                logger.debug(f"Command response from MaxiGauge: {repr(response)}")
                return response
            else:
                logger.warning("No response received for command from MaxiGauge")
                return None
                
        except socket.timeout:
            logger.debug("Socket timeout when sending command to MaxiGauge")
            return None
        except Exception as e:
            logger.error(f"Error sending command '{command}' to MaxiGauge: {e}")
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
                logger.debug(f"Updated MaxiGauge data queue: {self.data_queue}")
                return self.data_queue[:]  # Return a copy
            else:
                # If no fresh data, return cached data if available, otherwise return 6 None values
                if self.data_queue and len(self.data_queue) == 6:
                    return self.data_queue[:]
                else:
                    return [None] * 6
        except Exception as e:
            logger.error(f"Error getting latest MaxiGauge data: {e}")
            return [None] * 6
        
    def _monitor_tcp(self):
        while self.running:
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
                    logger.debug(f"Updated MaxiGauge data queue: {self.data_queue}")
                else:
                    logger.debug("No data received from MaxiGauge")
            except Exception as e:
                logger.error(f"Error monitoring Pfeiffer MaxiGauge: {e}")

            time.sleep(self.check_interval)