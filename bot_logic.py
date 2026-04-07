from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from scheduler import MARKET_SESSIONS

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command.
    """
    message = (
        "👋 Welcome! I am your **Market Session Monitor**.\n\n"
        "I will automatically alert this group when the **London, New York, Tokyo, and Sydney** markets open or close.\n\n"
        "📜 **Commands:**\n"
        "/sessions - Check what's open right now and time left!\n\n"
        "⏰ **What I do automatically:**\n"
        "• 🚨 30-minute Warning before Market Opens\n"
        "• 🟢 Live Market Open Alerts\n"
        "• 🔴 Market Close Alerts\n\n"
        "Sit back and let me keep you on track! 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /sessions command to show live status.
    """
    now_utc = datetime.now(timezone.utc)
    current_time_str = now_utc.strftime("%H:%M")
    
    response = "🗺️ **Market Status (Live UTC)**\n\n"
    
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

    response += f"\n🕒 **Current Time**: `{current_time_str}` UTC"
    await update.message.reply_text(response, parse_mode="Markdown")
