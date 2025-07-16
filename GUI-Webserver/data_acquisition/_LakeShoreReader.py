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

    def start(self):
        self.serialPort = serial.Serial(
            port=self.port, baudrate=self.baudrate, bytesize=self.bytesize, timeout=self.timeout, stopbits=self.stopbits
        )
        self.running = True

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.serialPort:
            self.serialPort.close()

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
                    
                    # # Check for reasonable range (0-255 for bytes)
                    # if 0 <= float_val <= 255:  # Valid byte range
                    #     cleaned_values.append(float_val)
                    # else:
                    #     logger.warning(f"Byte value {float_val} out of range, using 0.0")
                    #     cleaned_values.append(0.0)
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
        logger.info("Starting data reading thread")
        while self.running:
            try:
                self.serialPort.write(b'SRDG?\r\n')
                
                raw_data = self.serialPort.readline()
                logger.debug(f"Raw data received: {raw_data}")
                
                if raw_data:
                    cleaned_data = self._clean_and_convert_data(raw_data)
                    logger.debug(f"Cleaned data: {cleaned_data}")
                    
                    if cleaned_data:
                        self.data_queue = cleaned_data
                        logger.info(f"Updated data queue: {cleaned_data}")
                        logger.debug(f"Data queue type: {type(self.data_queue)}, length: {len(self.data_queue)}")
                        logger.debug(f"Data queue contents: {[type(x) for x in self.data_queue]}")
                    else:
                        logger.warning("No valid data received after cleaning")
                        logger.debug(f"cleaned_data is empty or falsy: {cleaned_data}")
                else:
                    logger.warning("No raw data received from device")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error reading data: {e}")
                time.sleep(1)
        
        logger.info("Data reading thread stopped")

    def data_stream(self):
        if not self.running:
            logger.error("Cannot start data stream - device not started")
            return
        
        if self.thread and self.thread.is_alive():
            logger.warning("Data stream already running")
            return
            
        self.thread = threading.Thread(target=self._read_data)
        self.thread.start()
        logger.info("Data stream started")

    def get_latest_data(self):
        """
        Get the latest data from the LakeShore device.
        Always returns a list of 8 float values.
        """
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
    
    
    


