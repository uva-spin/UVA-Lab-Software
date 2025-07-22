import serial 
import time
import logging
import threading

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set logger level to DEBUG

# Create file handler
file_handler = logging.FileHandler('keithley.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add handler to logger
logger.addHandler(file_handler)

# Prevent duplicate logs by not propagating to root logger
logger.propagate = False


class KeithleyReader:
    def __init__(self, port='COM6', baudrate=9600, bytesize=8, timeout=1, stopbits=1):
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
        try:
            if self.running:
                logger.warning("Keithley reader is already running")
                return False

            self.serialPort = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                timeout=self.timeout,
                stopbits=self.stopbits,
                parity=self.parity,
            )

            if self.serialPort.is_open:
                self.running = True
                logger.info("Keithley reader started successfully")
                
                if self.data_stream():
                    logger.info("Keithley reader started successfully with data stream")
                    return True
                else:
                    logger.error("Failed to start data stream")
                    self._cleanup()
                    return False
            
        except Exception as e:
            logger.error(f"Failed to start Keithley reader: {e}")
            return False
        
    def stop(self):

        logger.info("Stopping Keithley reader")

        self.running = False
        
        if self.thread and self.thread.is_alive():
            logger.info("Waiting for data reading thread to finish...")
            self.thread.join(timeout=5.0)  # Wait up to 5 seconds
            if self.thread.is_alive():
                logger.warning("Thread did not finish within timeout")
        
        self._cleanup()
        logger.info("Keithley reader stopped")

    def _cleanup(self):

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
            self.data_queue = None

    def _read_data(self):

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

                
                # if raw_data:
                #     parsed_data = self._parse_keithley_data(raw_data)
                #     logger.debug(f"Parsed data: {parsed_data}")
                    
                #     if parsed_data:
                #         with self._lock:
                #             self.data_queue = parsed_data
                #             logger.info(f"Updated data queue: {parsed_data}")
                #     else:
                #         logger.warning("No valid data received after parsing")
                else:
                    logger.warning("No raw data received from device")
                
                time.sleep(0.1)  # Add delay to prevent high CPU usage
                    
        except Exception as e:
            logger.error(f"Error in data reading thread: {e}")
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
        Get the latest data from the Keithley device.
        Always returns a list of 8 float values.
        """
        with self._lock:
            logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
            
            if self.data_queue and len(self.data_queue) > 0:
                result = self.data_queue

                logger.debug(f"Returning temperature data: {result}")
                return result
            else:
                logger.debug(f"Data queue is empty or None: {self.data_queue}")
                return None
    
    def _parse_keithley_data(self, raw_data):
        """Parse the raw data from the Keithley device."""
        try:
            if not raw_data:
                logger.warning("No raw data received from device")
                return None
            
            # Remove any non-numeric characters and split by commas
            data_str = raw_data.decode('utf-8').strip()
            data_str = data_str.replace(' ', '')
            data_str = data_str.replace('+', '')

        except Exception as e:
            logger.error(f"Error parsing Keithley data: {e}")
            return None