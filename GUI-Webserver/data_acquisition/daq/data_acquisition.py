"""
Data Acquisition System Module
This module provides a clean interface for data acquisition operations.
"""

import asyncio
import logging
import json
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

import pytz
import mariadb

from config import *
from _TeledyneReader import TeledyneDataReader
from _LabJackReader import LabJackReader_1, LabJackReader_2
from _LakeShoreReader import LakeShoreReader
from _MaxiGaugeReader import MaxiGaugeReader
from _IVCReader import IVCReader
from _QTReader import QTReader


class DataAcquisitionSystem:
    """
    Main data acquisition system class that manages all data acquisition operations.
    """
    
    def __init__(self):
        """Initialize the data acquisition system"""
        self.logger = logging.getLogger(__name__)
        self.EST = pytz.timezone('America/New_York')
        self.shutdown_event = asyncio.Event()
        
        # Load database configuration
        self.db_config = self._load_database_config()
        
        # Database connection pool
        self.connection_pool = None
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _load_database_config(self) -> Dict[str, Any]:
        """Load database configuration from file"""
        try:
            with open(DATABASE_FILE, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Database configuration loaded: {config}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load database configuration: {e}")
            raise
    
    def _initialize_data_sources(self):
        """Initialize all data source classes"""
        try:
            # Initialize QT Reader
            self.qt_reader = QTReader()
            self.logger.info("QT Reader initialized")
            
            # Initialize Teledyne Reader
            self.teledyne_reader = TeledyneDataReader()
            self.logger.info("Teledyne Reader initialized")
            
            # Initialize LabJack Readers
            self.labjack_reader_1 = LabJackReader_1()
            self.labjack_reader_2 = LabJackReader_2()
            self.logger.info("LabJack Readers initialized")
            
            # Initialize LakeShore Readers with specific table names
            self.lakeshore_reader_target_stick = LakeShoreReader(port="COM4", table_name="lakeshore_target_stick")
            self.lakeshore_reader_fridge_temp = LakeShoreReader(port="COM5", table_name="lakeshore_fridge_temp")
            self.lakeshore_reader_magnet_temp = LakeShoreReader(port="COM6", table_name="lakeshore_magnet_temp")
            self.logger.info("LakeShore Readers initialized")
            
            # Initialize MaxiGauge Reader
            self.maxigauge_reader = MaxiGaugeReader()
            self.logger.info("MaxiGauge Reader initialized")
            
            # Initialize IVC Reader
            self.ivc_reader = IVCReader()
            self.logger.info("IVC Reader initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize data sources: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Shutdown signal received: {signum}")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _create_connection_pool(self):
        """Create database connection pool"""
        try:
            self.connection_pool = mariadb.ConnectionPool(**self.db_config,
                pool_name="data_acquisition_pool",
                pool_size=7,
                pool_reset_connection=True
            )
            self.logger.info("Database connection pool created")
            
            # Set connection pools for all data sources
            self._set_data_source_connection_pools()
            
        except Exception as e:
            self.logger.error(f"Failed to create connection pool: {e}")
            raise

    def _set_data_source_connection_pools(self):
        """Set connection pools for all data sources"""
        data_sources = [
            ('qt_reader', self.qt_reader),
            ('teledyne_reader', self.teledyne_reader),
            ('labjack_reader_1', self.labjack_reader_1),
            ('labjack_reader_2', self.labjack_reader_2),
            ('lakeshore_reader_target_stick', self.lakeshore_reader_target_stick),
            ('lakeshore_reader_fridge_temp', self.lakeshore_reader_fridge_temp),
            ('lakeshore_reader_magnet_temp', self.lakeshore_reader_magnet_temp),
            ('maxigauge_reader', self.maxigauge_reader),
            ('ivc_reader', self.ivc_reader)
        ]
        
        for name, source in data_sources:
            if source is not None and hasattr(source, 'set_connection_pool'):
                source.set_connection_pool(self.connection_pool)
                self.logger.debug(f"Set connection pool for {name}")
    
    async def _start_data_sources(self):
        """Start all data sources"""
        data_sources = [
            ('qt_reader', self.qt_reader),
            ('teledyne_reader', self.teledyne_reader),
            ('labjack_reader_1', self.labjack_reader_1),
            ('labjack_reader_2', self.labjack_reader_2),
            ('lakeshore_reader_target_stick', self.lakeshore_reader_target_stick),
            ('lakeshore_reader_fridge_temp', self.lakeshore_reader_fridge_temp),
            ('lakeshore_reader_magnet_temp', self.lakeshore_reader_magnet_temp),
            ('maxigauge_reader', self.maxigauge_reader),
            ('ivc_reader', self.ivc_reader)
        ]
        
        for name, source in data_sources:
            if source is not None and hasattr(source, 'start'):
                try:
                    source.start()
                    self.logger.info(f"{name} started successfully")
                except Exception as e:
                    self.logger.error(f"Failed to start {name}: {e}")
    
    async def _stop_data_sources(self):
        """Stop all data sources"""
        data_sources = [
            ('qt_reader', self.qt_reader),
            ('teledyne_reader', self.teledyne_reader),
            ('labjack_reader_1', self.labjack_reader_1),
            ('labjack_reader_2', self.labjack_reader_2),
            ('lakeshore_reader_target_stick', self.lakeshore_reader_target_stick),
            ('lakeshore_reader_fridge_temp', self.lakeshore_reader_fridge_temp),
            ('lakeshore_reader_magnet_temp', self.lakeshore_reader_magnet_temp),
            ('maxigauge_reader', self.maxigauge_reader),
            ('ivc_reader', self.ivc_reader)
        ]
        
        for name, source in data_sources:
            if source is not None and hasattr(source, 'stop'):
                try:
                    source.stop()
                    self.logger.info(f"{name} stopped successfully")
                except Exception as e:
                    self.logger.error(f"Error stopping {name}: {e}")
    
    async def get_current_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        return datetime.now(self.EST)

    async def pipeline_all_data(self):

        tasks = [
            self.qt_reader.pipeline_data(),
            self.teledyne_reader.pipeline_data(),
            self.labjack_reader_1.pipeline_data(),
            self.labjack_reader_2.pipeline_data(),
            self.lakeshore_reader_target_stick.pipeline_data(),
            self.lakeshore_reader_fridge_temp.pipeline_data(),
            self.lakeshore_reader_magnet_temp.pipeline_data(),
            self.maxigauge_reader.pipeline_data(),
            self.ivc_reader.pipeline_data(),
        ]

        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                successful_pipelines = sum(1 for result in results if result is True)
                self.logger.debug(f"Pipeline completed: {successful_pipelines}/{len(tasks)} successful")
            except Exception as e:
                self.logger.error(f"Error in concurrent data pipeline: {e}")   

    
    async def run(self):
        """Main data acquisition loop"""
        try:
            # Initialize all data sources
            self._initialize_data_sources()
            
            # Create database connection pool
            await self._create_connection_pool()
            
            # Start all data sources
            await self._start_data_sources()
            
            self.logger.info("Data acquisition system started successfully")
            
            # Main data acquisition loop
            while not self.shutdown_event.is_set():
                try:
                    # Pipeline all data sources concurrently
                    await self.pipeline_all_data()
                    
                    # Wait before next iteration
                    await asyncio.sleep(ASYNC_READ_INTERVAL)
                    
                except Exception as e:
                    self.logger.error(f"Error in main data acquisition loop: {e}")
                    await asyncio.sleep(1)  # Brief pause before retrying
            
        except Exception as e:
            self.logger.error(f"Fatal error in data acquisition system: {e}")
            raise
        finally:
            # Cleanup
            self.logger.info("Cleaning up data acquisition system")
            
            # Stop all data sources
            await self._stop_data_sources()
            
            # Close connection pool
            if self.connection_pool:
                self.connection_pool.close()
                self.logger.info("Database connection pool closed")
            
            self.logger.info("Data acquisition system cleanup complete")
