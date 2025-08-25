#!/usr/bin/env python3
"""
Start script for the data collector
"""

import logging
import json

DATABASE_FILE = "/var/www/spin/config.json"

# Load database configuration
with open(DATABASE_FILE, 'r') as f:
    config = json.load(f)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start_data_collector():
    """Start the data collector Flask application"""

    logger.info(f"Database IP: {config['host']}")
    logger.info(f"Database port: {config['port']}")
    logger.info(f"Database user: {config['user']}")
    logger.info(f"Database password: {config['password']}")
    logger.info(f"Database name: {config['database']}")
    
    logger.info("🚀 Starting Data Collector...")
    logger.info("=" * 60)
    logger.info("📡 The data collector will receive data via HTTP endpoints:")
    logger.info("  • GET /get_recent_data - for querying stored data")
    logger.info("  • GET /health - for health checks")
    logger.info("  • POST /shutdown - for graceful server shutdown")
    logger.info("")
    logger.info("🌐 Web Interface: http://localhost:5000")
    logger.info("")
    logger.info("🛑 Shutdown Options:")
    logger.info("  • Press Ctrl+C in this terminal")
    logger.info("  • Use the shutdown button in the web interface")
    logger.info("  • Send POST request to /shutdown endpoint")
    logger.info("")
    logger.info("=" * 60)
    
    try:
        # Import and run the data collector
        from data_collector import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("🛑 Data collector stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Error starting data collector: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_data_collector() 