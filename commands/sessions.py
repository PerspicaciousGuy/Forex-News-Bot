from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from database import get_market_sessions
from messages.bot_text import SESSION_HEADER, SESSION_FOOTER, WEEKEND_MESSAGE

def get_time_diff_str(time1_str, time2_str):
    """Calculates difference between two HH:MM strings: time2 - time1."""
    t1 = datetime.strptime(time1_str, "%H:%M")
    t2 = datetime.strptime(time2_str, "%H:%M")
    
    diff = t2 - t1
    # Handle overnight sessions
    if diff.days < 0:
        diff += timedelta(days=1)
    
    hours, remainder = divmod(diff.seconds, 3600)
    minutes = remainder // 60
    return f"{hours}h {minutes}m"

async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /sessions command to show live status with duration counters.
    """
    now_utc = datetime.now(timezone.utc)
    current_time_str = now_utc.strftime("%H:%M")
    weekday = now_utc.weekday()
    
    # Check for Weekend first
    is_weekend = False
    if weekday == 5: # Saturday
        is_weekend = True
    elif weekday == 4 and current_time_str >= "21:05": # Friday night
        is_weekend = True
    elif weekday == 6 and current_time_str < "21:30": # Sunday morning
        is_weekend = True

    if is_weekend:
        await update.message.reply_text(WEEKEND_MESSAGE, parse_mode="Markdown")
        return

    # Fetch dynamic sessions from DB
    market_sessions = await get_market_sessions()

    response = SESSION_HEADER
    
    for session in market_sessions:
        name = session["name"]
        open_time = session["open"]
        close_time = session["close"]
        
        # Check active status
        is_open = False
        if open_time < close_time: # London 07:00 to 16:00
            if open_time <= current_time_str < close_time:
                is_open = True
        else: # Sydney 22:00 to 07:00
            if current_time_str >= open_time or current_time_str < close_time:
                is_open = True
        
        if is_open:
            status_emoji = "🟢 OPEN"
            # How long it has been open
            elapsed = get_time_diff_str(open_time, current_time_str)
            # How long until it closes
            remaining = get_time_diff_str(current_time_str, close_time)
            
            response += f"**{name}**: {status_emoji}\n"
            response += f"   🕒 Hours: `{open_time}` to `{close_time}` UTC\n"
            response += f"   ⌛ Open for: `{elapsed}`\n"
            response += f"   🛑 Closes in: `{remaining}`\n\n"
        else:
            status_emoji = "🔴 CLOSED"
            # How long until it opens
            until_open = get_time_diff_str(current_time_str, open_time)
            
            response += f"**{name}**: {status_emoji}\n"
            response += f"   🕒 Hours: `{open_time}` to `{close_time}` UTC\n"
            response += f"   🚀 Opens in: `{until_open}`\n\n"

    response += SESSION_FOOTER.format(current_time=current_time_str)
    await update.message.reply_text(response, parse_mode="Markdown")
