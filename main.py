import logging
import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from bot_logic import start_command, calendar_command, news_command
from scheduler import high_impact_alert_task
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Token from BotFather
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup FastAPI App for Health Check (Koyeb requires a web service)
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Forex Bot is Alive!", "timestamp": str(os.getenv("PORT"))}

async def run_bot():
    """
    Subroutine to run the Telegram bot.
    """
    if not TOKEN:
        logger.error("❌ Error: TELEGRAM_BOT_TOKEN not set!")
        return

    # Create application
    application = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("calendar", calendar_command))
    application.add_handler(CommandHandler("news", news_command))

    # JobQueue for alerts (runs every 30 minutes)
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(high_impact_alert_task, interval=1800, first=10)
        logger.info("✅ Alert scheduler started! (Checking every 30 mins)")

    # Run the bot with a simpler loop
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logger.info("🚀 Telegram Bot is polling...")
        
        # Keep the bot running until explicitly stopped
        while True:
            await asyncio.sleep(1)

async def run_web_server():
    """
    Subroutine to run the FastAPI web server.
    """
    # Port provided by Koyeb
    port = int(os.getenv("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info(f"🌐 Web Server starting on port {port}...")
    await server.serve()

async def main():
    """
    Main entry point for both Bot and Web Server.
    """
    # Run both simultaneously
    await asyncio.gather(run_bot(), run_web_server())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Bot stopped manually.")
