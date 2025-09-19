#!/usr/bin/env python3
"""
Main entry point for the Data Acquisition System
This script provides a clean interface to run the data acquisition system.
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from data_acquisition import DataAcquisitionSystem


def setup_logging(verbose=False, terminal_log=False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add file handler
    file_handler = logging.FileHandler('data_acquisition.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Add terminal handler if requested
    if terminal_log:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    return root_logger


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Data Acquisition System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run with file logging only
  python main.py --terminal-log            # Show logs in terminal
  python main.py --verbose                 # Enable verbose logging
  python main.py --verbose --terminal-log  # Verbose mode with terminal output
        """
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--terminal-log', 
        action='store_true', 
        help='Show log output in terminal'
    )
    
    return parser.parse_args()


async def main():
    """Main entry point"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup logging
        logger = setup_logging(verbose=args.verbose, terminal_log=args.terminal_log)
        logger.info("Starting Data Acquisition System")
        
        # Create and run data acquisition system
        data_acquisition = DataAcquisitionSystem()
        await data_acquisition.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown signal received from user")
        logger.info("Shutdown signal received from user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        if 'logger' in locals():
            logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        print("\n✅ Data acquisition system shutdown complete")
        if 'logger' in locals():
            logger.info("Data acquisition system shutdown complete")


if __name__ == '__main__':
    asyncio.run(main())
