import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "forex_bot_db"
COLLECTION_NAME = "subscribers"

# Initialize Client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
subscribers = db[COLLECTION_NAME]
calendar_collection = db["economic_calendar"]
sessions_collection = db["market_sessions"]

# --- DEFAULT MARKET SESSIONS (UTC) ---
DEFAULT_MARKET_SESSIONS = [
    {"name": "Sydney 🇦🇺", "open": "22:00", "close": "06:00"},
    {"name": "Tokyo 🇯🇵", "open": "23:00", "close": "07:00"},
    {"name": "Frankfurt 🇩🇪", "open": "06:00", "close": "14:00"},
    {"name": "London 🇬🇧", "open": "07:00", "close": "15:00"},
    {"name": "New York 🇺🇸", "open": "12:00", "close": "20:00"},
]


# To avoid duplicate alerts within the same minute
SENT_ALERTS_FILE = "sent_market_alerts.txt"

DEFAULT_PREFERENCES = {
    "Sydney 🇦🇺": True,
    "Tokyo 🇯🇵": True,
    "Frankfurt 🇩🇪": True,
    "London 🇬🇧": True,
    "New York 🇺🇸": True
}

async def add_subscriber(chat_id):
    """Adds a chat ID to the database with default preferences."""
    try:
        # Check if already exists
        exists = await subscribers.find_one({"chat_id": chat_id})
        if not exists:
            await subscribers.insert_one({
                "chat_id": chat_id,
                "preferences": DEFAULT_PREFERENCES.copy()
            })
            logger.info(f"New subscriber added: {chat_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error adding subscriber {chat_id}: {e}")
        return False

async def get_subscriber_prefs(chat_id):
    """Fetches preferences for a specific subscriber, ensuring all default sessions exist."""
    user = await subscribers.find_one({"chat_id": chat_id})
    
    # Start with a copy of defaults
    prefs = DEFAULT_PREFERENCES.copy()
    
    # Overwrite with saved user preferences if they exist
    if user and "preferences" in user:
        prefs.update(user["preferences"])
        
    return prefs

async def update_subscriber_prefs(chat_id, preferences):
    """Updates session preferences for a user."""
    await subscribers.update_one(
        {"chat_id": chat_id},
        {"$set": {"preferences": preferences}},
        upsert=True
    )

async def get_bot_stats():
    """Fetches general bot statistics."""
    total_users = await subscribers.count_documents({})
    return {"total_users": total_users}

async def remove_subscriber(chat_id):
    """Removes a chat ID from the database."""
    try:
        await subscribers.delete_one({"chat_id": chat_id})
        logger.info(f"Subscriber removed: {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error removing subscriber {chat_id}: {e}")
        return False

async def get_all_subscribers():
    """Returns a list of all chat IDs in the database."""
    try:
        cursor = subscribers.find({}, {"chat_id": 1, "_id": 0})
        results = await cursor.to_list(length=1000)
        return [r["chat_id"] for r in results]
    except Exception as e:
        logger.error(f"Error fetching subscribers: {e}")
        return []

async def get_all_subscribers_data():
    """Returns all subscriber documents."""
    try:
        cursor = subscribers.find({})
        return await cursor.to_list(length=1000)
    except Exception as e:
        logger.error(f"Error fetching subscriber data: {e}")
        return []

# --- ECONOMIC CALENDAR FUNCTIONS ---

async def save_news_events(events):
    """
    Clears the current calendar and saves new events.
    Filter: Only High impact (Red) and Bank Holidays (Grey).
    """
    try:
        # Filter relevant events
        # Note: Forex Factory JSON uses 'High', 'Medium', 'Low', 'Holiday'
        relevant_impacts = ["High", "Holiday"]
        filtered_events = [
            e for e in events 
            if e.get("impact") in relevant_impacts
        ]

        if not filtered_events:
            return 0

        # Replace all existing news
        await calendar_collection.delete_many({})
        await calendar_collection.insert_many(filtered_events)
        logger.info(f"Successfully saved {len(filtered_events)} news events.")
        return len(filtered_events)
    except Exception as e:
        logger.error(f"Error saving news events: {e}")
        return 0

async def get_upcoming_events(current_time_str, date_str):
    """
    Fetches news events for a specific time and date.
    """
    try:
        # We look for events matching the exact hour:minute and date
        # Forex Factory JSON format: date: "Apr 9, 2026", time: "6:00pm"
        # We will normalize this during parsing, but for now we query directly.
        cursor = calendar_collection.find({
            "normalized_date": date_str,
            "normalized_time": current_time_str,
            "impact": "High"
        })
        return await cursor.to_list(length=20)
    except Exception as e:
        logger.error(f"Error fetching upcoming news: {e}")
        return []

async def get_holidays_for_today(date_str):
    """
    Fetches Bank Holidays for a specific date.
    """
    try:
        cursor = calendar_collection.find({
            "normalized_date": date_str,
            "impact": "Holiday"
        })
        return await cursor.to_list(length=10)
    except Exception as e:
        logger.error(f"Error fetching holidays: {e}")
        return []
async def get_market_sessions():
    """Fetches market sessions from DB or returns defaults."""
    count = await sessions_collection.count_documents({})
    if count == 0:
        # Initialize with defaults
        await sessions_collection.insert_many(DEFAULT_MARKET_SESSIONS)
        return DEFAULT_MARKET_SESSIONS
    
    cursor = sessions_collection.find({}, {"_id": 0})
    return await cursor.to_list(length=20)

async def update_market_session(session_name, open_time=None, close_time=None):
    """Updates a specific session's timing."""
    update_data = {}
    if open_time: update_data["open"] = open_time
    if close_time: update_data["close"] = close_time
    
    if not update_data: return False
    
    result = await sessions_collection.update_one(
        {"name": session_name},
        {"$set": update_data}
    )
    return result.modified_count > 0
