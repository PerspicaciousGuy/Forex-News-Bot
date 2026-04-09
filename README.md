# Forex Market Session Monitor Bot

A professional Telegram bot designed to monitor global Forex market sessions and provide automated alerts for market openings, closings, and overlaps. The bot is focused on precision timing to help traders manage their trading day effectively.

## Features

### 1. Automated Market Alerts
The bot tracks the four major global market sessions: Sydney, Tokyo, London, and New York. It provides the following automated notifications for each:
- 30-Minute Warning: Notification sent 30 minutes before any market opens.
- 5-Minute Prep: Notification sent 5 minutes before any market opens.
- Market Open: Notification sent the moment a session officially begins.
- Market Close: Notification sent the moment a session ends.

### 2. User Personalization & Scalability
- **Session Filtering**: Use `/settings` to toggle specific market alerts (Tokyo, London, etc.) on or off.
- **Multi-User Support**: Powered by MongoDB, the bot handles thousands of subscribers simultaneously.
- **Stop Command**: Use `/stop` to easily unsubscribe and remove your data.

### 3. Administrative Dashboard
- **Bot Statistics**: Admins can use `/stats` to view total subscriber growth and system status.

### 4. High Volatility Overlap Alerts
- **London/NY Overlap**: Specialized alerts for the period of highest liquidity.
- **Grouped Notifications**: Smart logic combines overlapping alerts to reduce notification clutter.

### 5. Weekend Mode
- Friday Market Wrap: 21:00 UTC (New York Close).
- Sunday Market Open: 21:30 UTC (Sydney Pre-Open).
- Silent Weekends: No noise during non-trading hours.

## Interactive Commands
- `/start`: Onboard and register for alerts.
- `/settings`: Personalize your market alert preferences.
- `/sessions`: Check current live market status.
- `/stop`: Unsubscribe from all alerts.
- `/stats` (Admin): View global bot statistics.

## Project Architecture
- `database.py`: Asynchronous MongoDB driver for subscriber management.
- `commands/`: Modular command handlers for start, stop, sessions, settings, and admin.
- `scheduler.py`: The background engine managing precision timing and filtered broadcasts.
- `messages/`: Central repository for all professional bot communication.
- `main.py`: The entry point that initializes the Telegram application and the FastAPI health-check server.

## Installation and Setup

### Prerequisites
- Python 3.10 or higher.
- A Telegram Bot Token (obtained via @BotFather).
- A designated Telegram Chat ID (Group or Channel).

### Required Environment Variables
- `TELEGRAM_BOT_TOKEN`: API token from @BotFather.
- `MONGO_URI`: MongoDB connection string.
- `CHAT_ID`: Admin Chat ID for dashboard access.

### Running Locally
1. Install dependencies:
   pip install -r requirements.txt
2. Start the bot:
   python main.py

## Deployment
This project is configured for cloud hosting services like Koyeb. It includes a built-in FastAPI server on port 8000 for health monitoring.
