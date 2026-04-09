from telegram import Update
from telegram.ext import ContextTypes
from database import remove_subscriber

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /stop command. Removes the chat_id from the database.
    """
    chat_id = str(update.effective_chat.id)
    await remove_subscriber(chat_id)
    
    await update.message.reply_text(
        "🛑 **Unsubscribed**\n\nYou will no longer receive automatic market session alerts in this chat. Use /start to subscribe again at any time!", 
        parse_mode="Markdown"
    )
