import serial
import time
import logging
import os
import asyncio
import mariadb
from datetime import datetime
import pytz


class IVCReader:
    def __init__(self, port='COM7', baudrate=9600, bytesize=8, timeout=1, stopbits=1, connection_pool=None):
        self.port = port
        self.baudrate = baudrate
        self.serialPort = None
        self.running = False
        self.data_queue = None
        self.bytesize = bytesize
        self.timeout = timeout
        self.stopbits = stopbits
        self.parity = serial.PARITY_NONE
        self.connection_pool = connection_pool
        self.EST = pytz.timezone('America/New_York')

        self.logger = logging.getLogger(__name__)

        self.logger.setLevel(logging.INFO)

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(os.path.dirname(self.current_dir), 'data_logs', 'ivc_debug.log')
        self.logger.addHandler(logging.FileHandler(self.log_path))

    def start(self):
        """Start the IVC reader and open the serial port."""
        try:
            if self.running:
                self.logger.warning("IVC reader is already running")
                return False
            
            # Close any existing connection
            if self.serialPort and self.serialPort.is_open:
                self.logger.info("Closing existing serial connection")
                self.serialPort.close()
            
            # Open new serial connection
            self.logger.info(f"Opening serial port {self.port}")
            self.serialPort = serial.Serial(
                port=self.port, 
                baudrate=self.baudrate, 
                bytesize=self.bytesize, 
                parity=self.parity,
                timeout=self.timeout, 
                stopbits=self.stopbits
            )
            
            if self.serialPort.is_open:
                self.running = True
                self.logger.info("Serial port opened successfully")
                return True
            else:
                self.logger.error("Failed to open serial port")
                return False
                
        except serial.SerialException as e:
            self.logger.error(f"Serial port error: {e}")
            self._cleanup()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error starting IVC reader: {e}")
            self._cleanup()
            return False

    def stop(self):
        """Stop the IVC reader"""
        self.logger.info("Stopping IVC reader")
        self.running = False
        self._cleanup()
        self.logger.info("IVC reader stopped")

    def _cleanup(self):
        """Clean up the IVC reader"""
        self.logger.info("Cleaning up IVC reader")
        if self.serialPort:
            if self.serialPort.is_open:
                self.serialPort.close()
            self.serialPort = None
        self.running = False
        self.data_queue = None

    def _read_data(self):
        """Read data from the IVC reader"""
        self.logger.info("Reading data from IVC reader")
        try:
            # Clear the buffer first by sending PRX
            if self.serialPort and self.serialPort.is_open:
                self.logger.info("Clearing buffer with PRX command")
                self.serialPort.write(b'PRX')
                time.sleep(0.1)
                
                # Read any pending data to clear the buffer
                while self.serialPort.in_waiting:
                    self.serialPort.readline()
                time.sleep(1)
            
            if not self.serialPort or not self.serialPort.is_open:
                self.logger.error("Serial port is not open")
                return False
            
            try:
                # Request data transmission using the pattern from the reference code
                self.serialPort.write(b'\x05\r\n')
                
                # Wait for the device to respond - use a longer timeout
                time.sleep(0.5)
                
                # Try to read data with a timeout
                try:
                    # Use readline with timeout to wait for data
                    raw_data = self.serialPort.readline()
                    if raw_data:
                        self.logger.debug(f"Raw data received: {raw_data}")
                        self.data_queue = self._parse_ivc_data(raw_data)
                        return True
                    else:
                        self.logger.debug("No raw data received from IVC - timeout or empty response")
                        return False
                except serial.SerialTimeoutException:
                    self.logger.warning("Timeout waiting for IVC device response")
                    return False
                except Exception as e:
                    self.logger.error(f"Error reading from serial port: {e}")
                    return False
                
            except serial.SerialException as e:
                self.logger.error(f"Serial communication error: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Error reading data: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Error reading data from IVC reader: {e}")
            return False

    def read_data(self):
        """Read data from the IVC reader."""
        if not self.running:
            self.logger.error("Cannot read data - device not started")
            return False
            
        return self._read_data()
            
    def _parse_ivc_data(self, raw_data):
        """Parse the raw data from the IVC reader"""
        try:
            self.logger.debug(f"Parsing IVC data: {raw_data}")
            
            # Decode bytes to string and strip whitespace
            if isinstance(raw_data, bytes):
                data_str = raw_data.decode('ascii', errors='ignore').strip()
            else:
                data_str = str(raw_data).strip()
            
            self.logger.debug(f"Decoded data string: {data_str}")
            
            # Parse the comma-separated data format: statusCode_p1,p1,statusCode_p2,p2
            # We only want the first pressure (p1) with its status code
            if data_str:
                parts = data_str.split(',')
                self.logger.debug(f"Split data parts: {parts}")
                
                # Check if we have enough parts for at least the first pressure
                if len(parts) >= 2:
                    try:
                        status_code_p1 = int(parts[0].strip())
                        p1 = float(parts[1].strip())
                        
                        self.logger.debug(f"Status code p1: {status_code_p1}, Pressure p1: {p1}")
                        
                        # Check status code and return pressure only if data is good quality
                        if status_code_p1 == 0 and p1 >= 0.0:
                            self.logger.debug(f"Valid pressure reading: {p1} mbar")
                            return p1
                        elif status_code_p1 == 1:
                            self.logger.warning("Sensor 1: Underrange")
                        elif status_code_p1 == 2:
                            self.logger.warning("Sensor 1: Overrange")
                        elif status_code_p1 == 3:
                            self.logger.warning("Sensor 1: Sensor error")
                        elif status_code_p1 == 4:
                            self.logger.warning("Sensor 1: Sensor off")
                        elif status_code_p1 == 5:
                            self.logger.warning("Sensor 1: No sensor (output: 5,2000E-2)")
                        elif status_code_p1 == 6:
                            self.logger.warning("Sensor 1: Identification error")
                        else:
                            self.logger.warning(f"Unknown status code for sensor 1: {status_code_p1}")
                        
                        return None
                        
                    except (ValueError, TypeError) as e:
                        self.logger.warning(f"Could not convert data parts to numbers: {e}")
                        return None
                else:
                    self.logger.warning(f"Insufficient data parts. Expected at least 2, got {len(parts)}: {parts}")
                    return None
            else:
                self.logger.warning("Empty data string received")
                return None
            
        except Exception as e:
            self.logger.error(f"Error parsing IVC data: {e}")
            return None
    
    def get_latest_data(self):
        """Get the latest data from the IVC reader"""
        self.logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
        
        if self.data_queue is not None:
            self.logger.debug(f"Returning IVC data: {self.data_queue}")
            return self.data_queue
        else:
            self.logger.debug("Data queue is empty or None")
            return None

    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def insert_ivc_data(self, data):
        """Insert IVC data into the ivc table"""
        timestamp = await self.get_current_est_time()
        await asyncio.sleep(0.1)  # Small delay for async operations
        return self._insert_ivc_data_sync(data, timestamp)

    def _insert_ivc_data_sync(self, data, timestamp):
        """Synchronous function to insert IVC data into the ivc table"""
        if not self.connection_pool:
            self.logger.warning("No database connection pool available")
            return False
            
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            if data is not None:
                cursor.execute(
                    "INSERT INTO ivc (timestamp, data) VALUES (?, ?)",
                    (timestamp, data)
                )
                conn.commit()
                self.logger.debug(f"IVC data inserted: {data}")
                return True
            else:
                self.logger.warning("IVC data is None, skipping insertion")
                return False
                
        except Exception as e:
            self.logger.error(f"Error inserting IVC data: {e}")
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
            # Read data from IVC device
            data = self.get_latest_data()
            
            # Insert data into database if available
            if data is not None and self.connection_pool:
                await self.insert_ivc_data(data)
                return True
            else:
                self.logger.warning("No data to pipeline or no connection pool available")
                return False
        except Exception as e:
            self.logger.error(f"Error in IVC data pipeline: {e}")
            return False