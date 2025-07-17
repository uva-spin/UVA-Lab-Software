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
        self.data_queue = []
        self.check_interval = check_interval
        self.MAXIGAUGE_TCP_IP = "172.29.36.194"
        self.MAXIGAUGE_TCP_PORT = 8000
        self.MAXIGAUGE_TCP_UNIT_ID = 2
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

        Data comes in nice format: 1, %e, 2, %e, 5, %e, 5, %e, 5, %e, 5, %e
        Just get the %e values and return them as a list
        If there are no %e values, return None
        
        """
        if not self._socket_connection():
            return None
            
        try:
            self.data = []
            for i in range(6):
                self.socket.send(f'PR{i}\r\n'.encode('ascii'))
                time.sleep(0.1)
                data = self.socket.recv(1024)
                if not data:
                    logger.warning("No data received from MaxiGauge!")
                    self.connected = False
                    return None
                ascii_data = data.decode('ascii', errors='ignore')
                self.data.append(ascii_data)
            if not data:
                logger.warning("No data received from MaxiGauge!")
                self.connected = False
                return None
            ascii_data = data.decode('ascii', errors='ignore')
            logger.debug(f"Received ASCII data: {ascii_data}")
            # Find the %e values
            values = re.findall(r'%e', ascii_data)
            logger.debug(f"Found data values: {values}")
            if not values:
                logger.warning("No data values found in MaxiGauge data!")
                return None
            return values
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

    def get_latest_data(self):
        """Get the latest MaxiGauge data from the TCP connection"""
        try:
            data = self._socket_read()
            if data:
                self.data_queue = data
                logger.debug(f"Updated MaxiGauge data queue: {self.data_queue}")
            return self.data_queue
        except Exception as e:
            logger.error(f"Error getting latest MaxiGauge data: {e}")
            return None
        
    def _monitor_tcp(self):
        while self.running:
            try:
                data = self._socket_read()
                if data:
                    self.data_queue = data
                    logger.debug(f"Updated MaxiGauge data queue: {self.data_queue}")
                else:
                    logger.debug("No data received from MaxiGauge")
            except Exception as e:
                logger.error(f"Error monitoring Pfeiffer MaxiGauge: {e}")

            time.sleep(self.check_interval)