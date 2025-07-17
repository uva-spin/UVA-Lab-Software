from _LakeShoreReader import LakeShoreReader
import time

reader = LakeShoreReader(port="COM4")

try:
    reader.start()
    reader.data_stream()
    time.sleep(2)
    data, raw_data = reader.get_latest_data()
    print(f"Raw data: {raw_data}")
    print(f"Data: {data}")

except KeyboardInterrupt:
    print("Stopping LakeShore reader...")
    reader.stop()


