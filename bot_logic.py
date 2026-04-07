from telegram import Update
from telegram.ext import ContextTypes
from api_client import fetch_economic_calendar, fetch_forex_news
from datetime import datetime
import os

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command.
    """
    message = (
        "👋 Welcome to the **Forex High Impact Bot**!\n\n"
        "I'll keep you updated with the latest economic calendar and high-impact news.\n\n"
        "📜 **Commands:**\n"
        "/calendar - Get today's economic calendar\n"
        "/news - Get the latest high-impact forex news\n\n"
        "I'll also send automatic alerts for high-impact events! 🚀"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

async def calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /calendar command.
    """
    await update.message.reply_text("🔍 Fetching today's economic calendar...")
    
    events = await fetch_economic_calendar()
    
    # If events is None it would mean an error occurred, but our current API returns [] for errors too.
    # We check if it's a list.
    if not isinstance(events, list):
        await update.message.reply_text("❌ There was an error connecting to the news service.")
        return

    if not events:
        await update.message.reply_text("✅ No economic events found for the requested period.")
        return

    # Filter by High and Medium impact (Case-insensitive)
    high_impact_events = [
        e for e in events 
        if str(e.get("impact")).capitalize() in ["High", "Medium"]
    ]
    
    if not high_impact_events:
        await update.message.reply_text("✅ No high or medium impact events scheduled for today.")
        return

    response = "📊 **Economic Calendar (Today)**\n\n"
    # Take the first 10 events
    for event in high_impact_events[:10]:
        impact = str(event.get("impact")).capitalize()
        impact_emoji = "🔴" if impact == "High" else "🟠"
        
        # Parse date safely
        date_str = event.get("date")
        try:
            # FMP format usually: 2026-04-07 09:30:00
            time_str = date_str[11:16] if len(date_str) > 16 else date_str
        except:
            time_str = "??:??"

        currency = event.get("currency")
        event_name = event.get("event")
        
        response += (
            f"{impact_emoji} `{time_str}` **{currency}** - {event_name}\n"
            f"   Actual: `{event.get('actual') or '-'}` | Prev: `{event.get('previous') or '-'}`\n\n"
        )

    await update.message.reply_text(response, parse_mode="Markdown")

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /news command.
    """
    await update.message.reply_text("🗞️ Fetching the latest news...")
    
    news_items = await fetch_forex_news()
    if not news_items:
        await update.message.reply_text("❌ No recent news found.")
        return

    response = "🗞️ **Latest Forex News**\n\n"
    for news in news_items:
        title = news.get("title")
        url = news.get("url")
        response += f"• [{title}]({url})\n\n"

    await update.message.reply_text(response, parse_mode="Markdown", disable_web_page_preview=True)
