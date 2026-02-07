# ==============================
# SmartScannerLY – Core v1.1 (AR)
# ==============================

BOT_TOKEN = "8415018020:AAFXXLuwjWzCmAVm6IjkYb3a27JDx-Yerkc"
CHAT_ID = "5837332461"

CHECK_INTERVAL_SECONDS = 180
WHALE_SCORE_THRESHOLD = 75
COOLDOWN_HOURS = 6
MIN_WHALE_USDT = 500_000

EXCLUDED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

import requests
import time
from datetime import datetime, timedelta

last_alert_time = {}

# ==============================
# Telegram
# ==============================

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=data)

# ==============================
# Binance API
# ==============================

def get_usdt_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    data = requests.get(url, timeout=10).json()
    return [
        s["symbol"] for s in data["symbols"]
        if s["quoteAsset"] == "USDT"
        and s["status"] == "TRADING"
        and s["symbol"] not in EXCLUDED_SYMBOLS
    ]

def get_trades(symbol):
    url = f"https://api.binance.com/api/v3/trades?symbol={symbol}&limit=50"
    return requests.get(url, timeout=10).json()

def get_klines(symbol, interval="15m", limit=20):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    return requests.get(url, timeout=10).json()

# ==============================
# Whale Detection + Trade Plan
# ==============================

def analyze_symbol(symbol):
    trades = get_trades(symbol)
    whale_value = None

    for t in trades:
        value = float(t["price"]) * float(t["qty"])
        if value >= MIN_WHALE_USDT:
            whale_value = value
            break

    if not whale_value:
        return None

    klines = get_klines(symbol)
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]

    avg_vol = sum(volumes[:-1]) / len(volumes[:-1])
    cur_vol = volumes[-1]

    score = 0
    if whale_value >= MIN_WHALE_USDT:
        score += 30
    if cur_vol >= avg_vol * 3:
        score += 25
    if closes[-1] > max(highs[:-1]):
        score += 20

    if score < WHALE_SCORE_THRESHOLD:
        return None

    entry_low = lows[-1]
    entry_high = closes[-1]
    tp1 = entry_high * 1.03
    tp2 = entry_high * 1.08
    stop = entry_low * 0.97

    return {
        "symbol": symbol,
        "whale": int(whale_value),
        "score": score,
        "entry": (round(entry_low, 6), round(entry_high, 6)),
        "tp1": round(tp1, 6),
        "tp2": round(tp2, 6),
        "stop": round(stop, 6)
    }

# ==============================
# Cooldown
# ==============================

def can_alert(symbol):
    now = datetime.utcnow()
    last = last_alert_time.get(symbol)
    if not last:
        return True
    return now - last >= timedelta(hours=COOLDOWN_HOURS)

# ==============================
# Message Builder (Arabic)
# ==============================

def build_message(d):
    t = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""
🐋 <b>تنبيه حوت – بينانس (فوري)</b>

🪙 <b>الزوج:</b> {d['symbol']}
💰 <b>صفقة حوت:</b> {d['whale']:,} USDT
📊 <b>قوة الإشارة:</b> {d['score']} / 100

🎯 <b>خطة تداول ذكية (اختيارية)</b>
• الدخول: {d['entry'][0]} – {d['entry'][1]}
• الهدف 1: {d['tp1']}
• الهدف 2: {d['tp2']}
• إيقاف الخسارة: {d['stop']}
• المخاطرة: متوسطة

⏱ <b>الوقت:</b> {t}
🕊 <i>تنبيه آلي – ليس توصية مالية</i>
"""

# ==============================
# Main Loop
# ==============================

def main():
    send_telegram("🚀 SmartScannerLY شغّال الآن\n🐋 نظام رصد الحيتان مفعّل")
    pairs = get_usdt_pairs()

    while True:
        for sym in pairs:
            try:
                if not can_alert(sym):
                    continue

                data = analyze_symbol(sym)
                if data:
                    send_telegram(build_message(data))
                    last_alert_time[sym] = datetime.utcnow()

            except:
                pass

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
