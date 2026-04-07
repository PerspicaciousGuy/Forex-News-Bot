# ==========================================
# 📜 BOT COMMAND MESSAGES
# ==========================================

START_MESSAGE = (
    "👋 Welcome! I am your **Market Session Monitor**.\n\n"
    "I will automatically alert this group when the **London, New York, Tokyo, and Sydney** markets open or close.\n\n"
    "📜 **Commands:**\n"
    "/sessions - Check what's open right now and time left!\n\n"
    "⏰ **What I do automatically:**\n"
    "• 🚨 30-minute Warning before Market Opens\n"
    "• 🟢 Live Market Open Alerts\n"
    "• 🔴 Market Close Alerts\n\n"
    "Sit back and let me keep you on track! 🚀"
)

SESSION_HEADER = "🗺️ **Market Status (Live UTC)**\n\n"
SESSION_FOOTER = "\n🕒 **Current Time**: `{current_time}` UTC"
WEEKEND_MESSAGE = (
    "🛑 **MARKETS CLOSED** 😴\n\n"
    "Forex markets are closed for the weekend. They will re-open for the **Sydney session** at `22:00` UTC on Sunday night! 🚀"
)


# ==========================================
# 🚨 AUTOMATED MARKET ALERTS
# ==========================================

# Automated Market Alerts
WARNING_TEXT = "⏳ **30 MINUTE WARNING** 🚨\n\nThe **{name}** session will open in 30 minutes! Get your charts ready. 📈"
PREP_TEXT = "🔔 **5 MINUTE PREP** ⏱️\n\nThe **{name}** session is opening in just 5 minutes! Finalize your entries. 🚀"
OPEN_TEXT = "🟢 **MARKET OPEN** 🚀\n\nThe **{name}** session is now **OPEN**! High liquidity expected. 💎"
CLOSE_TEXT = "🔴 **MARKET CLOSE** 📉\n\nThe **{name}** session is now **CLOSED**. Volatility may decrease. 😴"

# Special Overlap Enhanced Messages
NY_OPEN_OVERLAP = "🟢 **MARKET OPEN & OVERLAP** 🚀🚀\n\nThe **New York** session is now **OPEN**! The **London/NY Overlap** has begun. Maximum liquidity and volatility expected! 💎💎"
LONDON_CLOSE_OVERLAP = "🔴 **MARKET CLOSE & OVERLAP END** 📉\n\nThe **London** session is now **CLOSED**. The **London/NY Overlap** has ended. Volatility may decrease. 😴"

# Weekend Specific Alerts
WEEKEND_CLOSE_ALERT = "🛑 **WEEKEND CLOSE** 😴\n\nThe New York session has closed. The Forex markets are now **CLOSED** for the weekend. Enjoy your rest, traders! ☕🛋️"
WEEKEND_OPEN_ALERT = "🚀 **MARKETS OPENING** 📈\n\nWelcome back! The new trading week is beginning. Sydney will open in 30 minutes! Get your charts ready. 🗺️📊"
