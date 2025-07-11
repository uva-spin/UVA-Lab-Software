import sys
import traceback
from datetime import datetime
import u3
import numpy as np
import logging
import os
import threading
import csv
import time

logger = logging.getLogger(__name__)

class LabJackReader:

    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = [None, None, None, None, None]
        self.running = False
        self.thread = None
        self.device = None
        self.avg_Root_Exhausted_Pressure = None
        self.avg_Buffer_Pressure = None
        self.avg_Magnet_Pressure = None
        self.avg_Purifier_Inlet_Pressure = None
        self.avg_Fridge_Vapor_Pressure = None

    def start(self):
        """Start the labjack data reading thread"""
        try:
            # Initialize device once
            self.device = u3.U3()
            self.device.configU3()
            self.device.getCalibrationData()
            # Configure FIO0-FIO4 as analog inputs
            self.device.configIO(FIOAnalog=31)  # 31 = 11111 in binary, enables FIO0-FIO4 as analog
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

    def _monitor_labjack(self):
        """Monitor the LabJack for new data and write to queue"""
        if not self.device:
            logger.error("LabJackReader: Device not initialized")
            return

        # MAX_REQUESTS is the number of packets to be read.
        MAX_REQUESTS = 75
        # SCAN_FREQUENCY is the scan frequency of stream mode in Hz
        SCAN_FREQUENCY = 5000

        try:
            logger.info("Configuring U3 stream")
            # Configure stream for 4 channels: AIN0, AIN1, AIN2, AIN3, 
            self.device.streamConfig(NumChannels=5, PChannels=[0, 1, 2, 3, 4], NChannels=[31, 31, 31, 31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)

            try:
                self.device.streamStart()
                start = datetime.now()
                logger.info(f"Stream started at {start}")

                missed = 0
                dataCount = 0
                packetCount = 0

                Root_Exhausted_Pressure = np.zeros(MAX_REQUESTS)
                Buffer_Pressure = np.zeros(MAX_REQUESTS)
                Magnet_Pressure = np.zeros(MAX_REQUESTS)
                Purifier_Inlet_Pressure = np.zeros(MAX_REQUESTS)
                Fridge_Vapor_Pressure = np.zeros(MAX_REQUESTS)

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
                        if self._check_data(r["AIN0"]): ### Root Exhaust Pressure
                            vOut_Root_Exhausted_Pressure = sum(r["AIN0"]) / len(r["AIN0"])
                        else:
                            logger.warning(f"No data for Root Exhaust Pressure Transducer at {datetime.now()}")

                        # Process AIN1 (Pressure 2)
                        if self._check_data(r["AIN1"]): ### Buffer Pressure
                            vOut_Buffer_Pressure = sum(r["AIN1"]) / len(r["AIN1"])
                        else:
                            logger.warning(f"No data for Buffer Pressure Transducer at {datetime.now()}")

                        # Process AIN2 (Pressure 3)
                        if self._check_data(r["AIN2"]): ### Magnet Pressure
                            vOut_Magnet_Pressure = sum(r["AIN2"]) / len(r["AIN2"])
                        else:
                            logger.warning(f"No data for Magnet Pressure Transducer at {datetime.now()}")

                        if self._check_data(r["AIN3"]): ### Purifier Inlet Pressure
                            vOut_Purifier_Inlet_Pressure = sum(r["AIN3"]) / len(r["AIN3"])
                        else:
                            logger.warning(f"No data for Magnet Pressure Transducer at {datetime.now()}")

                        if self._check_data(r["AIN4"]): ### Fridge Vapor Pressure
                            vOut_Fridge_Vapor_Pressure = sum(r["AIN4"]) / len(r["AIN4"])
                        else:
                            logger.warning(f"No data for Fridge Vapor Pressure at {datetime.now()}")
                            

                        dataCount += 1
                        packetCount += r['numPackets']

                        Root_Exhausted_Pressure[i] = vOut_Root_Exhausted_Pressure
                        Buffer_Pressure[i] = vOut_Buffer_Pressure
                        Magnet_Pressure[i] = vOut_Magnet_Pressure
                        Purifier_Inlet_Pressure[i] = vOut_Purifier_Inlet_Pressure
                        Fridge_Vapor_Pressure[i] = vOut_Fridge_Vapor_Pressure
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
                    self.avg_Root_Exhausted_Pressure = np.average(Root_Exhausted_Pressure)
                    self.avg_Buffer_Pressure = np.average(Buffer_Pressure)
                    self.avg_Magnet_Pressure = np.average(Magnet_Pressure)
                    self.avg_Purifier_Inlet_Pressure = np.average(Purifier_Inlet_Pressure)
                    self.avg_Fridge_Vapor_Pressure = np.average(Fridge_Vapor_Pressure)
                    self.data_queue[0] = self.avg_Root_Exhausted_Pressure
                    self.data_queue[1] = self.avg_Buffer_Pressure
                    self.data_queue[2] = self.avg_Magnet_Pressure
                    self.data_queue[3] = self.avg_Purifier_Inlet_Pressure
                    self.data_queue[4] = self.avg_Fridge_Vapor_Pressure
                    # logger.info(f"Data written to queue, average R2 - Pressure 1: {self.avg_Root_Exhausted_Pressure}, Pressure 2: {self.avg_Buffer_Pressure}, Pressure 3: {self.avg_Magnet_Pressure}, Pressure 4: {self.avg_Purifier_Inlet_Pressure}, Fridge Vapor Pressure: {self.avg_Fridge_Vapor_Pressure}")
        except Exception as e:
            logger.error(f"LabJackReader: Error in monitor loop: {e}")
            # Don't sleep here, let the data_stream method handle the delay



    def data_stream(self):
        """Read data from LabJack"""
        while self.running:
            try:
                self._monitor_labjack()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in data stream: {e}")      
                time.sleep(self.check_interval)

    def get_latest_data(self):
        """Get the latest data from the data queue"""
        try:
            # logger.info(f"Getting latest Pressure data from queue")
            # print(f"DEBUG: Pressure data: {self.data_queue[0]}, {self.data_queue[1]}, {self.data_queue[2]}, {self.data_queue[3]}, {self.data_queue[4]}")
            return [self.data_queue[0], self.data_queue[1], self.data_queue[2], self.data_queue[3], self.data_queue[4]]
        except Exception as e:
            logger.error(f"Error getting latest labjack data: {e}")
            return [None] * 5