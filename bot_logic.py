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
    if not events:
        await update.message.reply_text("❌ Could not fetch calendar at the moment.")
        return

    # Filter by High and Medium impact (if needed)
    high_impact_events = [e for e in events if e.get("impact") in ["High", "Medium"]]
    
    if not high_impact_events:
        await update.message.reply_text("✅ No high-impact events for today.")
        return

    response = "📊 **Economic Calendar (Today)**\n\n"
    for event in high_impact_events[:10]: # Limit to 10 for readability
        impact_emoji = "🔴" if event.get("impact") == "High" else "🟠"
        time_str = event.get("date")[11:16] # HH:MM
        currency = event.get("currency")
        event_name = event.get("event")
        
        response += (
            f"{impact_emoji} {time_str} {currency} - {event_name}\n"
            f"   Actual: {event.get('actual') or '-'} | Prev: {event.get('previous') or '-'}\n\n"
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
