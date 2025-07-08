import struct
import logging
from pyModbusTCP.client import ModbusClient

logger = logging.getLogger(__name__)

class HMIReader:
    def __init__(self, plc_ip, unit_id, int_port, float_port, num_reg_to_read, labels=None):
        """
        Initialize HMI Reader
        
        Args:
            plc_ip (str): IP address of the PLC
            unit_id (int): Modbus unit ID
            int_port (int): Port for integer registers
            float_port (int): Port for float registers
            num_reg_to_read (int): Number of registers to read
            labels (list, optional): List of labels for the float values
        """
        self.plc_ip = plc_ip
        self.unit_id = unit_id
        self.int_port = int_port
        self.float_port = float_port
        self.num_reg_to_read = num_reg_to_read
        self.labels = labels or []
        self.client = None

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
            logger.info("Reading integer values")
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
                logger.info(f'Successfully read integer values: {int_values[:3]}... ({len(int_values)} values)')
                return int_values
            else:
                logger.warning(f"Failed to read integer registers from {self.plc_ip}:{self.int_port}")
                return None
        except Exception as e:
            logger.error(f"Error reading integer registers: {e}")
            return None
        finally:
            if client and client.is_open:
                client.close()
                logger.info("Closed integer Modbus connection")

    def _read_float_registers(self):
        """
        Read float registers from Modbus TCP server
        
        Returns:
            list or None: List of float values or None if failed
        """
        try:
            logger.info("Reading float values")
            client = ModbusClient(
                host=self.plc_ip, 
                port=self.float_port, 
                unit_id=self.unit_id, 
                auto_open=True, 
                auto_close=False
            )
            
            float_regs = client.read_holding_registers(0, self.num_reg_to_read)
            
            if not float_regs:
                logger.error(f"Failed to read float registers from {self.plc_ip}:{self.float_port}")
                return None
                
            logger.info(f"Successfully read {len(float_regs)} float registers")
                
            float_values = []
            logger.info("Converting register pairs to float values...")
            for i in range(0, self.num_reg_to_read - 1, 2):
                raw = struct.pack(">HH", float_regs[i], float_regs[i + 1])  # Big Endian format
                float_values.append(struct.unpack(">f", raw)[0])  # Convert to float
            
            # Round float values to 2 decimal places
            rounded_float_values = [round(value, 2) for value in float_values]
            logger.info(f"Processed {len(rounded_float_values)} float values")
            
            return rounded_float_values
            
        except Exception as e:
            logger.error(f"Error reading float registers: {e}")
            return None
        finally:
            if client and client.is_open:
                client.close()
                logger.info("Closed float Modbus connection")

    def read_hmi_data(self):
        """
        Read HMI data from Modbus TCP server
        
        Returns:
            dict or None: Dictionary containing integer and float data, or None if failed
        """
        logger.info(f"=== Starting HMI Read ===")
        logger.info(f"PLC IP: {self.plc_ip}")
        logger.info(f"Unit ID: {self.unit_id}")
        logger.info(f"Integer Port: {self.int_port}")
        logger.info(f"Float Port: {self.float_port}")

        try:
            # Read integer values
            int_values = self._read_integer_registers()
            
            # Read float values
            float_values = self._read_float_registers()
            
            if float_values is None:
                return None
            
            # Log each value with its corresponding label if labels are provided
            if self.labels:
                for label, value in zip(self.labels, float_values[:18]):
                    logger.debug(f"{label}: {value}")
            
            # Ensure we have exactly 18 values for HMI data
            if len(float_values) >= 18:
                hmi_data = float_values[:18]
                logger.info("Successfully read all HMI data:")
                logger.info("First 3 values:")
                for i in range(min(3, len(hmi_data))):
                    label = self.labels[i] if i < len(self.labels) else f"Value_{i}"
                    logger.info(f"  {label}: {hmi_data[i]}")
                logger.info("... (15 more values)")
                
                return {
                    'integer_values': int_values,
                    'float_values': hmi_data,
                    'labels': self.labels[:18] if self.labels else None
                }
            else:
                logger.error(f"Not enough float values: got {len(float_values)}, need 18")
                return None
            
        except Exception as e:
            logger.error(f"Error reading Modbus data: {e}")
            logger.error("Exception details:", exc_info=True)
            return None

    def close_connections(self):
        """Close any open Modbus connections"""
        try:
            if self.client and self.client.is_open:
                self.client.close()
                logger.info("Closed Modbus connection")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")