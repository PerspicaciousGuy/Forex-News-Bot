import asyncio
from datetime import datetime, timedelta
from api_client import fetch_economic_calendar
from telegram.ext import ContextTypes
import os

# To avoid duplicate alerts
SENT_ALERTS_FILE = "sent_alerts.txt"

def is_alert_sent(event_id):
    """
    Check if an alert was already sent for this event.
    """
    if not os.path.exists(SENT_ALERTS_FILE):
        return False
    with open(SENT_ALERTS_FILE, "r") as f:
        return event_id in f.read().splitlines()

def mark_alert_as_sent(event_id):
    """
    Mark an alert as sent.
    """
    with open(SENT_ALERTS_FILE, "a") as f:
        f.write(f"{event_id}\n")

async def high_impact_alert_task(context: ContextTypes.DEFAULT_TYPE):
    """
    Task to check for high-impact news and send alerts.
    Runs every 30 minutes in the background.
    """
    print(f"[{datetime.now()}] --- Checking for high-impact alerts... ---")
    
    events = await fetch_economic_calendar()
    if not events:
        return

    now = datetime.now()
    alert_threshold = 60 # Check events within the next 60 minutes
    
    chat_id = os.getenv("CHAT_ID")
    if not chat_id:
        print("❌ Error: CHAT_ID not set in environment variables.")
        return

    for event in events:
        impact = event.get("impact")
        if impact != "High":
            continue
            
        event_time_str = event.get("date")
        # Format: 2026-04-07 09:30:00
        try:
            event_time = datetime.strptime(event_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"Invalid date format: {event_time_str}")
            continue

        # Check if event is within the next 60 minutes
        diff = (event_time - now).total_seconds() / 60
        
        # Unique ID for event: Date + Event Name
        event_id = f"{event.get('date')}_{event.get('event')}".replace(" ", "_")

        if 0 < diff <= alert_threshold and not is_alert_sent(event_id):
            currency = event.get("currency")
            event_name = event.get("event")
            time_left = int(diff)

            alert_message = (
                f"🚨 **HIGH IMPACT NEWS ALERT** 🚨\n\n"
                f"🪙 **Currency**: {currency}\n"
                f"📉 **Event**: {event_name}\n"
                f"⏰ **Time Left**: ~{time_left} minutes\n\n"
                "Get ready for volatility! 🧨"
            )
            
            try:
                await context.bot.send_message(chat_id=chat_id, text=alert_message, parse_mode="Markdown")
                mark_alert_as_sent(event_id)
                print(f"✅ Alert sent for: {event_name}")
            except Exception as e:
                print(f"❌ Error sending message: {e}")
