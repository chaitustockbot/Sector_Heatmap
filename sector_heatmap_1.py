import requests
import yfinance as yf
import os
from datetime import datetime

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

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def get_all_changes(symbols):
    try:
        data = yf.download(
            tickers=" ".join(symbols),
            period="2d",
            group_by="ticker",
            threads=False
        )

        results = {}
        for symbol in symbols:
            try:
                hist = data[symbol]
                current = hist["Close"].iloc[-1]
                previous = hist["Close"].iloc[-2]
                change = ((current - previous) / previous) * 100
                results[symbol] = round(change, 2)
            except:
                results[symbol] = None

        return results

    except Exception:
        return None

if __name__ == "__main__":

    now = datetime.now().strftime("%d %b %Y %I:%M %p IST")

    symbols = list(SECTORS.values())
    changes = get_all_changes(symbols)

    if not changes:
        send_message("⚠️ Yahoo rate limited. Try later.")
        exit()

    green = 0
    red = 0

    message = f"📊 Sector Heatmap\n🕒 {now}\n\n"

    for name, symbol in SECTORS.items():
        change = changes.get(symbol)
        if change is None:
            continue

        if change >= 0:
            green += 1
            indicator = "🟢"
        else:
            red += 1
            indicator = "🔴"

        message += f"{indicator} {name}: {change}%\n"

    message += f"\n🟢 {green} | 🔴 {red}"

    send_message(message)
