import requests
import yfinance as yf
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

DEFENSIVE = ["FMCG", "Pharma", "IT"]
CYCLICAL = ["Metal", "Infra", "Realty", "Auto", "Energy", "Bank", "PSU Bank"]

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_change(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="2d")

    if len(hist) < 2:
        return None

    current = hist["Close"].iloc[-1]
    previous = hist["Close"].iloc[-2]

    return round(((current - previous) / previous) * 100, 2)

def heat_emoji(change):
    if change > 1.5:
        return "🟢🟢"
    elif change > 0:
        return "🟢"
    elif change > -1.5:
        return "🔴"
    else:
        return "🔴🔴"

if __name__ == "__main__":

    ist = pytz.timezone("Asia/Kolkata")
    time_now = datetime.now(ist).strftime("%d %b %Y  %I:%M %p IST")

    sector_data = {}

    for name, symbol in SECTORS.items():
        change = get_change(symbol)
        if change is not None:
            sector_data[name] = change

    if not sector_data:
        send_message("Sector data unavailable.")
        exit()

    green = sum(1 for v in sector_data.values() if v > 0)
    red = sum(1 for v in sector_data.values() if v <= 0)

    breadth = round((green / len(sector_data)) * 100, 1)

    leader = max(sector_data, key=sector_data.get)
    weakest = min(sector_data, key=sector_data.get)

    # Risk Logic
    if red >= 9:
        risk = "HIGH 🔥"
    elif red >= 6:
        risk = "MODERATE ⚠️"
    else:
        risk = "LOW 🟢"

    # Defensive vs Cyclical
    defensive_avg = sum(sector_data[s] for s in DEFENSIVE if s in sector_data) / len(DEFENSIVE)
    cyclical_avg = sum(sector_data[s] for s in CYCLICAL if s in sector_data) / len(CYCLICAL)

    if defensive_avg > cyclical_avg:
        rotation = "Money moving to DEFENSIVE sectors 🛡️"
    else:
        rotation = "Money rotating to CYCLICAL sectors 🚀"

    message = f"""📊 Sector Heatmap
📅 {time_now}

Breadth: {green} Green | {red} Red ({breadth}% positive)
Risk Level: {risk}

Sector        Chg%
------------------------"""

    for sector, change in sector_data.items():
        message += f"\n{heat_emoji(change)} {sector:<10} {change}%"

    message += f"""

📌 Rotation Insight
🔥 Leader: {leader} ({sector_data[leader]}%)
❄️ Weakest: {weakest} ({sector_data[weakest]}%)

{rotation}
"""

    # Extreme Alert
    if red >= 10:
        message += "\n🚨 ALERT: Broad Market Selloff!"

    send_message(message)
