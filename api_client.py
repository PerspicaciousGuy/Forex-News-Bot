import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging to be visible in Koyeb / Server logs
logger = logging.getLogger(__name__)

FMP_API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"

async def fetch_economic_calendar(from_date=None, to_date=None):
    """
    Fetches economic calendar from FMP.
    from_date and to_date should be in YYYY-MM-DD format.
    """
    if not FMP_API_KEY:
        logger.error("❌ FMP_API_KEY is missing! Check your environment variables.")
        return []

    # Get a 3-day window by default to ensure we don't miss anything due to timezones
    if not from_date:
        from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if not to_date:
        to_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    url = f"{BASE_URL}/economic_calendar?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
    
    logger.info(f"🔍 Fetching calendar from {from_date} to {to_date}...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Fetched {len(data)} calendar events.")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Error fetching calendar: {response.status} - {error_text}")
                    return []
        except Exception as e:
            logger.error(f"⚠️ Exception during calendar fetch: {e}")
            return []

async def fetch_forex_news(limit=10):
    """
    Fetches latest forex-related news using multiple tickers for better coverage.
    """
    if not FMP_API_KEY:
        logger.error("❌ FMP_API_KEY is missing! Check your environment variables.")
        return []

    # Using stock_news with general forex-related tickers for broader coverage
    url = f"{BASE_URL}/stock_news?tickers=EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,USDCHF,NZDUSD&limit={limit}&apikey={FMP_API_KEY}"
    
    logger.info("🗞️ Fetching latest forex news...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Fetched {len(data)} news items.")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Error fetching news: {response.status} - {error_text}")
                    return []
        except Exception as e:
            logger.error(f"⚠️ Exception during news fetch: {e}")
            return []
