import asyncio
from datetime import datetime, timezone, timedelta
import logging
import os
from messages.bot_text import (
    WEEKEND_CLOSE_ALERT, WEEKEND_OPEN_ALERT, 
    WARNING_TEXT, PREP_TEXT, OPEN_TEXT, CLOSE_TEXT,
    NY_OPEN_OVERLAP, LONDON_CLOSE_OVERLAP
)
from database import get_all_subscribers

# Setup logging
logger = logging.getLogger(__name__)

# To avoid duplicate alerts within the same minute
SENT_ALERTS_FILE = "sent_market_alerts.txt"

# --- MARKET SESSIONS CONFIGURATION (UTC) ---
# Sydney (AEST = UTC+10): 22:00 - 07:00 UTC
# Tokyo (JST = UTC+9): 00:00 - 09:00 UTC
# London (BST = UTC+1): 07:00 - 16:00 UTC
# New York (EDT = UTC-4): 12:00 - 21:00 UTC

MARKET_SESSIONS = [
    {"name": "Sydney 🇦🇺", "open": "22:00", "close": "07:00"},
    {"name": "Tokyo 🇯🇵", "open": "00:00", "close": "09:00"},
    {"name": "London 🇬🇧", "open": "07:00", "close": "16:00"},
    {"name": "New York 🇺🇸", "open": "12:00", "close": "21:00"},
]

def is_alert_sent(alert_id):
    """Checks if alert was sent today."""
    if not os.path.exists(SENT_ALERTS_FILE):
        return False
    with open(SENT_ALERTS_FILE, "r") as f:
        return alert_id in f.read().splitlines()

def mark_alert_as_sent(alert_id):
    """Marks alert as sent."""
    with open(SENT_ALERTS_FILE, "a") as f:
        f.write(f"{alert_id}\n")

async def market_timing_alert_task(context):
    """
    Checks for market openings and closings every minute.
    """
    now_utc = datetime.now(timezone.utc)
    current_time_str = now_utc.strftime("%H:%M")
    today_str = now_utc.strftime("%Y-%m-%d")
    weekday = now_utc.weekday()
    
    # Get all human subscribers from MongoDB
    subscriber_ids = await get_all_subscribers()
    
    # Add the system CHAT_ID if set (for admin groups/legacy support)
    admin_chat_id = os.getenv("CHAT_ID")
    if admin_chat_id:
        try:
            subscriber_ids.append(int(admin_chat_id))
        except ValueError:
            pass
            
    # Remove duplicates
    subscriber_ids = list(set(subscriber_ids))

    if not subscriber_ids:
        return

    # --- SPECIAL WEEKEND ALERTS ---
    if weekday == 4 and current_time_str == "21:00":
        alert_id = f"{today_str}_weekend_close"
        if not is_alert_sent(alert_id):
            await send_telegram_msg(context, subscriber_ids, WEEKEND_CLOSE_ALERT, alert_id)
        return

    if weekday == 5 or (weekday == 6 and current_time_str < "21:30") or (weekday == 4 and current_time_str > "21:00"):
        return

    if weekday == 6 and current_time_str == "21:30":
        alert_id = f"{today_str}_weekend_open"
        if not is_alert_sent(alert_id):
            await send_telegram_msg(context, subscriber_ids, WEEKEND_OPEN_ALERT, alert_id)
        return

    # --- STANDARD SESSION ALERTS ---
    for session in MARKET_SESSIONS:
        name = session["name"]
        open_time = session["open"]
        close_time = session["close"]

        # Parse times to handle warnings
        open_dt = datetime.strptime(open_time, "%H:%M")
        warning_30m_dt = (open_dt - timedelta(minutes=30)).strftime("%H:%M")
        warning_5m_dt = (open_dt - timedelta(minutes=5)).strftime("%H:%M")

        # 🚀 Special Display Name for New York alerts to handle the Overlap
        display_name = f"{name} (London/NY Overlap 🚀🚀)" if name == "New York 🇺🇸" else name

        # 1. 30-min Warning
        if current_time_str == warning_30m_dt:
            alert_id = f"{today_str}_{name}_30min_warning"
            if not is_alert_sent(alert_id):
                await send_telegram_msg(context, subscriber_ids, WARNING_TEXT.format(name=display_name), alert_id)

        # 2. 5-min Prep
        if current_time_str == warning_5m_dt:
            alert_id = f"{today_str}_{name}_5min_warning"
            if not is_alert_sent(alert_id):
                await send_telegram_msg(context, subscriber_ids, PREP_TEXT.format(name=display_name), alert_id)

        # 3. Market Open
        if current_time_str == open_time:
            alert_id = f"{today_str}_{name}_open"
            if not is_alert_sent(alert_id):
                msg = NY_OPEN_OVERLAP if name == "New York 🇺🇸" else OPEN_TEXT.format(name=name)
                await send_telegram_msg(context, subscriber_ids, msg, alert_id)

        # 4. Market Close
        if current_time_str == close_time:
            alert_id = f"{today_str}_{name}_close"
            if not is_alert_sent(alert_id):
                msg = LONDON_CLOSE_OVERLAP if name == "London 🇬🇧" else CLOSE_TEXT.format(name=name)
                await send_telegram_msg(context, subscriber_ids, msg, alert_id)

async def send_telegram_msg(context, chat_ids, message, alert_id):
    """Broadcasts message to all subscribers and marks as sent."""
    if isinstance(chat_ids, (int, str)):
        chat_ids = [chat_ids]

    success_count = 0
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Error sending to {chat_id}: {e}")

    if success_count > 0:
        mark_alert_as_sent(alert_id)
        logger.info(f"✅ Broadcast Sent: {alert_id} to {success_count} users.")
