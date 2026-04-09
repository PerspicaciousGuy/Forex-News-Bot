from telegram import Update
from telegram.ext import ContextTypes
from messages.bot_text import START_MESSAGE
from database import add_subscriber

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command. Saves the chat_id to the database.
    """
    chat_id = str(update.effective_chat.id)
    await add_subscriber(chat_id)
    
    await update.message.reply_text(START_MESSAGE, parse_mode="Markdown")
