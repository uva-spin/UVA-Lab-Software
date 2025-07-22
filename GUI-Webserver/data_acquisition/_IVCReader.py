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
        """Start the IVC reader and open the serial port."""
        try:
            if self.running:
                logger.warning("IVC reader is already running")
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
                parity=self.parity,
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
            logger.error(f"Unexpected error starting IVC reader: {e}")
            self._cleanup()
            return False

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
                
                try:
                    self.serialPort.write(b'PRX')
                    raw_data = self.serialPort.readline()
                    if raw_data:
                        logger.debug(f"Raw data received: {raw_data}")
                        with self._lock:
                            self.data_queue = self._parse_ivc_data(raw_data)
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
            logger.error(f"Error reading data from IVC reader: {e}")
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
            
    def _parse_ivc_data(self, raw_data):
        """Parse the raw data from the IVC reader"""
        try:
            logger.debug(f"Parsing IVC data: {raw_data}")
            
            # Decode bytes to string and strip whitespace
            if isinstance(raw_data, bytes):
                data_str = raw_data.decode('ascii', errors='ignore').strip()
            else:
                data_str = str(raw_data).strip()
            
            logger.debug(f"Decoded data string: {data_str}")
            return data_str
            
        except Exception as e:
            logger.error(f"Error parsing IVC data: {e}")
            return None
    
    def get_latest_data(self):
        """Get the latest data from the IVC reader"""
        with self._lock:
            logger.debug(f"get_latest_data called. Queue contents: {self.data_queue}")
            
            if self.data_queue is not None:
                logger.debug(f"Returning IVC data: {self.data_queue}")
                return self.data_queue
            else:
                logger.debug("Data queue is empty or None")
                return None