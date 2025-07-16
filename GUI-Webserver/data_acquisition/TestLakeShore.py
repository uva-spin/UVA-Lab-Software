from _LakeShoreReader import LakeShoreReader
import time

reader = LakeShoreReader(port="COM4")
reader.start()
reader.data_stream()
time.sleep(2)
data = reader.get_latest_data()
print(data)