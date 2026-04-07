# Forex Market Session Monitor Bot

A professional Telegram bot designed to monitor global Forex market sessions and provide automated alerts for market openings, closings, and overlaps. The bot is focused on precision timing to help traders manage their trading day effectively.

## Features

### 1. Automated Market Alerts
The bot tracks the four major global market sessions: Sydney, Tokyo, London, and New York. It provides the following automated notifications for each:
- 30-Minute Warning: Notification sent 30 minutes before any market opens.
- 5-Minute Prep: Notification sent 5 minutes before any market opens.
- Market Open: Notification sent the moment a session officially begins.
- Market Close: Notification sent the moment a session ends.

### 2. High Volatility Overlap Alerts
The bot specifically identifies the London and New York session overlap, which is the period of highest liquidity and volatility in the Forex market.

### 3. Weekend Mode
To maintain a clean and professional experience, the bot includes a specialized weekend handler:
- Friday Market Wrap: Sends a notification at 21:00 UTC (New York Close) once the markets close for the weekend.
- Sunday Market Open: Sends a notification at 21:30 UTC just before the new trading week begins with the Sydney open.
- Silent Saturdays: Automated session alerts are automatically disabled during the weekend.

### 4. Interactive Commands
- /start: Welcomes the user and explains the bot's capabilities.
- /sessions: Provides a live real-time status of all four major markets, showing which sessions are currently open or closed and their respective trading hours.

## Project Architecture

The codebase is organized into a modular structure for easy maintenance and scalability:
- commands/: Contains individual logic files for each Telegram command.
- messages/: Centralized one-file repository for all bot communication text.
- scheduler.py: The background monitoring engine that handles all temporal calculations and alerts.
- main.py: The entry point that initializes the Telegram application and the FastAPI health-check server.

## Installation and Setup

### Prerequisites
- Python 3.10 or higher.
- A Telegram Bot Token (obtained via @BotFather).
- A designated Telegram Chat ID (Group or Channel).

### Required Environment Variables
Create a .env file in the root directory with the following keys:
- TELEGRAM_BOT_TOKEN: Your unique API token from @BotFather.
- CHAT_ID: The numeric ID of the group or channel where you want the alerts delivered.

### Running Locally
1. Install dependencies:
   pip install -r requirements.txt
2. Start the bot:
   python main.py

## Deployment
This project is configured for cloud hosting services like Koyeb. It includes a built-in FastAPI server on port 8000 for health monitoring.
