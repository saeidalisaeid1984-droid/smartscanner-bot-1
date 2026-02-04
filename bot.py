import os
import time
import requests

# ====== ENV VARIABLES ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ====== TELEGRAM ALERT ======
def send_alert(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN or CHAT_ID missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload)
    print("📨 Telegram response:", r.text)

# ====== MAIN LOOP ======
def main():
    print("🚀 SmartScannerLY Bot started")
    send_alert(
        "🚀 <b>SmartScannerLY Bot is LIVE</b>\n"
        "🕊 Network: <b>BSC</b>\n"
        "📡 Mode: <b>Early Liquidity Monitor</b>\n"
        "⏱ Timeframes: 5m / 15m\n"
        "⚠️ Alerts: <i>Pre-Pump & Pump</i>"
    )

    while True:
        time.sleep(60)  # keep alive

# ====== RUN ======
if __name__ == "__main__":
    main()
