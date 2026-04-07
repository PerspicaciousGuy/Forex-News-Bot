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
    Fetches economic calendar from Forex Factory (Free Source).
    """
    # Note: Forexfactory doesn't use from/to in this JSON, it gives the whole week.
    url = "https://nfs.forexfactory.com/ff_calendar_thisweek.json"
    
    logger.info("📊 Fetching FREE economic calendar from Forex Factory...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    # Standardize field names to match the rest of the bot
                    standardized_data = []
                    today = datetime.now().strftime("%m-%d-%Y")
                    
                    for event in data:
                        # ForexFactory JSON fields: title, country, date, time, impact, forecast, previous
                        standardized_data.append({
                            "event": event.get("title"),
                            "currency": event.get("country"),
                            "date": f"{event.get('date')} {event.get('time')}",
                            "impact": event.get("impact"),
                            "actual": "", # FF JSON usually doesn't have live 'actual' in this endpoint
                            "previous": event.get("previous"),
                        })
                    logger.info(f"✅ Fetched {len(standardized_data)} free calendar events.")
                    return standardized_data
                else:
                    logger.error(f"❌ Error fetching FF calendar: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"⚠️ FF Fetch Exception: {e}")
            return []

async def fetch_forex_news(limit=10):
    """
    Fetches latest forex news from ForexLive RSS feed (Free Source).
    """
    url = "https://www.forexlive.com/feed/news"
    
    logger.info("🗞️ Fetching FREE forex news from ForexLive RSS...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    
                    # Simple manual parsing for RSS items (avoiding extra dependencies)
                    import re
                    items = re.findall(r'<item>(.*?)</item>', xml_data, re.DOTALL)
                    
                    news_items = []
                    for item in items[:limit]:
                        title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                        link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                        
                        if title_match and link_match:
                            news_items.append({
                                "title": title_match.group(1).replace("<![CDATA[", "").replace("]]>", ""),
                                "url": link_match.group(1).strip()
                            })
                    
                    logger.info(f"✅ Fetched {len(news_items)} free news items.")
                    return news_items
                else:
                    logger.error(f"❌ Error fetching RSS news: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"⚠️ RSS Fetch Exception: {e}")
            return []
