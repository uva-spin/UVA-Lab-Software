import struct
import logging
import asyncio
import mariadb
from datetime import datetime
import pytz
import os
from pyModbusTCP.client import ModbusClient


class QTReader:

    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler() ## Console handler
    logger.addHandler(console_handler) 

    console_handler.setFormatter(logging.Formatter( ## Format for what shows on console
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    def __init__(self, plc_ip="172.29.36.193", unit_id=1, int_port=502, float_port=503, num_reg_to_read=36, labels=None, connection_pool=None):
        """
        Initialize QT Reader
        
        Args:
            plc_ip (str): IP address of the PLC
            unit_id (int): Modbus unit ID
            int_port (int): Port for integer registers
            float_port (int): Port for float registers
            num_reg_to_read (int): Number of registers to read
            labels (list, optional): List of labels for the float values
            connection_pool: Database connection pool
        """
        self.plc_ip = plc_ip
        self.unit_id = unit_id
        self.int_port = int_port
        self.float_port = float_port
        self.num_reg_to_read = num_reg_to_read
        self.labels = labels or []
        self.client = None
        self.connection_pool = connection_pool
        self.EST = pytz.timezone('America/New_York')

    def _get_list_2comp(self, regs, bits=16):
        """
        Convert registers to 2's complement integers
        
        Args:
            regs (list): List of register values
            bits (int): Number of bits (default 16)
            
        Returns:
            list: List of converted integer values
        """
        max_value = 2 ** (bits - 1)
        converted = []
        for reg in regs:
            if reg >= max_value:
                reg = reg - (2 ** bits)
            converted.append(reg)
        return converted

    def _read_integer_registers(self):
        """
        Read integer registers from Modbus TCP server
        
        Returns:
            list or None: List of integer values or None if failed
        """
        try:
            self.logger.info("Reading integer values")
            client = ModbusClient(
                host=self.plc_ip, 
                port=self.int_port, 
                unit_id=self.unit_id, 
                auto_open=True, 
                auto_close=False
            )
            
            int_regs = client.read_holding_registers(0, self.num_reg_to_read)
            if int_regs:
                int_values = self._get_list_2comp(int_regs, 16)
                self.logger.info(f'Successfully read integer values: {int_values[:3]}... ({len(int_values)} values)')
                return int_values
            else:
                self.logger.warning(f"Failed to read integer registers from {self.plc_ip}:{self.int_port}")
                return None
        except Exception as e:
            self.logger.error(f"Error reading integer registers: {e}")
            return None
        finally:
            if client and client.is_open:
                client.close()
                self.logger.info("Closed integer Modbus connection")

    def _read_float_registers(self):
        """
        Read float registers from Modbus TCP server
        
        Returns:
            list or None: List of float values or None if failed
        """
        try:
            self.logger.info("Reading float values")
            client = ModbusClient(
                host=self.plc_ip, 
                port=self.float_port, 
                unit_id=self.unit_id, 
                auto_open=True, 
                auto_close=False
            )
            
            float_regs = client.read_holding_registers(0, self.num_reg_to_read)
            
            if not float_regs:
                self.logger.error(f"Failed to read float registers from {self.plc_ip}:{self.float_port}")
                return None
                
            self.logger.info(f"Successfully read {len(float_regs)} float registers")
                
            float_values = []
            self.logger.info("Converting register pairs to float values...")
            for i in range(0, self.num_reg_to_read - 1, 2):
                raw = struct.pack(">HH", float_regs[i], float_regs[i + 1])  # Big Endian format
                float_values.append(struct.unpack(">f", raw)[0])  # Convert to float
            
            # Round float values to 10 decimal places
            rounded_float_values = [round(value, 10) for value in float_values]
            self.logger.info(f"Processed {len(rounded_float_values)} float values")
            
            return rounded_float_values
            
        except Exception as e:
            self.logger.error(f"Error reading float registers: {e}")
            return None
        finally:
            if client and client.is_open:
                client.close()
                self.logger.info("Closed float Modbus connection")

    def read_qt_data(self):
        """
        Read QT data from Modbus TCP server
        
        Returns:
            list or None: List of 18 float values for QT data, or None if failed
        """
        self.logger.info(f"=== Starting QT Read ===")
        self.logger.info(f"PLC IP: {self.plc_ip}")
        self.logger.info(f"Unit ID: {self.unit_id}")
        self.logger.info(f"Integer Port: {self.int_port}")
        self.logger.info(f"Float Port: {self.float_port}")

        try:
            # Read integer values (for reference, not used in final output)
            int_values = self._read_integer_registers()
            
            # Read float values
            float_values = self._read_float_registers()
            
            if float_values is None:
                return None
            
            # Log each value with its corresponding label if labels are provided
            if self.labels:
                self.logger.debug("QT Data Values:")
                for label, value in zip(self.labels, float_values[:18]):
                    self.logger.debug(f"{label}: {value}")
            
            # Ensure we have exactly 18 values for QT data
            if len(float_values) >= 18:
                qt_data = float_values[:18]
                self.logger.info("Successfully read all QT data")
                self.logger.debug("First 3 values:")
                for i in range(3):
                    label = self.labels[i] if i < len(self.labels) else f"Value_{i}"
                    self.logger.debug(f"  {label}: {qt_data[i]}")
                self.logger.debug("... (15 more values)")
                return qt_data
            else:
                self.logger.error(f"Not enough float values: got {len(float_values)}, need 18")
                return None
            
        except Exception as e:
            self.logger.error(f"Error reading QT data: {e}")
            self.logger.debug("Exception details:", exc_info=True)
            return None

    def close_connections(self):
        """Close any open Modbus connections"""
        try:
            if self.client and self.client.is_open:
                self.client.close()
                self.logger.info("Closed QT Modbus connection")
        except Exception as e:
            self.logger.warning(f"Error closing connection: {e}")

    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def insert_qt_data(self, data):
        """Insert QT data into the QT table"""
        timestamp = await self.get_current_est_time()
        await asyncio.sleep(0.1)  # Small delay for async operations
        return self._insert_qt_data_sync(data, timestamp)

    def _insert_qt_data_sync(self, data, timestamp):
        """Synchronous function to insert QT data into the QT table"""
        if not self.connection_pool:
            self.logger.warning("No database connection pool available")
            return False
            
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            if data is not None:
                cursor.execute(
                    "INSERT INTO QT (timestamp, data) VALUES (?, ?)",
                    (timestamp, data)
                )
                conn.commit()
                self.logger.debug(f"QT data inserted: {data}")
                return True
            else:
                self.logger.warning("QT data is None, skipping insertion")
                return False
                
        except Exception as e:
            self.logger.error(f"Error inserting QT data: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def set_connection_pool(self, connection_pool):
        """Set the database connection pool"""
        self.connection_pool = connection_pool

    async def pipeline_data(self):
        """Pipeline method: read data and insert into database"""
        try:
            # Read data from QT device
            data = self.read_qt_data()
            
            # Insert data into database if available
            if data is not None and self.connection_pool:
                await self.insert_qt_data(data)
                return True
            else:
                self.logger.warning("No data to pipeline or no connection pool available")
                return False
        except Exception as e:
            self.logger.error(f"Error in QT data pipeline: {e}")
            return False 