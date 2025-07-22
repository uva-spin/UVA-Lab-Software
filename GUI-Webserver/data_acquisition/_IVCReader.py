import serial
import time
import logging
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class IVCReader:
    def __init__(self, port='COM7', baudrate=9600, bytesize=8, timeout=1, stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.serialPort = None
        self.running = False
        self.thread = None
        self.data_queue = None
        self._lock = threading.Lock()
        self.bytesize = bytesize
        self.timeout = timeout
        self.stopbits = stopbits
        self.parity = serial.PARITY_NONE

    def start(self):
        """Start the IVC reader"""
        logger.info("Starting IVC reader")
        self.running = True
        self.thread = threading.Thread(target=self._read_data)
        self.thread.start()

    def stop(self):
        """Stop the IVC reader"""
        logger.info("Stopping IVC reader")
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
            if self.thread.is_alive():
                logger.warning("Thread did not finish within timeout")
        self._cleanup()
        logger.info("IVC reader stopped")

    def _cleanup(self):
        """Clean up the IVC reader"""
        logger.info("Cleaning up IVC reader")
        if self.serialPort:
            if self.serialPort.is_open:
                self.serialPort.close()
            self.serialPort = None
        self.running = False
        self.thread = None
        self.data_queue = None

    def _read_data(self):
        """Read data from the IVC reader"""
        logger.info("Starting data reading thread")
        try:
            while self.running:
                if not self.serialPort or not self.serialPort.is_open:
                    logger.error("Serial port is not open")
                    break
                
                self.serialPort.write(b'*idn?')
                raw_data = self.serialPort.readline()
                if raw_data:
                    logger.debug(f"Raw data received: {raw_data}")
                    self.data_queue = raw_data
                else:
                    logger.warning("No raw data received from device")
                    
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error reading data from IVC reader: {e}")
            self._cleanup()
            raise

    def data_stream(self):
        """Get the latest data from the IVC reader"""
        with self._lock:
            logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
            
            if self.data_queue and len(self.data_queue) > 0:
                result = self.data_queue

                logger.debug(f"Returning temperature data: {result}")
                return result
            else:
                logger.debug(f"Data queue is empty or None: {self.data_queue}")
                return None 
            
    def _parse_ivc_data(self, raw_data):
        """Parse the raw data from the IVC reader"""
        logger.debug(f"Parsing IVC data: {raw_data}")
        return raw_data
    
    def get_latest_data(self):
        """Get the latest data from the IVC reader"""
        with self._lock:
            logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
            
            if self.data_queue and len(self.data_queue) > 0:
                result = self.data_queue

                logger.debug(f"Returning temperature data: {result}")
                return result
            else:
                logger.debug(f"Data queue is empty or None: {self.data_queue}")
                return None