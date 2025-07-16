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
        self.data_queue = [None, None, None]

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
        try:

            raw_bytes = re.sub(r'b\'','',raw_bytes)
            
            raw_string = raw_bytes.decode('ascii')
            
            values = raw_string.strip().split(',')
            cleaned_values = []
            
            for value in values:
                clean_value = value.strip()
                if clean_value:
                    try:
                        float_val = float(clean_value)
                        cleaned_values.append(float_val)
                    except ValueError:
                        cleaned_values.append(clean_value)
            
            return cleaned_values
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            return []

    def _read_data(self):
        while self.running:
            try:
                self.serialPort.write(b'SRDG?\r\n')
                
                raw_data = self.serialPort.readline()
                
                if raw_data:
                    cleaned_data = self._clean_and_convert_data(raw_data)
                    
                    if cleaned_data:
                        self.data_queue = cleaned_data
                        logger.debug(f"Received data: {cleaned_data}")
                    else:
                        logger.warning("No valid data received")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error reading data: {e}")
                time.sleep(1)

    def data_stream(self):
        self.thread = threading.Thread(target=self._read_data)
        self.thread.start()

    def get_latest_data(self):
        if self.thread and self.thread.is_alive():
            return self.data_queue
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
    
    
    


