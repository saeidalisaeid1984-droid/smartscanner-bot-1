import requests
import time
import os
from datetime import datetime

# =============================
# CONFIG (Environment Variables)
# =============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DEX_API = "https://api.dexscreener.com/latest/dex/search?q=BSC"

SCAN_INTERVAL = 60  # seconds

# Thresholds (احترافية – قابلة للتطوير لاحقًا)
MIN_LIQUIDITY = 20000       # $
MIN_VOLUME_5M = 15000      # $
VOLUME_SPIKE_X = 2.5
PRICE_CHANGE_PRE = 3       # %
PRICE_CHANGE_PUMP = 10     # %

# Memory (عشان ما يكرر)
seen_tokens = set()

# =============================
# Telegram
# =============================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=10)

# =============================
# DexScreener Fetch
# =============================
def fetch_pairs():
    try:
        r = requests.get(DEX_API, timeout=15)
        return r.json().get("pairs", [])
    except:
        return []

# =============================
# Core Logic
# =============================
def analyze(pair):
    try:
        token = pair["baseToken"]["symbol"]
        address = pair["pairAddress"]
        liquidity = pair["liquidity"]["usd"]
        volume5m = pair["volume"]["m5"]
        price_change = pair["priceChange"]["m5"]
        price = pair["priceUsd"]

        if liquidity < MIN_LIQUIDITY:
            return

        # -------- PRE-PUMP --------
        if volume5m >= MIN_VOLUME_5M and price_change >= PRICE_CHANGE_PRE:
            key = f"PRE-{address}"
            if key not in seen_tokens:
                seen_tokens.add(key)

                send(
                    f"🟡 <b>Pre-Pump Detected</b>\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"🪙 Token: <b>{token}</b>\n"
                    f"🌐 Network: BSC\n"
                    f"💧 Liquidity: ${liquidity:,.0f}\n"
                    f"📊 Volume (5m): ${volume5m:,.0f}\n"
                    f"📈 Price Change: +{price_change}%\n"
                    f"💲 Price: ${price}\n\n"
                    f"⚠️ <i>No recommendation – Early monitoring</i>"
                )

        # -------- EXPLOSION --------
        if price_change >= PRICE_CHANGE_PUMP and volume5m >= MIN_VOLUME_5M * VOLUME_SPIKE_X:
            key = f"PUMP-{address}"
            if key not in seen_tokens:
                seen_tokens.add(key)

                entry1 = price
                entry2 = round(float(price) * 0.97, 8)
                stop = round(float(price) * 0.90, 8)

                send(
                    f"🔴 <b>ALPHA EXPLOSION ALERT</b> 🚀\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"🪙 Token: <b>{token}</b>\n"
                    f"🌐 Network: BSC\n"
                    f"💧 Liquidity: ${liquidity:,.0f}\n"
                    f"📊 Volume (5m): ${volume5m:,.0f}\n"
                    f"📈 Momentum: +{price_change}%\n\n"
                    f"🎯 <b>Entry</b>\n"
                    f"• Entry 1: {entry1}\n"
                    f"• Entry 2: {entry2}\n\n"
                    f"🎯 <b>Targets</b>\n"
                    f"• TP1: +20%\n"
                    f"• TP2: +40%\n"
                    f"• TP3: Moon 🌕 (Momentum based)\n\n"
                    f"🛑 Stop-Loss: {stop}\n\n"
                    f"🧠 <i>Smart money volume confirmed</i>"
                )

    except:
        return

# =============================
# Main Loop
# =============================
def main():
    send(
        "🚀 <b>SmartScannerLY is LIVE</b>\n"
        "━━━━━━━━━━━━━━\n"
        "🌐 Network: BSC\n"
        "🧠 Mode: Alpha Liquidity Intelligence\n"
        "⏱ Timeframes: 5m / 15m\n"
        "⚠️ Alerts: Pre-Pump & Explosion"
    )

    while True:
        pairs = fetch_pairs()
        for pair in pairs:
            analyze(pair)
        time.sleep(SCAN_INTERVAL)

# =============================
if __name__ == "__main__":
    main()
