from telegram import Update
from telegram.ext import ContextTypes
from messages.bot_text import START_MESSAGE

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command.
    """
    await update.message.reply_text(START_MESSAGE, parse_mode="Markdown")
