import csv
from datetime import datetime
import random
import time
import os

# Configuration
CSV_FILE = '../static/csv/Test_data.csv'
INTERVAL_SECONDS = 60

def append_data():
    # Generate data
    timestamp = datetime.now().isoformat()
    r2_value = round(random.uniform(0, 200), 2)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(CSV_FILE)
    
    # Append data to CSV
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'R2'])
        writer.writerow([timestamp, r2_value])

if __name__ == '__main__':
    try:
        while True:
            append_data()
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nScript stopped by user")