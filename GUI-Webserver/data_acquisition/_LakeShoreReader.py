import serial
import time
import logging
import threading
import re

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('data_logs/lakeshore_debug.log'))

class LakeShoreReader:
    def __init__(self, port="COM4", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.stopbits = stopbits
        self.serialPort = None
        self.running = False
        self.thread = None
        self.data_queue = [0.0] * 8
        self._lock = threading.Lock()  # Add thread safety

    def start(self):
        """Start the LakeShore reader and open the serial port."""
        try:
            # Check if already running
            if self.running:
                logger.warning("LakeShore reader is already running")
                return False
            
            # Close any existing connection
            if self.serialPort and self.serialPort.is_open:
                logger.info("Closing existing serial connection")
                self.serialPort.close()
            
            # Open new serial connection
            logger.info(f"Opening serial port {self.port}")
            self.serialPort = serial.Serial(
                port=self.port, 
                baudrate=self.baudrate, 
                bytesize=self.bytesize, 
                timeout=self.timeout, 
                stopbits=self.stopbits
            )
            
            if self.serialPort.is_open:
                self.running = True
                logger.info("Serial port opened successfully")
                return True
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
        
        # Set running flag to False to stop the thread
        self.running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            logger.info("Waiting for data reading thread to finish...")
            self.thread.join(timeout=5.0)  # Wait up to 5 seconds
            if self.thread.is_alive():
                logger.warning("Thread did not finish within timeout")
        
        # Clean up resources
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

    def _clean_and_convert_data(self, raw_bytes):
        """
        Convert raw bytes to a list of float values using ord().
        Applies ord() directly to each byte in the raw input.
        """
        try:
            logger.debug(f"Raw bytes: {raw_bytes}")
            logger.debug(f"Raw bytes type: {type(raw_bytes)}")
            logger.debug(f"Raw bytes length: {len(raw_bytes)}")
            
            # Convert each byte to its ord() value directly
            byte_values = []
            for byte in raw_bytes:
                try:
                    # Convert byte to its numeric value using ord()
                    byte_val = ord(byte)
                    byte_values.append(byte_val)
                    logger.debug(f"Byte {byte} -> ord() = {byte_val}")
                except Exception as e:
                    logger.warning(f"Could not get ord() for byte {byte}: {e}")
                    byte_values.append(0)
            
            logger.debug(f"Byte values: {byte_values}")
            
            # Convert byte values to floats
            cleaned_values = []
            for i, byte_val in enumerate(byte_values):
                try:
                    # Convert byte value to float
                    float_val = float(byte_val)
                    cleaned_values.append(float_val)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not convert byte value {byte_val} to float: {e}, using 0.0")
                    cleaned_values.append(0.0)
            
            # Ensure we have exactly 8 values (LakeShore typically has 8 channels)
            while len(cleaned_values) < 8:
                cleaned_values.append(0.0)
            
            # Truncate if we have more than 8 values
            cleaned_values = cleaned_values[:8]
            
            logger.debug(f"Final cleaned values: {cleaned_values}")
            return cleaned_values
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            # Return default values on error
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
                    
                    # Send command to device
                    self.serialPort.write(b'SRDG?\r\n')
                    
                    # Read response
                    raw_data = self.serialPort.readline()
                    logger.debug(f"Raw data received: {raw_data}")
                    
                    if raw_data:
                        cleaned_data = self._clean_and_convert_data(raw_data)
                        logger.debug(f"Cleaned data: {cleaned_data}")
                        
                        if cleaned_data:
                            with self._lock:
                                self.data_queue = cleaned_data
                            logger.info(f"Updated data queue: {cleaned_data}")
                        else:
                            logger.warning("No valid data received after cleaning")
                    else:
                        logger.warning("No raw data received from device")
                    
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
            # Don't call self.stop() here to avoid recursive calls

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
            # Check if we have any data, regardless of thread status
            logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
            logger.debug(f"Queue type: {type(self.data_queue)}, length: {len(self.data_queue) if self.data_queue else 0}")
            
            # Check if data_queue exists and has content
            if self.data_queue and len(self.data_queue) > 0:
                # Ensure all values are floats
                float_data = []
                for i, value in enumerate(self.data_queue):
                    if value is not None:
                        try:
                            float_val = float(value)
                            float_data.append(float_val)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid value at index {i}: {value}, using 0.0")
                            float_data.append(0.0)
                    else:
                        float_data.append(0.0)
                
                # Ensure we have exactly 8 values
                while len(float_data) < 8:
                    float_data.append(0.0)
                float_data = float_data[:8]
                
                logger.debug(f"Returning float data: {float_data}")
                return float_data
            else:
                logger.debug(f"Data queue is empty or None: {self.data_queue}")
                return [0.0] * 8

    def get_formatted_data(self):
        """
        Get data in a more readable format with labels
        """
        data = self.get_latest_data()
        if data:
            formatted = {}
            for i, value in enumerate(data):
                formatted[f"Channel_{i+1}"] = value
            return formatted
        return None

    def is_connected(self):
        """Check if the device is connected and running."""
        return self.running and self.serialPort and self.serialPort.is_open
    
    
    


