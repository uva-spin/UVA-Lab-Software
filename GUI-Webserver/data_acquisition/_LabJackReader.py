import sys
import traceback
from datetime import datetime
import u3
import numpy as np
import queue
import logging
import os
import threading
import csv
import time

logger = logging.getLogger(__name__)

class LabJackReader:

    def __init__(self, csv_path, check_interval=1):
        self.csv_path = csv_path
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None

    def start(self):
        """Start the labjack data reading thread"""
        self.running = True
        self.thread = threading.Thread(target=self.data_stream, daemon=True)
        self.thread.start()
        logger.info(f"LabJackReader: Data stream started")
        
    def stop(self):
        """Stop the labjack data reading thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            logger.info(f"LabJackReader: Data stream stopped")

    def _monitor_file(self):
        """Monitor the CSV file for new data"""

        # MAX_REQUESTS is the number of packets to be read.
        MAX_REQUESTS = 75
        # SCAN_FREQUENCY is the scan frequency of stream mode in Hz
        SCAN_FREQUENCY = 5000

        d = None
        # At high frequencies ( >5 kHz), the number of samples will be MAX_REQUESTS
        # times 48 (packets per request) times 25 (samples per packet).
        d = u3.U3()

        # To learn the if the U3 is an HV
        d.configU3()

        # For applying the proper calibration to readings.
        d.getCalibrationData()

        # Set the FIO0 and FIO1 to Analog (d3 = b00000011)
        d.configIO(FIOAnalog=3)

        print("Configuring U3 stream")
        d.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)
        if d is None:
            print("Configure a device first.")
            sys.exit(0)

        while self.running:
            try:
                if not os.path.exists(self.csv_path):
                    logger.warning(f"LabJackReader: CSV file not found: {self.csv_path}. Creating file...")
                    with open(self.csv_path, 'w') as file:
                        file.write("Timestamp,Pressure_1\n")
                    self.last_position = 0
                    continue

                try:
                    d.streamStart()
                    start = datetime.now()
                    print("Start time is %s" % start)

                    missed = 0
                    dataCount = 0
                    packetCount = 0
                    data_R2 = np.zeros(MAX_REQUESTS)

                    for i, r in enumerate(d.streamData()):
                        if r is not None:
                            if dataCount >= MAX_REQUESTS:
                                break

                            if r["errors"] != 0:
                                print("Errors counted: %s ; %s" % (r["errors"], datetime.now()))

                            if r["numPackets"] != d.packetsPerRequest:
                                print("----- UNDERFLOW : %s ; %s" %
                                    (r["numPackets"], datetime.now()))

                            if r["missed"] != 0:
                                missed += r['missed']
                                print("+++ Missed %s" % r["missed"])

                            vOut = sum(r["AIN0"]) / len(r["AIN0"])
                            vIn = 10
                            R1 = 100
                            R2 = R1*(1/((vIn/vOut)-1))

                            dataCount += 1
                            packetCount += r['numPackets']

                            data_R2[i] = R2
                        else:
                            # Got no data back from our read.
                            # This only happens if your stream isn't faster than the USB read
                            # timeout, ~1 sec.
                            print("No data ; %s" % datetime.now())
                except:
                    print("".join(i for i in traceback.format_exc()))
                finally:
                    stop = datetime.now()
                    self._to_csv(np.average(data_R2))
                    logger.info(f"LabJackReader: Data stream stopped")
                    d.streamStop()
                    logger.info(f"LabJackReader: Stream stopped")
                    d.close()
                    logger.info(f"LabJackReader: Device closed")
            except Exception as e:
                logger.error(f"LabJackReader: Error in monitor loop: {e}")
                time.sleep(self.check_interval)

    def _to_csv(self, data):
        """Write data to CSV file"""
        with open(self.csv_path, 'a', newline='') as file:
            writer = csv.writer(file)

            if file.tell() == 0:
                writer.writerow(["Timestamp", "Pressure_1"])

            writer.writerow([datetime.now(), data])

    def data_stream(self):
        """Read data from LabJack"""
        while self.running:
            self._monitor_file()
            time.sleep(self.check_interval) 

    def get_latest_data(self):
        """Get the latest data from the data queue"""
        return self.data_queue.get()