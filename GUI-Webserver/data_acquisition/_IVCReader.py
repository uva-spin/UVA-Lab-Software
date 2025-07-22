import serial
import time
import logging
import threading
import re

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
                
                # Automatically start the data stream
                if self.data_stream():
                    logger.info("IVC reader started successfully with data stream")
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
                    self.serialPort.write(b'PRX\r\n')
                    time.sleep(0.1)
                    self.serialPort.write(b'\x05')
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
            
            # Remove any non-printable characters and control characters
            clean_data = re.sub(r'[^\x20-\x7E]', '', data_str)
            logger.debug(f"Cleaned data string: {clean_data}")
            
            # Parse the comma-separated data format: 1,<number>,5,<number>
            # We want the second entry (index 1 after splitting)
            if clean_data:
                parts = clean_data.split(',')
                logger.debug(f"Split data parts: {parts}")
                
                # Look for numeric values in all parts, not just the second one
                for i, part in enumerate(parts):
                    part = part.strip()
                    if part:
                        try:
                            # Try to extract scientific notation or regular float
                            if 'E' in part.upper() or 'e' in part:
                                # Scientific notation
                                numeric_value = float(part)
                                logger.debug(f"Extracted scientific notation value from part {i}: {numeric_value}")
                                return numeric_value
                            else:
                                # Regular number
                                numeric_value = float(part)
                                # Skip obvious status codes like 1, 5, etc. (usually single digits)
                                if abs(numeric_value) > 10 or (numeric_value != int(numeric_value) if numeric_value == int(numeric_value) else True):
                                    logger.debug(f"Extracted numeric value from part {i}: {numeric_value}")
                                    return numeric_value
                        except (ValueError, TypeError) as e:
                            logger.debug(f"Could not convert part '{part}' to float: {e}")
                            continue
                
                # If we couldn't find a good numeric value, try the traditional second position
                if len(parts) >= 2:
                    try:
                        second_value = float(parts[1].strip())
                        logger.debug(f"Fallback: extracted second value: {second_value}")
                        return second_value
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Could not convert fallback value '{parts[1]}' to float: {e}")
                
                logger.warning(f"No valid numeric data found in parts: {parts}")
                return None
            else:
                logger.warning("Empty or invalid data string received")
                return None
            
        except Exception as e:
            logger.error(f"Error parsing IVC data: {e}")
            return None
    
    def get_latest_data(self):
        """Get the latest data from the IVC reader with retry logic for valid numeric data"""
        max_attempts = 5
        attempt_delay = 0.1  # 100ms between attempts
        
        for attempt in range(max_attempts):
            with self._lock:
                current_data = self.data_queue
                
            # Check if we have valid numeric data
            if current_data is not None and isinstance(current_data, (int, float)):
                logger.debug(f"Returning valid IVC data: {current_data}")
                return current_data
            
            # If no valid data, try to get fresh data directly
            if attempt < max_attempts - 1:  # Don't wait on the last attempt
                logger.debug(f"No valid IVC data yet (attempt {attempt + 1}/{max_attempts}), trying to get fresh data...")
                fresh_data = self._get_fresh_data()
                if fresh_data is not None and isinstance(fresh_data, (int, float)):
                    with self._lock:
                        self.data_queue = fresh_data
                    logger.debug(f"Got fresh IVC data: {fresh_data}")
                    return fresh_data
                
                time.sleep(attempt_delay)
        
        logger.warning("Could not get valid numeric IVC data after multiple attempts")
        return None
    
    def _get_fresh_data(self):
        """Try to get fresh data immediately from the device"""
        if not self.serialPort or not self.serialPort.is_open:
            return None
            
        try:
            # Clear any pending data
            if self.serialPort.in_waiting > 0:
                self.serialPort.read_all()
            
            # Send command and read response
            self.serialPort.write(b'PRX\r\n')
            time.sleep(0.1)
            self.serialPort.write(b'\x05')
            time.sleep(0.1)
            
            raw_data = self.serialPort.readline()
            if raw_data:
                logger.debug(f"Fresh raw data received: {raw_data}")
                return self._parse_ivc_data(raw_data)
            else:
                logger.debug("No fresh raw data received from device")
                return None
                
        except Exception as e:
            logger.debug(f"Error getting fresh IVC data: {e}")
            return None