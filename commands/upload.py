import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database import save_news_events

logger = logging.getLogger(__name__)

async def upload_calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles JSON file uploads for the economic calendar."""
    document = update.message.document
    
    # Check if it's a JSON file (by extension if mime-type check was loose)
    if not document.file_name.endswith(".json"):
        await update.message.reply_text("❌ Please upload a valid `.json` file containing the economic calendar.")
        return

    status_msg = await update.message.reply_text("📥 Processing calendar file...")

    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_path = f"scratch/{document.file_name}"
        await file.download_to_drive(file_path)

        # Parse JSON
        with open(file_path, "r") as f:
            events = json.load(f)

        if not isinstance(events, list):
            await status_msg.edit_text("❌ Invalid JSON format. Expected a list of events.")
            return

        # Normalize data (Forex Factory format)
        normalized_events = []
        for event in events:
            try:
                # Example input: "Apr 09 2026", "1:30pm"
                raw_date = event.get("date", "")
                raw_time = event.get("time", "")

                if not raw_date or not raw_time:
                    continue

                # Parse date (handles common formats like "Apr 09 2026" or "2026-04-09")
                try:
                    dt_obj = datetime.strptime(raw_date, "%b %d %Y")
                except ValueError:
                    dt_obj = datetime.strptime(raw_date, "%Y-%m-%d")

                # Parse time (handles "1:30pm" or "13:30")
                try:
                    time_obj = datetime.strptime(raw_time, "%I:%M%p")
                except ValueError:
                    time_obj = datetime.strptime(raw_time, "%H:%M")

                event["normalized_date"] = dt_obj.strftime("%Y-%m-%d")
                event["normalized_time"] = time_obj.strftime("%H:%M")
                normalized_events.append(event)
            except Exception as e:
                logger.warning(f"Skipping event due to parsing error: {e}")
                continue

        if not normalized_events:
            await status_msg.edit_text("⚠️ No valid events found in the file.")
            return

        # Save to DB
        count = await save_news_events(normalized_events)
        
        await status_msg.edit_text(
            f"✅ *Calendar Updated!*\n\n"
            f"📊 Imported: `{count}` high/medium impact events.\n"
            f"🚀 The bot will now monitor and alert for these events 0-15 minutes before they occur.",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        await status_msg.edit_text(f"❌ Error processing file: {str(e)}")
