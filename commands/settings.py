import os
import logging
import re
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, CommandHandler, 
    ConversationHandler, MessageHandler, filters
)
from database import (
    get_subscriber_prefs, update_subscriber_prefs, 
    get_market_sessions, update_market_session
)

logger = logging.getLogger(__name__)

# Conversation States
MAIN_MENU, ADMIN_SESSIONS, ADMIN_EDIT_FIELD, ADMIN_TYPING_TIME = range(4)

def is_admin(user_id):
    """Checks if the user is an admin."""
    admin_id = os.getenv("ADMIN_ID")
    return admin_id and str(user_id) == str(admin_id)

def ist_to_utc(ist_time_str):
    """Converts HH:MM IST string to HH:MM UTC string."""
    try:
        dt = datetime.strptime(ist_time_str, "%H:%M")
        utc_dt = dt - timedelta(hours=5, minutes=30)
        return utc_dt.strftime("%H:%M")
    except Exception:
        return ist_time_str

def utc_to_ist(utc_time_str):
    """Converts HH:MM UTC string to HH:MM IST string."""
    try:
        dt = datetime.strptime(utc_time_str, "%H:%M")
        ist_dt = dt + timedelta(hours=5, minutes=30)
        return ist_dt.strftime("%H:%M")
    except Exception:
        return utc_time_str

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the session preference menu."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    prefs = await get_subscriber_prefs(chat_id)
    
    keyboard = []
    # Display user alert preferences
    for session, enabled in prefs.items():
        status = "✅" if enabled else "❌"
        keyboard.append([InlineKeyboardButton(f"{session}: {status}", callback_data=f"toggle_{session}")])
    
    # Add Admin Button if authorized
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("⚙️ Edit Market Sessions (Admin)", callback_data="admin_main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🛠 *Market Alert Settings*\n\nToggle the sessions you want to receive alerts for:"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        
    return MAIN_MENU

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles toggle clicks in the main settings menu."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    data = query.data
    
    if data.startswith("toggle_"):
        session_name = data.replace("toggle_", "")
        prefs = await get_subscriber_prefs(chat_id)
        
        if session_name in prefs:
            prefs[session_name] = not prefs[session_name]
            await update_subscriber_prefs(chat_id, prefs)
        
        # Rebuild keyboard
        keyboard = []
        for session, enabled in prefs.items():
            status = "✅" if enabled else "❌"
            keyboard.append([InlineKeyboardButton(f"{session}: {status}", callback_data=f"toggle_{session}")])
        
        if is_admin(user_id):
            keyboard.append([InlineKeyboardButton("⚙️ Edit Market Sessions (Admin)", callback_data="admin_main")])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        return MAIN_MENU

# --- ADMIN SESSION EDITING FLOW ---

async def admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin entry: Timings in text, names on buttons."""
    query = update.callback_query
    await query.answer()
    
    sessions = await get_market_sessions()
    
    text = "⚙️ *Admin: Market Sessions (IST)*\n\n"
    keyboard = []
    
    # Build the text list
    for s in sessions:
        name = s['name']
        open_ist = utc_to_ist(s['open'])
        close_ist = utc_to_ist(s['close'])
        text += f"📍 **{name}:** `{open_ist}` - `{close_ist}`\n"
    
    text += "\nSelect a session to modify its timing:"
    
    # Build the button grid (2 per row for better look)
    row = []
    for s in sessions:
        name = s['name']
        row.append(InlineKeyboardButton(name, callback_data=f"edit_session_{name}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Settings", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return ADMIN_SESSIONS

async def select_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed view for a specific session."""
    query = update.callback_query
    await query.answer()
    
    session_name = query.data.replace("edit_session_", "")
    context.user_data['editing_session'] = session_name
    
    sessions = await get_market_sessions()
    session_data = next((s for s in sessions if s['name'] == session_name), None)
    
    open_ist = utc_to_ist(session_data['open'])
    close_ist = utc_to_ist(session_data['close'])
    
    text = (
        f"📊 *Editing Session:* {session_name}\n\n"
        f"🟢 **Current Open:** `{open_ist}` IST\n"
        f"🔴 **Current Close:** `{close_ist}` IST\n\n"
        f"Select which field you want to update:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🟢 Set Open Time", callback_data="field_open")],
        [InlineKeyboardButton("🔴 Set Close Time", callback_data="field_close")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return ADMIN_EDIT_FIELD

async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Waits for the follow up message."""
    query = update.callback_query
    await query.answer()
    
    field = query.data.replace("field_", "")
    context.user_data['editing_field'] = field
    session = context.user_data['editing_session']
    
    text = (
        f"📝 *Update {session} {field.capitalize()}*\n\n"
        f"Send the new time in **IST** (`HH:MM`).\n"
        f"Example: `09:30`"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return ADMIN_TYPING_TIME

async def save_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves and returns to the session list message."""
    ist_time = update.message.text.strip()
    session = context.user_data.get('editing_session')
    field = context.user_data.get('editing_field')
    
    if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", ist_time):
        await update.message.reply_text("❌ *Invalid format!* Please send time as `HH:MM`.")
        return ADMIN_TYPING_TIME

    utc_time = ist_to_utc(ist_time)
    
    success = False
    if field == "open":
        success = await update_market_session(session, open_time=utc_time)
    else:
        success = await update_market_session(session, close_time=utc_time)
        
    if success:
        await update.message.reply_text(f"✅ *Saved {session}:* {field} is now `{ist_time}` IST.")
    else:
        await update.message.reply_text("❌ Error saving to database.")

    # Return to sessions list
    return await admin_main_via_command(update, context)

async def admin_main_via_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper for returning to menu via a new text message."""
    sessions = await get_market_sessions()
    text = "⚙️ *Admin: Market Sessions (IST)*\n\n"
    keyboard = []
    
    for s in sessions:
        name = s['name']
        open_ist = utc_to_ist(s['open'])
        close_ist = utc_to_ist(s['close'])
        text += f"📍 **{name}:** `{open_ist}` - `{close_ist}`\n"
    
    text += "\nSelect a session to modify its timing:"
    
    row = []
    for s in sessions:
        name = s['name']
        row.append(InlineKeyboardButton(name, callback_data=f"edit_session_{name}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Settings", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return ADMIN_SESSIONS

async def cancel_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        return await settings_command(update, context)
    return ConversationHandler.END

def get_settings_handlers():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("settings", settings_command)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(admin_main, pattern="^admin_main$"),
                CallbackQueryHandler(settings_callback, pattern="^toggle_")
            ],
            ADMIN_SESSIONS: [
                CallbackQueryHandler(select_field, pattern="^edit_session_"),
                CallbackQueryHandler(cancel_config, pattern="^back_to_main$")
            ],
            ADMIN_EDIT_FIELD: [
                CallbackQueryHandler(ask_time, pattern="^field_"),
                CallbackQueryHandler(admin_main, pattern="^admin_main$")
            ],
            ADMIN_TYPING_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_time)
            ]
        },
        fallbacks=[CommandHandler("settings", settings_command), CallbackQueryHandler(cancel_config, pattern="^back_to_main$")],
        per_message=False
    )
    return [conv_handler]
