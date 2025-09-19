# Data Acquisition System - Refactored

This document describes the refactored data acquisition system that has been cleaned up and modularized for better maintainability and ease of use.

## Structure

### Files

- **`main.py`** - Clean entry point with argument parsing and logging setup
- **`data_acquisition.py`** - Main data acquisition system class
- **`standalone_data_acquisition.py`** - Original file (kept for reference)
- **`_*.py`** - Individual device reader modules

### Key Improvements

1. **Clean Separation of Concerns**
   - `main.py` handles CLI arguments, logging setup, and error handling
   - `data_acquisition.py` contains the core business logic
   - Each device reader is in its own module

2. **Object-Oriented Design**
   - `DataAcquisitionSystem` class encapsulates all functionality
   - Clean initialization and lifecycle management
   - Proper resource cleanup

3. **Better Error Handling**
   - Graceful shutdown on signals (SIGINT, SIGTERM)
   - Comprehensive error logging
   - Proper exception propagation

4. **Improved Logging**
   - Configurable log levels (INFO/DEBUG)
   - Optional terminal output
   - Structured log formatting

5. **No Threading**
   - All operations are synchronous
   - Simpler code flow
   - Easier debugging

## Usage

### Basic Usage

```bash
# Run with file logging only
python main.py

# Show logs in terminal
python main.py --terminal-log

# Enable verbose logging
python main.py --verbose

# Verbose mode with terminal output
python main.py --verbose --terminal-log
```

### Programmatic Usage

```python
import asyncio
from data_acquisition import DataAcquisitionSystem

async def run_acquisition():
    system = DataAcquisitionSystem()
    await system.run()

# Run the system
asyncio.run(run_acquisition())
```

## Configuration

The system uses the same configuration files as before:
- `config.py` - Main configuration
- Database configuration JSON file
- Device-specific settings

## Data Flow

1. **Initialization**
   - Load database configuration
   - Initialize all device readers
   - Create database connection pool
   - Setup signal handlers

2. **Main Loop**
   - Read data from all devices
   - Insert data into database concurrently
   - Wait for next iteration
   - Handle shutdown signals

3. **Cleanup**
   - Stop all device readers
   - Close database connections
   - Log completion

## Device Readers

All device readers follow the same interface:
- `start()` - Initialize and start the reader
- `stop()` - Stop and cleanup the reader
- `get_latest_data()` - Get the most recent data
- `read_data()` - Perform a single read operation

## Database Operations

Database operations are handled synchronously with proper connection pooling:
- Automatic connection management
- Error handling and logging
- Data validation before insertion
- Concurrent insertion of different data types

## Error Handling

The system includes comprehensive error handling:
- Graceful shutdown on signals
- Individual device error isolation
- Database connection error recovery
- Detailed error logging

## Logging

Logging is configurable and includes:
- File logging (always enabled)
- Optional terminal output
- Configurable log levels
- Structured log format with timestamps

## Migration from Original

The refactored system maintains full compatibility with the original:
- Same configuration files
- Same database schema
- Same data formats
- Same device interfaces

The main difference is the cleaner, more maintainable code structure.
