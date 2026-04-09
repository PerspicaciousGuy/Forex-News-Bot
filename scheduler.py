import asyncio
from datetime import datetime, timezone, timedelta
import logging
import os
from messages.bot_text import (
    WEEKEND_CLOSE_ALERT, WEEKEND_OPEN_ALERT, 
    WARNING_TEXT, PREP_TEXT, OPEN_TEXT, CLOSE_TEXT,
    NY_OPEN_OVERLAP, LONDON_CLOSE_OVERLAP
)
from database import get_all_subscribers_data

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
    
    # Get all subscribers with preferences from MongoDB
    subscribers = await get_all_subscribers_data()
    
    # Process for each session alert
    for session in MARKET_SESSIONS:
        session_name = session["name"]
        
        # Determine current alert type
        open_time = session["open"]
        close_time = session["close"]
        open_dt = datetime.strptime(open_time, "%H:%M")
        warning_30m_dt = (open_dt - timedelta(minutes=30)).strftime("%H:%M")
        warning_5m_dt = (open_dt - timedelta(minutes=5)).strftime("%H:%M")

        alert_msg = None
        alert_type = None
        display_name = f"{session_name} (London/NY Overlap 🚀🚀)" if session_name == "New York 🇺🇸" else session_name

        if current_time_str == warning_30m_dt:
            alert_msg = WARNING_TEXT.format(name=display_name)
            alert_type = f"{session_name}_30min"
        elif current_time_str == warning_5m_dt:
            alert_msg = PREP_TEXT.format(name=display_name)
            alert_type = f"{session_name}_5min"
        elif current_time_str == open_time:
            alert_msg = NY_OPEN_OVERLAP if session_name == "New York 🇺🇸" else OPEN_TEXT.format(name=session_name)
            alert_type = f"{session_name}_open"
        elif current_time_str == close_time:
            alert_msg = LONDON_CLOSE_OVERLAP if session_name == "London 🇬🇧" else CLOSE_TEXT.format(name=session_name)
            alert_type = f"{session_name}_close"

        if alert_msg and alert_type:
            full_alert_id = f"{today_str}_{alert_type}"
            if not is_alert_sent(full_alert_id):
                # Filter subscribers who want this session
                target_chat_ids = [
                    s["chat_id"] for s in subscribers 
                    if s.get("preferences", {}).get(session_name, True)
                ]
                
                # Add admin if not in list
                admin_id = os.getenv("CHAT_ID")
                if admin_id and int(admin_id) not in target_chat_ids:
                    target_chat_ids.append(int(admin_id))

                await send_telegram_msg(context, target_chat_ids, alert_msg, full_alert_id)

    # --- SPECIAL WEEKEND ALERTS (Sent to all) ---
    all_chat_ids = [s["chat_id"] for s in subscribers]
    admin_id = os.getenv("CHAT_ID")
    if admin_id and int(admin_id) not in all_chat_ids:
        all_chat_ids.append(int(admin_id))

    if weekday == 4 and current_time_str == "21:00":
        alert_id = f"{today_str}_weekend_close"
        if not is_alert_sent(alert_id):
            await send_telegram_msg(context, all_chat_ids, WEEKEND_CLOSE_ALERT, alert_id)
    
    if weekday == 6 and current_time_str == "21:30":
        alert_id = f"{today_str}_weekend_open"
        if not is_alert_sent(alert_id):
            await send_telegram_msg(context, all_chat_ids, WEEKEND_OPEN_ALERT, alert_id)

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
