import requests
import time

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
CHAT_ID = "PUT_YOUR_CHAT_ID_HERE"

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

def main():
    send_alert("🚀 SmartScannerLY Bot is running\n🕊 BSC Early Alert system active")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
