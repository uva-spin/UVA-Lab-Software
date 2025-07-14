# from _TeledyneReader import TeledyneDataReader

# reader = TeledyneDataReader()


# ### Testing Modbus TCP Connection ###

# print("="*10 + "Testing Modbus TCP Connection" + "="*10)

# try:
#     print("Trying to read integer registers...")
#     reader._read_integer_registers()
# except Exception as e:
#     print(f"Error reading integer registers: {e}")

# try:
#     print("Trying to read float registers...")
#     reader._read_float_registers()
# except Exception as e:
#     print(f"Error reading float registers: {e}")


# ### Testing Socket Connection ###

# print("="*10 + "Testing Socket Connection" + "="*10)

# print("Trying to connect to socket...")
# reader._socket_connection()

# print("Trying to read data from socket...")
# reader._socket_read()

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

client = ModbusClient('172.29.36.192',port=101)       # Create client object
client.connect()                               # connect to device

int_regs = client.read_holding_registers(0, 1, unit=2)
log.debug(int_regs)
assert(not int_regs.isError()) 

client.close()                                 # Disconnect device

        
