import serial
import time
import logging
import threading
import re

logger = logging.getLogger(__name__)

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
        self.data_queue = [None] * 8

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
        Clean raw bytes before converting to ASCII, then parse the data
        """
        try:
            # First, clean the raw bytes by filtering out control characters
            cleaned_bytes = b''
            for byte in raw_bytes:
                # Keep only printable ASCII characters (32-126) and newline/carriage return
                if byte in [10, 13] or (32 <= byte <= 126):
                    cleaned_bytes += bytes([byte])
            
            # Now convert cleaned bytes to string
            raw_string = cleaned_bytes.decode('ascii')
            
            # Remove any remaining whitespace and split by commas
            values = raw_string.strip().split(',')
            cleaned_values = []
            
            logger.debug(f"Raw string: '{raw_string}', split values: {values}")
            
            for value in values:
                clean_value = value.strip()
                if clean_value:
                    try:
                        # Try to convert to float if it's a number
                        float_val = float(clean_value)
                        cleaned_values.append(float_val)
                    except ValueError:
                        # If not a number, keep as string
                        cleaned_values.append(clean_value)
            
            logger.debug(f"Cleaned values: {cleaned_values}")
            return cleaned_values
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            return []

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
        # Check if we have any data, regardless of thread status
        logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
        logger.debug(f"Queue type: {type(self.data_queue)}, length: {len(self.data_queue) if self.data_queue else 0}")
        
        # Check if data_queue exists and has content
        if self.data_queue and len(self.data_queue) > 0:
            # Check if any element is not None and not an empty string
            has_valid_data = any(x is not None and x != '' for x in self.data_queue)
            if has_valid_data:
                logger.debug(f"Returning data: {self.data_queue}")
                return self.data_queue
            else:
                logger.debug(f"Data queue exists but contains no valid data: {self.data_queue}")
        else:
            logger.debug(f"Data queue is empty or None: {self.data_queue}")
        
        return None

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
    
    
    


