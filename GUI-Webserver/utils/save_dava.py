import time
import csv
from LabJack_Reader import get_r_value  # Assuming the function is imported from LabJack_Reader

# Define the full network path where the CSV file will be saved
csv_file = r'\\172.29.36.50\share\code_for_monitoring\static\csv\r_values.csv'

while True:
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(['Timestamp', 'R2 Value'])

        # Get the R2 value from the get_r_value function
        r2_value = round(get_r_value(),2)
        print(r2_value)
        
        # Get the current timestamp
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Write the timestamp and R2 value to the CSV file
        writer.writerow([timestamp, r2_value])
        
    # Wait for 1 seconds before the next reading
    time.sleep(1)
