from _MaxiGaugeReader import MaxiGaugeReader
import time

maxigauge_reader = MaxiGaugeReader()
maxigauge_reader.start()

try:
    while True:
        data = maxigauge_reader.get_latest_data()
        print(f"MaxiGauge data: {data}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping MaxiGauge reader...")
    maxigauge_reader.stop()


