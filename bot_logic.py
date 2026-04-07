from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command.
    """
    message = (
        "👋 Welcome! I am your **Market Session Monitor**.\n\n"
        "I will automatically alert this group when the **London, New York, Tokyo, and Sydney** markets open or close.\n\n"
        "⏰ **What I do:**\n"
        "• 🚨 30-minute Warning before Market Opens\n"
        "• 🟢 Live Market Open Alerts\n"
        "• 🔴 Market Close Alerts\n\n"
        "Sit back and let me keep you on track! 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")
