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

async def add_subscriber(chat_id):
    """Adds a chat ID to the database if it doesn't already exist."""
    try:
        # Check if already exists
        exists = await subscribers.find_one({"chat_id": chat_id})
        if not exists:
            await subscribers.insert_one({"chat_id": chat_id})
            logger.info(f"New subscriber added: {chat_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error adding subscriber {chat_id}: {e}")
        return False

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
