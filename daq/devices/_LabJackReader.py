import sys
import traceback
from datetime import datetime
import u3
from labjack import ljm
import numpy as np
import logging
import os
import csv
import time
import asyncio
import mariadb
import pytz


class LabJackReader_1:




    def __init__(self, check_interval=1, connection_pool=None):
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = [None, None, None, None, None, None]
        self.running = False
        self.device = None
        self.avg_Root_Exhausted_Pressure = None
        self.avg_Buffer_Pressure = None
        self.avg_Magnet_Pressure = None
        self.avg_Purifier_Inlet_Pressure = None
        self.avg_Fridge_Vapor_Pressure = None
        self.avg_Thermocouple = None

        # self.ROOT_EXHAUST_SCALE_FACTOR = 0.7928388747 # Torr
        self.ROOT_EXHAUST_SCALE_FACTOR = 4.284
        self.BUFFER_SCALE_FACTOR = 20.356 #PSI
        self.MAGNET_SCALE_FACTOR = 3.726 #PSI
        self.PURIFIER_INLET_SCALE_FACTOR = 1 #PSI
        self.FRIDGE_VAPOR_SCALE_FACTOR = 52.55102041 # Roughly in Torr

        self.ROOT_EXHAUST_SHIFT = -807.446
        self.BUFFER_SHIFT = 0.043
        self.MAGNET_SHIFT = -3.682
        self.PURIFIER_INLET_SHIFT = 0.015
        self.FRIDGE_VAPOR_SHIFT = 0.023
        
        self.connection_pool = connection_pool
        self.EST = pytz.timezone('America/New_York')

        self.logger = logging.getLogger("LabJack_1")
        

    def psi_to_torr(self, psi):
        return psi * 51.715 # 1 psi = 51.715 torr

    def start(self):
        """Start the labjack data reading"""
        try:
            self.device = u3.U3()
            self.device.configU3()
            self.device.getCalibrationData()
            self.device.configIO(FIOAnalog=127)  # 127 = 0x7F = 01111111 binary (enables FIO0-FIO6 as analog)  
            self.logger.info("LabJackReader: Device initialized")
            
            self.running = True
            self.logger.info(f"LabJackReader: Device started")
        except Exception as e:
            self.logger.error(f"LabJackReader: Error during start: {e}")
            if self.device:
                try:
                    self.device.close()
                except:
                    pass
            raise
        
    def stop(self):
        """Stop the labjack data reading"""
        self.running = False
        
        if self.device:
            try:
                self.device.streamStop()
                self.device.close()
                self.logger.info("LabJackReader: Device closed")
            except:
                pass
            self.device = None

    def _check_data(self, data):
        """ Check if the channels are getting data """
        if data is None or len(data) == 0:
            self.logger.warning(f"No data from Labjack 1 channel at {datetime.now()}")
            return False
        return True

    def _monitor_labjack(self):
        """Monitor the LabJack for new data and write to queue"""
        if not self.device:
            self.logger.error("LabJackReader: Device not initialized")
            return

        # MAX_REQUESTS is the number of packets to be read.
        MAX_REQUESTS = 75
        # SCAN_FREQUENCY is the scan frequency of stream mode in Hz
        SCAN_FREQUENCY = 5000
        


        try:
            self.logger.info("Configuring U3 stream")

            self.device.streamConfig(NumChannels=6, PChannels=[0, 1, 2, 3, 4, 6], NChannels=[31, 31, 31, 31, 31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)

            try:
                self.device.streamStart()
                start = datetime.now()
                self.logger.info(f"Stream started at {start}")

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
                            self.logger.warning(f"Errors counted: {r['errors']} at {datetime.now()}")

                        if r["numPackets"] != self.device.packetsPerRequest:
                            self.logger.warning(f"UNDERFLOW: {r['numPackets']} at {datetime.now()}")

                        if r["missed"] != 0:
                            missed += r['missed']
                            self.logger.warning(f"Missed {r['missed']} packets")

                        # Process AIN0 (Pressure 1)
                        if self._check_data(r["AIN0"]): ### Root Exhaust Pressure
                            vOut_Root_Exhausted_Pressure = sum(r["AIN0"]) / len(r["AIN0"])
                        else:
                            self.logger.warning(f"No data for Root Exhaust Pressure Transducer at {datetime.now()}")

                        # Process AIN1 (Pressure 2)
                        if self._check_data(r["AIN1"]): ### Buffer Pressure
                            vOut_Buffer_Pressure = sum(r["AIN1"]) / len(r["AIN1"])
                        else:
                            self.logger.warning(f"No data for Buffer Pressure Transducer at {datetime.now()}")

                        # Process AIN2 (Pressure 3)
                        if self._check_data(r["AIN2"]): ### Magnet Pressure
                            vOut_Magnet_Pressure = sum(r["AIN2"]) / len(r["AIN2"])
                        else:
                            self.logger.warning(f"No data for Magnet Pressure Transducer at {datetime.now()}")

                        if self._check_data(r["AIN3"]): ### Purifier Inlet Pressure
                            vOut_Purifier_Inlet_Pressure = sum(r["AIN3"]) / len(r["AIN3"])
                        else:
                            self.logger.warning(f"No data for Magnet Pressure Transducer at {datetime.now()}")

                        if self._check_data(r["AIN4"]): ### Fridge Vapor Pressure
                            vOut_Fridge_Vapor_Pressure = sum(r["AIN4"]) / len(r["AIN4"])
                        else:
                            self.logger.warning(f"No data for Fridge Vapor Pressure at {datetime.now()}")

                        if self._check_data(r["AIN6"]): ### Thermocouple
                            vOut_Thermocouple = sum(r["AIN6"]) / len(r["AIN6"])
                        else:
                            self.logger.warning(f"No data for Thermocouple at {datetime.now()}")

                        dataCount += 1
                        packetCount += r['numPackets']

                        Root_Exhausted_Pressure[i] = vOut_Root_Exhausted_Pressure
                        Buffer_Pressure[i] = vOut_Buffer_Pressure
                        Magnet_Pressure[i] = vOut_Magnet_Pressure
                        Purifier_Inlet_Pressure[i] = vOut_Purifier_Inlet_Pressure
                        Fridge_Vapor_Pressure[i] = vOut_Fridge_Vapor_Pressure
                        Thermocouple[i] = vOut_Thermocouple
                    else:
                        self.logger.warning(f"No data at {datetime.now()}")

            finally:
                try:
                    if self.device:
                        self.device.streamStop()
                        self.logger.info("Stream stopped cleanly")
                except Exception as e:
                    self.logger.error(f"Error stopping stream: {e}")

                if dataCount > 0:
                    self.avg_Root_Exhausted_Pressure = np.average(Root_Exhausted_Pressure)
                    self.avg_Buffer_Pressure = np.average(Buffer_Pressure)
                    self.avg_Magnet_Pressure = np.average(Magnet_Pressure)
                    self.avg_Purifier_Inlet_Pressure = np.average(Purifier_Inlet_Pressure)
                    self.avg_Fridge_Vapor_Pressure = np.average(Fridge_Vapor_Pressure)
                    self.avg_Thermocouple = np.average(Thermocouple)
                    self.data_queue[0] = self.psi_to_torr(self.ROOT_EXHAUST_SCALE_FACTOR * self.avg_Root_Exhausted_Pressure + self.ROOT_EXHAUST_SHIFT) ## In Torr
                    self.data_queue[1] = self.BUFFER_SCALE_FACTOR * self.avg_Buffer_Pressure - 4.22 ## In PSI
                    self.data_queue[2] = self.MAGNET_SCALE_FACTOR * self.avg_Magnet_Pressure + self.MAGNET_SHIFT ## In PSI
                    self.data_queue[3] = self.PURIFIER_INLET_SCALE_FACTOR * self.avg_Purifier_Inlet_Pressure ## In PSI
                    self.data_queue[4] = self.FRIDGE_VAPOR_SCALE_FACTOR * self.avg_Fridge_Vapor_Pressure + self.FRIDGE_VAPOR_SHIFT ## In Torr
                    self.data_queue[5] = self.avg_Thermocouple ## In C
        except Exception as e:
            self.logger.error(f"LabJackReader: Error in monitor loop: {e}")

    def read_data(self):
        """Read data from LabJack"""
        if not self.running:
            self.logger.error("Cannot read data - device not started")
            return False
            
        try:
            self._monitor_labjack()
            return True
        except Exception as e:
            self.logger.error(f"Error reading data: {e}")
            return False

    def get_latest_data(self):
        """Get the latest data from the data queue"""
        try:
            return [self.data_queue[0], self.data_queue[1], self.data_queue[2], self.data_queue[3], self.data_queue[4], self.data_queue[5]]
        except Exception as e:
            self.logger.error(f"Error getting latest labjack data: {e}")
            return [None] * 6

    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def insert_labjack_1_data(self, pressure_data):
        """Insert LabJack data into the pressures table"""
        timestamp = await self.get_current_est_time()
        await asyncio.sleep(0.1)  # Small delay for async operations
        return self._insert_labjack_1_data_sync(pressure_data, timestamp)

    def _insert_labjack_1_data_sync(self, pressure_data, timestamp):
        """Synchronous function to insert LabJack data into the pressures table"""
        if not self.connection_pool:
            self.logger.warning("No database connection pool available")
            return False
            
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            if pressure_data and len(pressure_data) >= 6:
                cursor.execute(
                    """INSERT INTO pressures (timestamp, root_exhaust_pressure, buffer_pressure, 
                       magnet_pressure, purifier_inlet_pressure, fridge_vapor_pressure, thermocouple) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (timestamp, pressure_data[0], pressure_data[1], pressure_data[2], 
                     pressure_data[3], pressure_data[4], pressure_data[5])
                )
                conn.commit()
                self.logger.debug(f"LabJack 1 data inserted: {pressure_data}")
                return True
            else:
                self.logger.warning("LabJack 1 data is invalid, skipping insertion")
                return False
                
        except Exception as e:
            self.logger.error(f"Error inserting LabJack 1 data: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def set_connection_pool(self, connection_pool):
        """Set the database connection pool"""
        self.connection_pool = connection_pool

    async def pipeline_data(self):
        """Pipeline method: read data and insert into database"""
        try:
            # Read data from LabJack device
            data = self.get_latest_data()
            
            # Insert data into database if available
            if data is not None and self.connection_pool:
                await self.insert_labjack_1_data(data)
                return True
            else:
                self.logger.warning("No data to pipeline or no connection pool available")
                return False
        except Exception as e:
            self.logger.error(f"Error in LabJack 1 data pipeline: {e}")
            return False
        


class LabJackReader_2:

    def __init__(self, check_interval=1, connection_pool=None):
        self.check_interval = check_interval
        self.last_position = 0
        self.data_queue = [None, None, None, None]
        self.running = False
        self.device = None
        self.avg_Flow_Meter_1 = None
        self.avg_Flow_Meter_2 = None
        self.avg_magnet_bottom_temperature = None
        self.avg_magnet_top_temperature = None
        self.connection_pool = connection_pool
        self.EST = pytz.timezone('America/New_York')

        self.logger = logging.getLogger("LabJack_2")
        

    def start(self):
        """Start the labjack data reading"""
        try:
            self.device = ljm.openS("T4", "ANY", "ANY")
            self.logger.info("LabJackReader: Device initialized")
            
            self.running = True
            self.logger.info(f"LabJackReader: Device started")
        except Exception as e:
            self.logger.error(f"LabJackReader: Error during start: {e}")
            if self.device:
                try:
                    self.device.close()
                except:
                    pass
            raise
        
    def stop(self):
        """Stop the labjack data reading"""
        self.running = False
        
        if self.device:
            try:
                ljm.close(self.device)
                self.logger.info("LabJackReader: Device closed")
            except:
                pass
            self.device = None

    def _check_data(self, data):
        """ Check if the channels are getting data """
        if data is None:
            self.logger.warning(f"No data from Labjack 2 channel at {datetime.now()}")
            return False
        # Handle both single values and arrays
        if isinstance(data, (list, np.ndarray)):
            if len(data) == 0:
                self.logger.warning(f"Empty data array from Labjack 2 channel at {datetime.now()}")
                return False
        return True

    def _monitor_labjack(self):
        """Monitor the LabJack for new data and write to queue"""
        if not self.device:
            self.logger.error("LabJackReader: Device not initialized")
            return

        MAX_REQUESTS = 75
        SCAN_FREQUENCY = 5000

        # Flow Meter 1
        vIn = 2.5 # V
        RLoad = 1000 # Ohms

        # Flow Meter 2
        
        vIn = 2.5 # V
        RLoad = 1000 # Ohms

        try:
            self.logger.info("Reading from T4 AIN1 and AIN2 channels")

            Flow_Meter_1 = np.zeros(MAX_REQUESTS)
            Flow_Meter_2 = np.zeros(MAX_REQUESTS)
            Magnet_Bottom_Temperature = np.zeros(MAX_REQUESTS)
            Magnet_Top_Temperature = np.zeros(MAX_REQUESTS)
            dataCount = 0

            # Read data from AIN1 and AIN2
            for i in range(MAX_REQUESTS):
                if not self.running:
                    break

                try:
                    # Read AIN1 (Microwave Flow Meter)
                    vOut_Microwave_Flow_Meter = ljm.eReadName(self.device, "AIN1")
                    if self._check_data(vOut_Microwave_Flow_Meter):
                        Flow_Meter_1[i] = vOut_Microwave_Flow_Meter
                    else:
                        self.logger.warning(f"No data for Flow Meter 1 at {datetime.now()}")

                    # Read AIN2 (Heat Exchanger Flow Meter)
                    vOut_Heat_Exchanger_Flow_Meter = ljm.eReadName(self.device, "AIN2")
                    if self._check_data(vOut_Heat_Exchanger_Flow_Meter):
                        Flow_Meter_2[i] = vOut_Heat_Exchanger_Flow_Meter
                    else:
                        self.logger.warning(f"No data for Flow Meter 2 at {datetime.now()}")

                    vOut_Magnet_Bottom_Temperature = ljm.eReadName(self.device, "AIN4")
                    if self._check_data(vOut_Magnet_Bottom_Temperature):
                        Magnet_Bottom_Temperature[i] = RLoad * ((vIn / vOut_Magnet_Bottom_Temperature) - 1)
                    else:
                        self.logger.warning(f"No data for Magnet Bottom Temperature at {datetime.now()}")

                    vOut_Magnet_Top_Temperature = ljm.eReadName(self.device, "AIN5")
                    if self._check_data(vOut_Magnet_Top_Temperature):
                        Magnet_Top_Temperature[i] = RLoad * ((vIn / vOut_Magnet_Top_Temperature) - 1)
                    else:
                        self.logger.warning(f"No data for Magnet Top Temperature at {datetime.now()}")
                        

                    dataCount += 1
                    
                    # Small delay between readings
                    time.sleep(0.01)

                except Exception as e:
                    self.logger.error(f"Error reading channel data: {e}")
                    break

            if dataCount > 0:
                self.avg_Microwave_Flow_Meter = np.average(Flow_Meter_1[:dataCount])
                self.avg_Heat_Exchanger_Flow_Meter = np.average(Flow_Meter_2[:dataCount])
                self.avg_Magnet_Bottom_Temperature = np.average(Magnet_Bottom_Temperature[:dataCount])
                self.avg_Magnet_Top_Temperature = np.average(Magnet_Top_Temperature[:dataCount])
                self.data_queue[0] = self.avg_Microwave_Flow_Meter - 10.650 # slm 
                self.data_queue[1] = self.avg_Heat_Exchanger_Flow_Meter # slm
                self.data_queue[2] = self.avg_Magnet_Bottom_Temperature # C
                self.data_queue[3] = self.avg_Magnet_Top_Temperature # C
                self.logger.info(f"Flow Meter 1 average: {self.avg_Flow_Meter_1}")
                self.logger.info(f"Flow Meter 2 average: {self.avg_Flow_Meter_2}")
        except Exception as e:
            self.logger.error(f"LabJackReader: Error in monitor loop: {e}")
    def read_data(self):
        """Read data from LabJack"""
        if not self.running:
            self.logger.error("Cannot read data - device not started")
            return False
            
        try:
            self._monitor_labjack()
            return True
        except Exception as e:
            self.logger.error(f"Error reading data: {e}")
            return False

    def get_latest_data(self):
        """Get the latest data from the data queue"""
        try:
            return [self.data_queue[0], self.data_queue[1], self.data_queue[2], self.data_queue[3]]
        except Exception as e:
            self.logger.error(f"Error getting latest labjack data: {e}")
            return [None] * 4

    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def insert_labjack_2_data(self, labjack_2_data):
        """Insert LabJack 2 data into the Flow_Rates table"""
        await asyncio.sleep(0.1)  # Small delay for async operations
        return self._insert_labjack_2_data_sync(labjack_2_data)

    def _insert_labjack_2_data_sync(self, labjack_2_data):
        """Synchronous function to insert LabJack 2 data into the Flow_Rates table"""
        if not self.connection_pool:
            self.logger.warning("No database connection pool available")
            return False
            
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            if labjack_2_data and len(labjack_2_data) >= 4:
                cursor.execute(
                    """INSERT INTO Flow_Rates (timestamp, microwave_flow_meter, heat_exchanger_flow_meter, 
                       magnet_bottom_temperature, magnet_top_temperature) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (datetime.now(self.EST), labjack_2_data[0], labjack_2_data[1], 
                     labjack_2_data[2], labjack_2_data[3])
                )
                conn.commit()
                self.logger.debug(f"LabJack 2 data inserted: {labjack_2_data}")
                return True
            else:
                self.logger.warning("LabJack 2 data is invalid, skipping insertion")
                return False
                
        except Exception as e:
            self.logger.error(f"Error inserting LabJack 2 data: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def set_connection_pool(self, connection_pool):
        """Set the database connection pool"""
        self.connection_pool = connection_pool