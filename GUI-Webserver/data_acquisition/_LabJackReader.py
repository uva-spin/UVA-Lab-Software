import sys
import traceback
from datetime import datetime
import u3
from labjack import ljm
import numpy as np
import logging
import os
import threading
import csv
import time

logger = logging.getLogger(__name__)

class LabJackReader_1:

    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = [None, None, None, None, None, None]
        self.running = False
        self.thread = None
        self.device = None
        self.avg_Root_Exhausted_Pressure = None
        self.avg_Buffer_Pressure = None
        self.avg_Magnet_Pressure = None
        self.avg_Purifier_Inlet_Pressure = None
        self.avg_Fridge_Vapor_Pressure = None
        self.avg_Thermocouple = None

        self.ROOT_EXHAUST_SCALE_FACTOR = 0.7928388747 # Torr
        self.BUFFER_SCALE_FACTOR = 17.46031746 #PSI
        self.MAGNET_SCALE_FACTOR = 1 #PSI
        self.PURIFIER_INLET_SCALE_FACTOR = 1 #PSI
        self.FRIDGE_VAPOR_SCALE_FACTOR = 52.55102041 # Roughly in Torr

        self.FRIDGE_VAPOR_SHIFT =  -0.19

    def psi_to_torr(self, psi):
        return psi * 51.715 # 1 psi = 51.715 torr

    def start(self):
        """Start the labjack data reading thread"""
        try:
            self.device = u3.U3()
            self.device.configU3()
            self.device.getCalibrationData()
            self.device.configIO(FIOAnalog=127)  # 127 = 0x7F = 01111111 binary (enables FIO0-FIO6 as analog)  
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

            self.device.streamConfig(NumChannels=6, PChannels=[0, 1, 2, 3, 4, 6], NChannels=[31, 31, 31, 31, 31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)

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
                Thermocouple = np.zeros(MAX_REQUESTS)

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

                        if self._check_data(r["AIN6"]): ### Thermocouple
                            vOut_Thermocouple = sum(r["AIN6"]) / len(r["AIN6"])
                        else:
                            logger.warning(f"No data for Thermocouple at {datetime.now()}")

                        dataCount += 1
                        packetCount += r['numPackets']

                        Root_Exhausted_Pressure[i] = vOut_Root_Exhausted_Pressure
                        Buffer_Pressure[i] = vOut_Buffer_Pressure
                        Magnet_Pressure[i] = vOut_Magnet_Pressure
                        Purifier_Inlet_Pressure[i] = vOut_Purifier_Inlet_Pressure
                        Fridge_Vapor_Pressure[i] = vOut_Fridge_Vapor_Pressure
                        Thermocouple[i] = vOut_Thermocouple
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
                    self.avg_Thermocouple = np.average(Thermocouple)
                    self.data_queue[0] = self.psi_to_torr(self.ROOT_EXHAUST_SCALE_FACTOR * self.avg_Root_Exhausted_Pressure) ## In Torr
                    self.data_queue[1] = self.BUFFER_SCALE_FACTOR * self.avg_Buffer_Pressure ## In PSI
                    self.data_queue[2] = self.MAGNET_SCALE_FACTOR * self.avg_Magnet_Pressure ## In PSI
                    self.data_queue[3] = self.PURIFIER_INLET_SCALE_FACTOR * self.avg_Purifier_Inlet_Pressure ## In PSI
                    self.data_queue[4] = self.FRIDGE_VAPOR_SCALE_FACTOR * self.avg_Fridge_Vapor_Pressure + self.FRIDGE_VAPOR_SHIFT ## In Torr
                    self.data_queue[5] = self.avg_Thermocouple ## In C
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
            return [self.data_queue[0], self.data_queue[1], self.data_queue[2], self.data_queue[3], self.data_queue[4], self.data_queue[5]]
        except Exception as e:
            logger.error(f"Error getting latest labjack data: {e}")
            return [None] * 6
        


class LabJackReader_2:

    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = [None, None, None, None, None, None]
        self.running = False
        self.thread = None
        self.device = None
        self.avg_Flow_Meter_1 = None
        self.avg_Flow_Meter_2 = None

    def start(self):
        """Start the labjack data reading thread"""
        try:
            self.device = ljm.openS("T4", "ANY", "ANY")
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
                ljm.close(self.device)
                logger.info("LabJackReader: Device closed")
            except:
                pass
            self.device = None

    def _check_data(self, data):
        """ Check if the channels are getting data """
        if data is None:
            logger.warning(f"No data from channel at {datetime.now()}")
            return False
        # Handle both single values and arrays
        if isinstance(data, (list, np.ndarray)):
            if len(data) == 0:
                logger.warning(f"Empty data array from channel at {datetime.now()}")
                return False
        return True

    def _monitor_labjack(self):
        """Monitor the LabJack for new data and write to queue"""
        if not self.device:
            logger.error("LabJackReader: Device not initialized")
            return

        MAX_REQUESTS = 75

        try:
            logger.info("Reading from T4 AIN1 and AIN2 channels")

            Flow_Meter_1 = np.zeros(MAX_REQUESTS)
            Flow_Meter_2 = np.zeros(MAX_REQUESTS)
            dataCount = 0

            # Read data from AIN1 and AIN2
            for i in range(MAX_REQUESTS):
                if not self.running:
                    break

                try:
                    # Read AIN1 (Flow Meter 1)
                    vOut_Flow_Meter_1 = ljm.eReadName(self.device, "AIN1")
                    if self._check_data(vOut_Flow_Meter_1):
                        Flow_Meter_1[i] = vOut_Flow_Meter_1
                    else:
                        logger.warning(f"No data for Flow Meter 1 at {datetime.now()}")

                    # Read AIN2 (Flow Meter 2)
                    vOut_Flow_Meter_2 = ljm.eReadName(self.device, "AIN2")
                    if self._check_data(vOut_Flow_Meter_2):
                        Flow_Meter_2[i] = vOut_Flow_Meter_2
                    else:
                        logger.warning(f"No data for Flow Meter 2 at {datetime.now()}")

                    dataCount += 1
                    
                    # Small delay between readings
                    time.sleep(0.01)

                except Exception as e:
                    logger.error(f"Error reading channel data: {e}")
                    break

            if dataCount > 0:
                self.avg_Flow_Meter_1 = np.average(Flow_Meter_1[:dataCount])
                self.avg_Flow_Meter_2 = np.average(Flow_Meter_2[:dataCount])
                self.data_queue[0] = self.avg_Flow_Meter_1
                self.data_queue[1] = self.avg_Flow_Meter_2
                logger.info(f"Flow Meter 1 average: {self.avg_Flow_Meter_1}")
                logger.info(f"Flow Meter 2 average: {self.avg_Flow_Meter_2}")
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
            return [self.data_queue[0], self.data_queue[1]]
        except Exception as e:
            logger.error(f"Error getting latest labjack data: {e}")
            return [None] * 2