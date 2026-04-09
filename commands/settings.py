from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from database import get_subscriber_prefs, update_subscriber_prefs
import logging

logger = logging.getLogger(__name__)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the session preference menu."""
    chat_id = update.effective_chat.id
    prefs = await get_subscriber_prefs(chat_id)
    
    keyboard = []
    for session, enabled in prefs.items():
        status = "✅" if enabled else "❌"
        # Toggle logic: if we click it, we flip the value
        keyboard.append([InlineKeyboardButton(f"{session}: {status}", callback_data=f"toggle_{session}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🛠 *Market Alert Settings*\n\nToggle the sessions you want to receive alerts for:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles toggle clicks."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    data = query.data
    
    if data.startswith("toggle_"):
        session_name = data.replace("toggle_", "")
        prefs = await get_subscriber_prefs(chat_id)
        
        # Toggle
        if session_name in prefs:
            prefs[session_name] = not prefs[session_name]
            await update_subscriber_prefs(chat_id, prefs)
        
        # Rebuild keyboard
        keyboard = []
        for session, enabled in prefs.items():
            status = "✅" if enabled else "❌"
            keyboard.append([InlineKeyboardButton(f"{session}: {status}", callback_data=f"toggle_{session}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)

# Handler setup helper
def get_settings_handlers():
    return [
        CommandHandler("settings", settings_command),
        CallbackQueryHandler(settings_callback, pattern="^toggle_")
    ]
