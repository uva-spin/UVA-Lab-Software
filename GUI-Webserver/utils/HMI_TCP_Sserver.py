from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import struct
import time
import csv
import requests
import json 

# Define the labels for the float values
labels = [
    "FC501.AI.Value",
    "FC501_OUT.Value",
    "FC502.AI.Value",
    "FC502_OUT.Value",
    "LIT501.AI.Value",
    "PT501.AI.Value",
    "PT502.AI.Value",
    "PT503.AI.Value",
    "PT504.AI.Value",
    'Purity Meter_DB."Purity Downstream"',
    'Purity Meter_DB."Purity Upstream"',
    "AIT501.AI.Value",
    "TI501.AI.Value",
    "TI502.AI.Value",
    "TI503.AI.Value",
    "TI504.AI.Value",
    "TI505.AI.Value",
    "TI523.AI.Value"
]

def read_modbus_data():
    plc_ip = "192.168.0.1"
    unit_id = 2
    int_port = 503
    float_port = 502
    num_reg_to_read = 49

    # Read integer values
    client = ModbusClient(host=plc_ip, port=int_port, unit_id=unit_id, auto_open=True, auto_close=False)
    int_regs = client.read_holding_registers(0, num_reg_to_read)
    print(f'Integer values: {utils.get_list_2comp(int_regs, 16)}')

    # Read float values
    client = ModbusClient(host=plc_ip, port=float_port, unit_id=unit_id, auto_open=True, auto_close=False)
    float_regs = client.read_holding_registers(0, num_reg_to_read)
    float_values = []
    for i in range(0, num_reg_to_read - 1, 2):
        raw = struct.pack(">HH", float_regs[i], float_regs[i + 1])  # Big Endian format
        float_values.append(struct.unpack(">f", raw)[0])  # Convert to float
    print("Float values:", float_values)

    # Round float values to 2 decimal places
    rounded_float_values = [round(value, 2) for value in float_values]
    print("Rounded float values:", rounded_float_values)

    return rounded_float_values

def append_to_csv(data):
    file_name = "../static/csv/hmi_data.csv"
    file_exists = False

    # Check if the file already exists
    try:
        with open(file_name, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass

    # Append data to CSV
    with open(file_name, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(labels)  # Write header if file doesn't exist
        writer.writerow(data)

def send_to_data_collector(data):
    """Send data to the local data collector"""
    try:
        url = "http://172.29.36.50/data"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"Data sent to local collector: {response.json()}")
            return True
        else:
            print(f"Failed to send to local collector: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error sending to local collector: {e}")
        return False

def send_to_external_server(data):
    """Send data to the external Flask server (fallback)"""
    try:
        url = "http://172.29.36.50/data"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=5)
        print(f"Data sent to external server: {response}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending to external server: {e}")
        return False

if __name__ == '__main__':
    sleep = 5

    while True:
        try:
            # Read Modbus data
            float_data = read_modbus_data()

            # Try to send to local data collector first
            local_success = send_to_data_collector(float_data)
            
            # If local collector fails, try external server as fallback
            if not local_success:
                print("Local collector unavailable, trying external server...")
                send_to_external_server(float_data)

            # Append data to CSV (keeping original functionality)
            append_to_csv(float_data)

            # Wait before repeating
            time.sleep(sleep)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(sleep)  # Wait before retrying