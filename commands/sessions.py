from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes
from scheduler import MARKET_SESSIONS
from messages.bot_text import SESSION_HEADER, SESSION_FOOTER, WEEKEND_MESSAGE

async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /sessions command to show live status.
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

    response = SESSION_HEADER
    
    for session in MARKET_SESSIONS:
        name = session["name"]
        open_time = session["open"]
        close_time = session["close"]
        
        # Simple check for active status (handles overnight open/close)
        is_open = False
        if open_time < close_time: # London 07:00 to 16:00
            if open_time <= current_time_str < close_time:
                is_open = True
        else: # Sydney 22:00 to 07:00
            if current_time_str >= open_time or current_time_str < close_time:
                is_open = True
        
        status_emoji = "🟢 OPEN" if is_open else "🔴 CLOSED"
        response += f"**{name}**: {status_emoji}\n"
        response += f"   🕒 Hours: `{open_time}` to `{close_time}` UTC\n\n"

    response += SESSION_FOOTER.format(current_time=current_time_str)
    await update.message.reply_text(response, parse_mode="Markdown")
