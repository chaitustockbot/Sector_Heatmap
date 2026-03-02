import requests
import yfinance as yf
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# NSE Sector Indices
SECTORS = {
    "Metal": "^CNXMETAL",
    "IT": "^CNXIT",
    "Pharma": "^CNXPHARMA",
    "FMCG": "^CNXFMCG",
    "Bank": "^NSEBANK",
    "Infra": "^CNXINFRA",
    "Realty": "^CNXREALTY",
    "Energy": "^CNXENERGY",
    "PSU Bank": "^CNXPSUBANK",
    "Auto": "^CNXAUTO",
    "Media": "^CNXMEDIA"
}


def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)


def get_sector_change(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="2d")

    if len(hist) < 2:
        return None

    current = hist["Close"].iloc[-1]
    previous = hist["Close"].iloc[-2]

    change_percent = ((current - previous) / previous) * 100
    return round(change_percent, 2)


if __name__ == "__main__":

    ist = pytz.timezone("Asia/Kolkata")
    time_now = datetime.now(ist).strftime("%d %b %Y  %I:%M %p IST")

    sector_changes = {}

    for name, symbol in SECTORS.items():
        change = get_sector_change(symbol)
        if change is not None:
            sector_changes[name] = change

    if not sector_changes:
        send_message("Sector data not available.")
        exit()

    green = sum(1 for v in sector_changes.values() if v > 0)
    red = sum(1 for v in sector_changes.values() if v <= 0)

    circles = "🟢 " * green + "🔴 " * red

    # Find leading & weakest
    leader = max(sector_changes, key=sector_changes.get)
    weakest = min(sector_changes, key=sector_changes.get)

    message = f"""📊 Sector Heatmap
📅 {time_now}

{circles}
{green} Green  {red} Red  ({len(sector_changes)} sectors)

Sector        Chg%
------------------------"""

    for sector, change in sector_changes.items():
        arrow = "▲" if change > 0 else "▼"
        message += f"\n{sector:<12} {arrow} {change}%"

    message += f"""

📌 Rotation Signal
📉 Broad selloff — {red}/{len(sector_changes)} sectors declining
🔥 {leader} leading {sector_changes[leader]}%
❄️ {weakest} weakest {sector_changes[weakest]}%

🤖 Every 5 min | NSE via Yahoo Finance
"""

    send_message(message)
