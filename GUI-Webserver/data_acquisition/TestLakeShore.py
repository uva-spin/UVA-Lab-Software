from _LakeShoreReader import LakeShoreReader
import time

lake_shore_reader = LakeShoreReader()

lake_shore_reader.data_stream()

while True:
    print(lake_shore_reader.get_latest_data())
    time.sleep(1)