from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import get_bot_stats
import os
import logging

logger = logging.getLogger(__name__)

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin only: Shows bot statistics."""
    user_id = update.effective_user.id
    admin_id = os.getenv("CHAT_ID") # Using development CHAT_ID as the admin ID
    
    # Simple security check
    if str(user_id) != str(admin_id):
        return # Silently ignore non-admins

    stats = await get_bot_stats()
    
    msg = (
        "📊 *Bot Admin Dashboard*\n\n"
        f"👥 *Total Subscribers:* {stats['total_users']}\n"
        "✅ *Status:* Online & Monitoring Markets"
    )
    
    await update.message.reply_text(msg, parse_mode="Markdown")

def get_admin_handlers():
    return [CommandHandler("stats", admin_stats_command)]
