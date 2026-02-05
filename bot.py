# ==============================
# SmartScannerLY - Core Config
# ==============================

BOT_TOKEN = "8415018020:AAFXXLuwjWzCmAVm6IjkYb3a27JDx-Yerkc"
CHAT_ID = "5837332461"

# --- General Settings ---
CHECK_INTERVAL_SECONDS = 180        # Binance check every 3 minutes
WHALE_SCORE_THRESHOLD = 75
COOLDOWN_HOURS = 6

# --- Excluded Major Coins ---
EXCLUDED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# --- Whale Trade Threshold ---
MIN_WHALE_USDT = 500_000             # 500k USDT

# ==============================
# Imports
# ==============================

import requests
import time
from datetime import datetime, timedelta

# ==============================
# Global Memory (Anti-Spam)
# ==============================

last_alert_time = {}

# ==============================
# Telegram Alert System
# ==============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

# ==============================
# Binance Data Fetchers
# ==============================

def get_usdt_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    data = requests.get(url, timeout=10).json()
    pairs = []

    for s in data["symbols"]:
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING":
            symbol = s["symbol"]
            if symbol not in EXCLUDED_SYMBOLS:
                pairs.append(symbol)
    return pairs

def get_recent_trades(symbol):
    url = f"https://api.binance.com/api/v3/trades?symbol={symbol}&limit=50"
    return requests.get(url, timeout=10).json()

def get_klines(symbol, interval="5m", limit=20):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    return requests.get(url, timeout=10).json()

# ==============================
# Whale Detection Logic
# ==============================

def detect_whale(symbol):
    trades = get_recent_trades(symbol)
    whale_trade = None

    for t in trades:
        trade_value = float(t["price"]) * float(t["qty"])
        if trade_value >= MIN_WHALE_USDT:
            whale_trade = trade_value
            break

    if not whale_trade:
        return None

    klines = get_klines(symbol)
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]

    avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
    current_volume = volumes[-1]

    score = 0
    if whale_trade >= MIN_WHALE_USDT:
        score += 30
    if current_volume >= avg_volume * 3:
        score += 25
    if closes[-1] > max(closes[:-1]):
        score += 20

    if score >= WHALE_SCORE_THRESHOLD:
        return {
            "symbol": symbol,
            "trade_value": int(whale_trade),
            "score": score
        }

    return None

# ==============================
# Cooldown Check
# ==============================

def allowed_to_alert(symbol):
    now = datetime.utcnow()
    last = last_alert_time.get(symbol)

    if not last:
        return True

    return now - last >= timedelta(hours=COOLDOWN_HOURS)

# ==============================
# Alert Builder
# ==============================

def build_message(data):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return f"""
🐋 <b>Binance Whale Alert</b>

🪙 <b>Pair:</b> {data['symbol']}
🏦 <b>Market:</b> Binance Spot
💰 <b>Whale Trade:</b> {data['trade_value']:,} USDT
📊 <b>Whale Score:</b> {data['score']} / 100

🎯 <b>Signal Type:</b> Smart Whale Momentum
⏱ <b>Time:</b> {now}

🕊 <i>Automated signal – not financial advice</i>
"""

# ==============================
# Main Loop
# ==============================

def main():
    send_telegram("🚀 SmartScannerLY Core v1.0 is LIVE\n🐋 Binance Whale Engine Activated")

    pairs = get_usdt_pairs()

    while True:
        for symbol in pairs:
            try:
                if not allowed_to_alert(symbol):
                    continue

                result = detect_whale(symbol)
                if result:
                    message = build_message(result)
                    send_telegram(message)
                    last_alert_time[symbol] = datetime.utcnow()

            except Exception as e:
                pass

        time.sleep(CHECK_INTERVAL_SECONDS)

# ==============================
# Run
# ==============================

if __name__ == "__main__":
    main()
