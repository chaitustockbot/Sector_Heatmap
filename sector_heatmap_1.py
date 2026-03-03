import requests
import yfinance as yf
import os
import time
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# -----------------------------
# Sector Mapping
# -----------------------------
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


# -----------------------------
# Telegram Sender
# -----------------------------
def send_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram Error:", e)


# -----------------------------
# Bulk Sector Data Fetch
# -----------------------------
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

    except Exception as e:
        print("Bulk fetch failed:", e)
        return None


# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":

    try:
        now = datetime.now().strftime("%d %b %Y %I:%M %p IST")

        symbols = list(SECTORS.values())
        changes = get_all_changes(symbols)

        if not changes:
            send_message("⚠️ Sector data unavailable right now.")
            exit()

        green = 0
        red = 0
        message = f"📊 Sector Heatmap\n🕒 {now}\n\n"

        for name, symbol in SECTORS.items():
            change = changes.get(symbol)

            if change is None:
                continue

            if change >= 0:
                indicator = "🟢"
                green += 1
            else:
                indicator = "🔴"
                red += 1

            message += f"{indicator} {name}: {change}%\n"

        message += f"\n🟢 Green: {green} | 🔴 Red: {red}"

        # Rotation Signal Logic
        if red >= 8:
            message += "\n\n📌 Broad Selloff — Most sectors declining"
        elif green >= 8:
            message += "\n\n📌 Broad Rally — Most sectors advancing"
        else:
            message += "\n\n📌 Mixed Market — Sector rotation ongoing"

        send_message(message)

    except Exception as e:
        print("Main Error:", e)
        send_message("⚠️ Sector Heatmap Bot Error")
