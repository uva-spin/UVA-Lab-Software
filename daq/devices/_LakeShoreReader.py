import serial
import time
import logging
import asyncio
import mariadb
from datetime import datetime
import pytz

class LakeShoreReader:


    def __init__(self, port="COM4", baudrate=9600, bytesize=7, timeout=2, stopbits=1, connection_pool=None, table_name=None):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.stopbits = stopbits
        self.serialPort = None
        self.running = False
        self.data_queue = [0.0] * 8
        self.connection_pool = connection_pool
        self.table_name = table_name or "lakeshore_target_stick"  # Default table name
        self.EST = pytz.timezone('America/New_York')

        self.logger = logging.getLogger(__name__)


    def start(self):
        """Start the LakeShore reader and open the serial port."""
        try:
            if self.running:
                self.logger.warning("LakeShore reader is already running")
                return False
            
            # Close any existing connection
            if self.serialPort and self.serialPort.is_open:
                self.logger.info("Closing existing serial connection")
                self.serialPort.close()
            
            # Open new serial connection with proper parity
            self.logger.info(f"Opening serial port {self.port}")
            self.serialPort = serial.Serial(
                port=self.port, 
                baudrate=self.baudrate, 
                bytesize=self.bytesize, 
                parity=serial.PARITY_ODD,
                timeout=self.timeout, 
                stopbits=self.stopbits
            )
            
            if self.serialPort.is_open:
                self.running = True
                self.logger.info("Serial port opened successfully")
                
                self.logger.info("LakeShore reader started successfully")
                return True
            else:
                self.logger.error("Failed to open serial port")
                return False
                
        except serial.SerialException as e:
            self.logger.error(f"Serial port error: {e}")
            self._cleanup()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error starting LakeShore reader: {e}")
            self._cleanup()
            return False

    def stop(self):
        """Stop the LakeShore reader and close the serial port."""
        self.logger.info("Stopping LakeShore reader")
        
        self.running = False
    
        self._cleanup()
        self.logger.info("LakeShore reader stopped")

    def _cleanup(self):
        """Clean up resources and close serial port."""
        try:
            if self.serialPort:
                if self.serialPort.is_open:
                    self.logger.info("Closing serial port")
                    self.serialPort.close()
                self.serialPort = None
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            self.running = False

    def __del__(self):
        """Destructor to ensure cleanup when object is destroyed."""
        self.stop()

    def _parse_lakeshore_data(self, raw_data):
        """
        Parse LakeShore data response.
        Expected format: "123.456,234.567,345.678,456.789,567.890,678.901,789.012,890.123\r\n"
        """
        try:
            self.logger.debug(f"Raw data: {raw_data}")
            
            # Decode bytes to string and strip whitespace
            if isinstance(raw_data, bytes):
                data_str = raw_data.decode('ascii', errors='ignore').strip()
            else:
                data_str = str(raw_data).strip()
            
            self.logger.debug(f"Decoded data string: {data_str}")
            
            # Split by commas and convert to floats
            if data_str:
                parts = data_str.split(',')
                temperature_values = []
                
                for part in parts:
                    part = part.strip()
                    if part:
                        try:
                            temp_val = float(part)
                            temperature_values.append(temp_val)
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Could not convert '{part}' to float: {e}, using 0.0")
                            temperature_values.append(0.0)
                
                # Ensure we have exactly 8 values
                while len(temperature_values) < 8:
                    temperature_values.append(0.0)
                temperature_values = temperature_values[:8]
                
                self.logger.debug(f"Parsed temperature values: {temperature_values}")
                return temperature_values
            else:
                self.logger.warning("Empty data string received")
                return [0.0] * 8
                
        except Exception as e:
            self.logger.error(f"Error parsing LakeShore data: {e}")
            return [0.0] * 8

    def _read_data(self):
        """Read data from the LakeShore device."""
        self.logger.info("Reading data from LakeShore device")
        
        try:
            # Check if serial port is still open
            if not self.serialPort or not self.serialPort.is_open:
                self.logger.error("Serial port is not open")
                return False
            
            # Simple communication like Teledyne example
            self.serialPort.write(b'SRDG?\r\n')
            raw_data = self.serialPort.readline()
            self.logger.debug(f"Raw data received: {raw_data}")
            
            if raw_data:
                parsed_data = self._parse_lakeshore_data(raw_data)
                self.logger.debug(f"Parsed data: {parsed_data}")
                
                if parsed_data:
                    self.data_queue = parsed_data
                    self.logger.debug(f"Updated data queue: {parsed_data}")
                    return True
                else:
                    self.logger.warning("No valid data received after parsing")
                    return False
            else:
                self.logger.debug("No raw data received from Lakeshore - timeout or empty response")
                return False
                
        except serial.SerialException as e:
            self.logger.error(f"Serial communication error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error reading data: {e}")
            return False

    def read_data(self):
        """Read data from the LakeShore device."""
        if not self.running:
            self.logger.error("Cannot read data - device not started")
            return False
            
        return self._read_data()

    def get_latest_data(self):
        """
        Get the latest data from the LakeShore device.
        Always returns a list of 8 float values.
        """
        self.logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
        
        if self.data_queue and len(self.data_queue) > 0:
            # Ensure we return exactly 8 values
            result = self.data_queue[:8]
            while len(result) < 8:
                result.append(0.0)
            
            self.logger.debug(f"Returning temperature data: {result}")
            return result
        else:
            self.logger.debug(f"Data queue is empty or None: {self.data_queue}")
            return [0.0] * 8

    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def insert_lakeshore_data(self, data):
        """Insert Lakeshore data into the specified table"""
        timestamp = await self.get_current_est_time()
        await asyncio.sleep(0.1)  # Small delay for async operations
        return self._insert_lakeshore_data_sync(data, timestamp)

    def _insert_lakeshore_data_sync(self, data, timestamp):
        """Synchronous function to insert Lakeshore data into the specified table"""
        if not self.connection_pool:
            self.logger.warning("No database connection pool available")
            return False
            
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            if data and len(data) >= 8:
                cursor.execute(
                    f"""INSERT INTO {self.table_name} (timestamp, temp1, temp2, temp3, temp4, 
                       temp5, temp6, temp7, temp8) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (timestamp, data[0], data[1], data[2], data[3], 
                     data[4], data[5], data[6], data[7])
                )
                conn.commit()
                self.logger.debug(f"Lakeshore data inserted into {self.table_name}: {data}")
                return True
            else:
                self.logger.warning(f"Lakeshore data is invalid, skipping insertion into {self.table_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error inserting Lakeshore data into {self.table_name}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def set_connection_pool(self, connection_pool):
        """Set the database connection pool"""
        self.connection_pool = connection_pool

    def set_table_name(self, table_name):
        """Set the database table name for this reader"""
        self.table_name = table_name

    async def pipeline_data(self):
        """Pipeline method: read data and insert into database"""
        try:
            # Read data from LakeShore device
            data = self.get_latest_data()
            
            # Insert data into database if available
            if data is not None and self.connection_pool:
                await self.insert_lakeshore_data(data)
                return True
            else:
                self.logger.warning("No data to pipeline or no connection pool available")
                return False
        except Exception as e:
            self.logger.error(f"Error in LakeShore data pipeline: {e}")
            return False
    


