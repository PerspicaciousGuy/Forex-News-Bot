import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler
from bot_logic import start_command, calendar_command, news_command
from scheduler import high_impact_alert_task
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Token from BotFather
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ Error: TELEGRAM_BOT_TOKEN not set in environment variables.")

def main():
    """
    Main entry point for the bot.
    """
    print("🚀 Starting High-Impact Forex Bot...")

    # Create application
    application = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("calendar", calendar_command))
    application.add_handler(CommandHandler("news", news_command))

    # JobQueue for alerts (runs every 30 minutes)
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(high_impact_alert_task, interval=1800, first=10) # 1800s = 30 mins
        print("✅ Alert scheduler started! (Checking every 30 mins)")
    else:
        print("❌ Error: JobQueue not available. Alerts will not be sent.")

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
