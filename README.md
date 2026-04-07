# 📈 Forex High-Impact News Bot

A Telegram bot to send high-impact economic alerts and news to groups or channels. Designed for Python and hosting on **Koyeb**.

## 🚀 Features
*   📊 `/calendar`: Current day's economic calendar (Filtered for High/Medium impact).
*   🗞️ `/news`: Latest news for major Forex pairs (EURUSD, GBPUSD, etc.).
*   🚨 **Auto-Alerts**: Scans the calendar every 30 minutes and sends a notification 30-60 mins before any **High Impact** event.

## 🛠️ Setup

### 1. Requirements
*   **Python 3.10+**
*   **Telegram Bot Token**: Get it from [@BotFather](https://t.me/BotFather).
*   **FMP API Key**: Get a free key from [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs/).
*   **Chat ID**: The ID of your group or channel. If it's a public channel, use `@channel_username`. If it's private, you'll need the numeric ID.

### 2. Configuration
1.  Copy `.env.example` to `.env`.
2.  Fill in your `TELEGRAM_BOT_TOKEN`, `FMP_API_KEY`, and `CHAT_ID`.

```bash
TELEGRAM_BOT_TOKEN=123456...
FMP_API_KEY=your_key...
CHAT_ID=@my_forex_channel
```

### 3. Running Locally
```bash
pip install -r requirements.txt
python main.py
```

## 🏗️ Deployment (Koyeb)
1.  Connect your GitHub repository to Koyeb.
2.  Select **Docker** (using the provided `Dockerfile`) or **Native Buildpack** (using the `Procfile`).
3.  Add the environment variables in the Koyeb dashboard.
4.  **Important**: Deploy as a **"Worker"** (no port required).

## 🛡️ License
MIT
