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
        self.device = None

    def start(self):
        """Start the labjack data reading thread"""
        try:
            # Initialize device once
            self.device = u3.U3()
            self.device.configU3()
            self.device.getCalibrationData()
            self.device.configIO(FIOAnalog=3)
            logger.info("LabJackReader: Device initialized")
            
            self.running = True
            self.thread = threading.Thread(target=self.data_stream, daemon=True)
            self.thread.start()
            logger.info(f"LabJackReader: Data stream started")
        except Exception as e:
            logger.error(f"LabJackReader: Error during start: {e}")
            if self.device:
                try:
                    self.device.close()
                except:
                    pass
            raise
        
    def stop(self):
        """Stop the labjack data reading thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            logger.info(f"LabJackReader: Data stream stopped")
        
        if self.device:
            try:
                self.device.streamStop()
                self.device.close()
                logger.info("LabJackReader: Device closed")
            except:
                pass
            self.device = None

    def _monitor_file(self):
        """Monitor the CSV file for new data"""
        if not self.device:
            logger.error("LabJackReader: Device not initialized")
            return

        # MAX_REQUESTS is the number of packets to be read.
        MAX_REQUESTS = 75
        # SCAN_FREQUENCY is the scan frequency of stream mode in Hz
        SCAN_FREQUENCY = 5000

        try:
            if not os.path.exists(self.csv_path):
                logger.warning(f"LabJackReader: CSV file not found: {self.csv_path}. Creating file...")
                with open(self.csv_path, 'w') as file:
                    file.write("Timestamp,Pressure_1\n")
                self.last_position = 0
                return

            logger.info("Configuring U3 stream")
            self.device.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)

            try:
                self.device.streamStart()
                start = datetime.now()
                logger.info(f"Stream started at {start}")

                missed = 0
                dataCount = 0
                packetCount = 0
                data_R2 = np.zeros(MAX_REQUESTS)

                for i, r in enumerate(self.device.streamData()):
                    if not self.running:
                        break

                    if r is not None:
                        if dataCount >= MAX_REQUESTS:
                            break

                        if r["errors"] != 0:
                            logger.warning(f"Errors counted: {r['errors']} at {datetime.now()}")

                        if r["numPackets"] != self.device.packetsPerRequest:
                            logger.warning(f"UNDERFLOW: {r['numPackets']} at {datetime.now()}")

                        if r["missed"] != 0:
                            missed += r['missed']
                            logger.warning(f"Missed {r['missed']} packets")

                        vOut = sum(r["AIN0"]) / len(r["AIN0"])
                        vIn = 10
                        R1 = 100
                        R2 = R1*(1/((vIn/vOut)-1))

                        dataCount += 1
                        packetCount += r['numPackets']

                        data_R2[i] = R2
                    else:
                        logger.warning(f"No data at {datetime.now()}")

            finally:
                try:
                    if self.device:
                        self.device.streamStop()
                        logger.info("Stream stopped cleanly")
                except Exception as e:
                    logger.error(f"Error stopping stream: {e}")

                if dataCount > 0:
                    self._to_csv(np.average(data_R2))
                    logger.info(f"Data written to CSV, average R2: {np.average(data_R2)}")

        except Exception as e:
            logger.error(f"LabJackReader: Error in monitor loop: {e}")
            # Don't sleep here, let the data_stream method handle the delay

    def _to_csv(self, data):
        """Write data to CSV file"""
        try:
            with open(self.csv_path, 'a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(["Timestamp", "Pressure_1"])
                writer.writerow([datetime.now(), data])
        except Exception as e:
            logger.error(f"Error writing to CSV: {e}")

    def data_stream(self):
        """Read data from LabJack"""
        while self.running:
            try:
                self._monitor_file()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in data stream: {e}")
                time.sleep(self.check_interval)

    def get_latest_data(self):
        """Get the latest data from the data queue"""
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None