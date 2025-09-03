# Discord Bot Monitoring System

## Overview

The Discord bot provides automated monitoring and alerting for the UVA lab systems. It continuously monitors database health, equipment status, and sends real-time alerts to Discord channels.

## 🤖 Bot Features

### Real-time Monitoring
- **LN2 Level Monitoring**: Alerts when liquid nitrogen needs refilling
- **Temperature Monitoring**: Coldhead temperature range checks
- **Data Freshness**: Alerts when data collection stops
- **System Health**: Periodic status updates

### Interactive Commands
- **Status Queries**: Get current system readings
- **Data Checks**: Verify database connectivity
- **Manual Updates**: Trigger status reports
- **Help System**: List available commands

## 🚀 Quick Start

### Prerequisites
```bash
# Required Python packages
pip install discord.py python-dotenv pytz apscheduler

# Discord bot token (from Discord Developer Portal)
# Channel IDs for notifications
```

### Environment Setup
Create a `.env` file in the root directory:
```env
# Discord Configuration
DISCORD_TOKEN=your_bot_token_here
BOT_CHANNEL_ID=1234567890123456789
UVALAB_CHANNEL_ID=1234567890123456789

# Alert Thresholds
LN2_THRESHOLD=2.5
ColdHead_TEMP_HIGH=5.0
ColdHead_TEMP_LOW=3.0
```

### Running the Bot
```bash
# Start the Discord bot
python Discord_Alert.py

# Expected output:
# ✅ Bot is online as LabBot#1234
# 👁️👄👁️ Always watching...
```

## 📱 Discord Commands

### Basic Commands

#### `!Commands`
Shows list of available bot commands
