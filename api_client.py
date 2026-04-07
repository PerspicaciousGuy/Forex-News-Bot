import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"

async def fetch_economic_calendar(from_date=None, to_date=None):
    """
    Fetches economic calendar from FMP.
    from_date and to_date should be in YYYY-MM-DD format.
    """
    if not from_date:
        from_date = datetime.now().strftime("%Y-%m-%d")
    if not to_date:
        to_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"{BASE_URL}/economic_calendar?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching calendar: {response.status}")
                return []

async def fetch_forex_news(limit=5):
    """
    Fetches latest forex news.
    """
    url = f"{BASE_URL}/stock_news?tickers=EURUSD,GBPUSD,USDJPY&limit={limit}&apikey={FMP_API_KEY}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching news: {response.status}")
                return []
