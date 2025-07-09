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
        self.avg_pressure1 = None
        self.avg_pressure2 = None
        self.avg_pressure3 = None

    def start(self):
        """Start the labjack data reading thread"""
        try:
            # Initialize device once
            self.device = u3.U3()
            self.device.configU3()
            self.device.getCalibrationData()
            # Configure FIO0, FIO1, and FIO2 as analog inputs
            self.device.configIO(FIOAnalog=7)  # 7 = 111 in binary, enables FIO0, FIO1, FIO2 as analog
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

    def _check_data(self, data):
        """ Check if the channels are getting data """
        if data is None or len(data) == 0:
            logger.warning(f"No data from channel at {datetime.now()}")
            return False
        return True

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
                    file.write("Timestamp,Pressure_1,Pressure_2,Pressure_3\n")
                self.last_position = 0
                return

            logger.info("Configuring U3 stream")
            # Configure stream for 3 channels: AIN0, AIN1, AIN2
            self.device.streamConfig(NumChannels=3, PChannels=[0, 1, 2], NChannels=[31, 31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)

            try:
                self.device.streamStart()
                start = datetime.now()
                logger.info(f"Stream started at {start}")

                missed = 0
                dataCount = 0
                packetCount = 0
                data_R2_pressure1 = np.zeros(MAX_REQUESTS)
                data_R2_pressure2 = np.zeros(MAX_REQUESTS)
                data_R2_pressure3 = np.zeros(MAX_REQUESTS)

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

                        # Process AIN0 (Pressure 1)
                        if self._check_data(r["AIN0"]):
                            vOut_pressure1 = sum(r["AIN0"]) / len(r["AIN0"])
                            vIn = 10
                            R1 = 100
                            R2_pressure1 = R1*(1/((vIn/vOut_pressure1)-1))
                        else:
                            R2_pressure1 = None
                            logger.warning(f"No data for Pressure 1 at {datetime.now()}")

                        # Process AIN1 (Pressure 2)
                        if self._check_data(r["AIN1"]):
                            vOut_pressure2 = sum(r["AIN1"]) / len(r["AIN1"])
                            R2_pressure2 = R1*(1/((vIn/vOut_pressure2)-1))
                        else:
                            R2_pressure2 = None
                            logger.warning(f"No data for Pressure 2 at {datetime.now()}")

                        # Process AIN2 (Pressure 3)
                        if self._check_data(r["AIN2"]):
                            vOut_pressure3 = sum(r["AIN2"]) / len(r["AIN2"])
                            R2_pressure3 = R1*(1/((vIn/vOut_pressure3)-1))
                        else:
                            R2_pressure3 = None
                            logger.warning(f"No data for Pressure 3 at {datetime.now()}")

                        dataCount += 1
                        packetCount += r['numPackets']

                        data_R2_pressure1[i] = R2_pressure1
                        data_R2_pressure2[i] = R2_pressure2
                        data_R2_pressure3[i] = R2_pressure3
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
                    avg_pressure1 = np.average(data_R2_pressure1)
                    avg_pressure2 = np.average(data_R2_pressure2)
                    avg_pressure3 = np.average(data_R2_pressure3)
                    self.avg_pressure1 = avg_pressure1
                    self.avg_pressure2 = avg_pressure2
                    self.avg_pressure3 = avg_pressure3
                    self.data_queue.put([avg_pressure1, avg_pressure2, avg_pressure3])
                    logger.info(f"Data written to queue, average R2 - Pressure 1: {avg_pressure1}, Pressure 2: {avg_pressure2}, Pressure 3: {avg_pressure3}")
        except Exception as e:
            logger.error(f"LabJackReader: Error in monitor loop: {e}")
            # Don't sleep here, let the data_stream method handle the delay



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
            logger.info(f"Getting latest Pressure data from queue")
            print(f"DEBUG: Pressure data queue size: {self.data_queue.qsize()}")
            print(f"DEBUG: Pressure data queue: {self.data_queue.get_nowait()}")
            return self.data_queue.get_nowait()
        except queue.Empty:
            logger.warning("No data in queue. Returning None values instead...")
            return [None] * 3