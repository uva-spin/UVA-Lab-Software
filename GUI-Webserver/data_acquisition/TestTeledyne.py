from _TeledyneReader import TeledyneDataReader

reader = TeledyneDataReader()

try:
    print("Trying to read integer registers...")
    reader._read_integer_registers()
    print("Successfully read integer registers")
except Exception as e:
    print(f"Error reading integer registers: {e}")

try:
    print("Trying to read float registers...")
    reader._read_float_registers()
    print("Successfully read float registers")
except Exception as e:
    print(f"Error reading float registers: {e}")

print(reader.get_latest_data())