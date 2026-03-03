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
    "Media": "NIFTY_MEDIA.NS"
   
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
            threads=False,
            progress=False
        )

        results = {}

        for symbol in symbols:
            try:
                if symbol not in data:
                    results[symbol] = None
                    continue

                hist = data[symbol]

                if len(hist) < 2:
                    results[symbol] = None
                    continue

                current = hist["Close"].iloc[-1]
                previous = hist["Close"].iloc[-2]
                change = ((current - previous) / previous) * 100
                results[symbol] = round(change, 2)

            except Exception:
                results[symbol] = None

        return results

    except Exception:
        return None
