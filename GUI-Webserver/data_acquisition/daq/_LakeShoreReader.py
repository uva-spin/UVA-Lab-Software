import serial
import time
import logging
import threading
import os

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# Create the data_logs directory and set up file logging
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(os.path.dirname(current_dir), 'data_logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'lakeshore_debug.log')
    logger.addHandler(logging.FileHandler(log_path))
except Exception as e:
    logger.warning(f"Could not set up file logging: {e}")

class LakeShoreReader:
    def __init__(self, port="COM4", baudrate=9600, bytesize=7, timeout=2, stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.stopbits = stopbits
        self.serialPort = None
        self.running = False
        self.thread = None
        self.data_queue = [0.0] * 8
        self._lock = threading.Lock()


    def start(self):
        """Start the LakeShore reader and open the serial port."""
        try:
            if self.running:
                logger.warning("LakeShore reader is already running")
                return False
            
            # Close any existing connection
            if self.serialPort and self.serialPort.is_open:
                logger.info("Closing existing serial connection")
                self.serialPort.close()
            
            # Open new serial connection with proper parity
            logger.info(f"Opening serial port {self.port}")
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
                logger.info("Serial port opened successfully")
                
                # Automatically start the data stream
                if self.data_stream():
                    logger.info("LakeShore reader started successfully with data stream")
                    return True
                else:
                    logger.error("Failed to start data stream")
                    self._cleanup()
                    return False
            else:
                logger.error("Failed to open serial port")
                return False
                
        except serial.SerialException as e:
            logger.error(f"Serial port error: {e}")
            self._cleanup()
            return False
        except Exception as e:
            logger.error(f"Unexpected error starting LakeShore reader: {e}")
            self._cleanup()
            return False

    def stop(self):
        """Stop the LakeShore reader and close the serial port."""
        logger.info("Stopping LakeShore reader")
        
        self.running = False
        
        if self.thread and self.thread.is_alive():
            logger.info("Waiting for data reading thread to finish...")
            self.thread.join(timeout=5.0)  # Wait up to 5 seconds
            if self.thread.is_alive():
                logger.warning("Thread did not finish within timeout")
        
        self._cleanup()
        logger.info("LakeShore reader stopped")

    def _cleanup(self):
        """Clean up resources and close serial port."""
        try:
            if self.serialPort:
                if self.serialPort.is_open:
                    logger.info("Closing serial port")
                    self.serialPort.close()
                self.serialPort = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self.running = False
            self.thread = None

    def __del__(self):
        """Destructor to ensure cleanup when object is destroyed."""
        self.stop()

    def _parse_lakeshore_data(self, raw_data):
        """
        Parse LakeShore data response.
        Expected format: "123.456,234.567,345.678,456.789,567.890,678.901,789.012,890.123\r\n"
        """
        try:
            logger.debug(f"Raw data: {raw_data}")
            
            # Decode bytes to string and strip whitespace
            if isinstance(raw_data, bytes):
                data_str = raw_data.decode('ascii', errors='ignore').strip()
            else:
                data_str = str(raw_data).strip()
            
            logger.debug(f"Decoded data string: {data_str}")
            
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
                            logger.warning(f"Could not convert '{part}' to float: {e}, using 0.0")
                            temperature_values.append(0.0)
                
                # Ensure we have exactly 8 values
                while len(temperature_values) < 8:
                    temperature_values.append(0.0)
                temperature_values = temperature_values[:8]
                
                logger.debug(f"Parsed temperature values: {temperature_values}")
                return temperature_values
            else:
                logger.warning("Empty data string received")
                return [0.0] * 8
                
        except Exception as e:
            logger.error(f"Error parsing LakeShore data: {e}")
            return [0.0] * 8

    def _read_data(self):
        """Read data from the LakeShore device in a separate thread."""
        logger.info("Starting data reading thread")
        
        try:
            while self.running:
                try:
                    # Check if serial port is still open
                    if not self.serialPort or not self.serialPort.is_open:
                        logger.error("Serial port is not open")
                        break
                    
                    # Simple communication like Teledyne example
                    self.serialPort.write(b'SRDG?\r\n')
                    raw_data = self.serialPort.readline()
                    logger.debug(f"Raw data received: {raw_data}")
                    
                    if raw_data:
                        parsed_data = self._parse_lakeshore_data(raw_data)
                        logger.debug(f"Parsed data: {parsed_data}")
                        
                        if parsed_data:
                            with self._lock:
                                self.data_queue = parsed_data
                            logger.debug(f"Updated data queue: {parsed_data}")
                        else:
                            logger.warning("No valid data received after parsing")
                    else:
                        logger.debug("No raw data received from Lakeshore - timeout or empty response")
                    
                    time.sleep(0.1)
                    
                except serial.SerialException as e:
                    logger.error(f"Serial communication error: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error reading data: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Critical error in data reading thread: {e}")
        finally:
            logger.info("Data reading thread stopped")

    def data_stream(self):
        """Start the data streaming thread."""
        if not self.running:
            logger.error("Cannot start data stream - device not started")
            return False
        
        if self.thread and self.thread.is_alive():
            logger.warning("Data stream already running")
            return False
            
        try:
            self.thread = threading.Thread(target=self._read_data, daemon=True)
            self.thread.start()
            logger.info("Data stream started")
            return True
        except Exception as e:
            logger.error(f"Error starting data stream: {e}")
            return False

    def get_latest_data(self):
        """
        Get the latest data from the LakeShore device.
        Always returns a list of 8 float values.
        """
        with self._lock:
            logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
            
            if self.data_queue and len(self.data_queue) > 0:
                # Ensure we return exactly 8 values
                result = self.data_queue[:8]
                while len(result) < 8:
                    result.append(0.0)
                
                logger.debug(f"Returning temperature data: {result}")
                return result
            else:
                logger.debug(f"Data queue is empty or None: {self.data_queue}")
                return [0.0] * 8
    
    


