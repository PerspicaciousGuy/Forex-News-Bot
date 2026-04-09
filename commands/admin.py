from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import get_bot_stats, save_news_events
import os
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin only: Shows bot statistics."""
    user_id = update.effective_user.id
    admin_id = os.getenv("ADMIN_ID")
    
    # Simple security check
    if not admin_id or str(user_id) != str(admin_id):
        await update.message.reply_text("⛔ *Access Denied:* You are not authorized to view these stats.", parse_mode="Markdown")
        return

    stats = await get_bot_stats()
    
    msg = (
        "📊 *Bot Admin Dashboard*\n\n"
        f"👥 *Total Subscribers:* {stats['total_users']}\n"
        "✅ *Status:* Online & Monitoring Markets"
    )
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_news_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles JSON file uploads from admin to update news calendar."""
    user_id = update.effective_user.id
    admin_id = os.getenv("CHAT_ID")
    
    if str(user_id) != str(admin_id):
        return

    document = update.message.document
    if not document.file_name.endswith(".json"):
        await update.message.reply_text("❌ Please send a `.json` file exported from Forex Factory.")
        return

    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()
        data = json.loads(file_content.decode("utf-8"))

        # Normalize data for easier scheduling
        # FF JSON format example: {"title": "...", "country": "USD", "date": "Apr 10, 2026", "time": "6:00pm", "impact": "High"}
        normalized_events = []
        for entry in data:
            try:
                # Normalize Date: "Apr 10, 2026" -> "2026-04-10"
                raw_date = entry.get("date")
                dt_obj = datetime.strptime(raw_date, "%b %d, %Y")
                entry["normalized_date"] = dt_obj.strftime("%Y-%m-%d")

                # Normalize Time: "6:00pm" -> "18:00", "All Day" -> "00:00"
                raw_time = entry.get("time", "").lower()
                if "all day" in raw_time or not raw_time:
                    entry["normalized_time"] = "00:00"
                else:
                    # Handle formats like "6:00pm" or "10:30am"
                    time_obj = datetime.strptime(raw_time, "%I:%M%p")
                    entry["normalized_time"] = time_obj.strftime("%H:%M")
                
                normalized_events.append(entry)
            except Exception as parse_err:
                logger.warning(f"Skipping entry due to parse error: {parse_err} | Entry: {entry}")

        count = await save_news_events(normalized_events)
        
        await update.message.reply_text(
            f"✅ *Calendar Updated!*\n\n"
            f"📥 *Total Events Saved:* {count}\n"
            f"🚀 The bot will now alert for High/Medium impact news automatically.",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error processing news file: {e}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")

def get_admin_handlers():
    from telegram.ext import MessageHandler, filters
    return [
        CommandHandler("stats", admin_stats_command),
        MessageHandler(filters.Document.ALL, handle_news_file)
    ]
