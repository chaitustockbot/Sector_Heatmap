import requests
import yfinance as yf
import os
from flask import Flask

app = Flask(__name__)

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

def run_bot():
    sector_data = {}

    for name, symbol in SECTORS.items():
        hist = yf.Ticker(symbol).history(period="2d")
        if len(hist) >= 2:
            change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2]) * 100
            sector_data[name] = round(change, 2)

    green = sum(1 for v in sector_data.values() if v > 0)
    red = sum(1 for v in sector_data.values() if v <= 0)

    message = f"📊 Sector Heatmap\n\n{green} Green | {red} Red\n"

    for sector, change in sector_data.items():
        circle = "🟢" if change > 0 else "🔴"
        message += f"{circle} {sector}: {change}%\n"

    send_message(message)

@app.route("/")
def home():
    return "Bot Running!"

@app.route("/run")
def trigger():
    run_bot()
    return "Sector Heatmap Sent!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
