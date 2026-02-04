import os
import time
import requests

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DEX_API = "https://api.dexscreener.com/latest/dex/search?q=bsc"

SCAN_INTERVAL = 60  # seconds

# Filters (Pre-Pump)
MIN_LIQUIDITY = 20000        # $
MIN_VOLUME_5M = 15000        # $
MIN_PRICE_CHANGE_5M = 5      # %

sent_pairs = set()

# ================== TELEGRAM ==================
def send_alert(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN or CHAT_ID missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        print("📩 Telegram:", r.status_code)
    except Exception as e:
        print("Telegram error:", e)

# ================== DATA ==================
def fetch_pairs():
    try:
        r = requests.get(DEX_API, timeout=15)
        return r.json().get("pairs", [])
    except Exception as e:
        print("API error:", e)
        return []

# ================== SCANNER ==================
def scan_market():
    pairs = fetch_pairs()

    for p in pairs:
        try:
            if p.get("chainId") != "bsc":
                continue

            pair_address = p.get("pairAddress")
            if not pair_address or pair_address in sent_pairs:
                continue

            base = p.get("baseToken", {})
            token_name = base.get("name", "Unknown")
            token_symbol = base.get("symbol", "N/A")

            price_change_5m = p.get("priceChange", {}).get("m5", 0)
            volume_5m = p.get("volume", {}).get("m5", 0)
            liquidity = p.get("liquidity", {}).get("usd", 0)
            dex = p.get("dexId", "DEX")

            if (
                liquidity >= MIN_LIQUIDITY
                and volume_5m >= MIN_VOLUME_5M
                and price_change_5m >= MIN_PRICE_CHANGE_5M
            ):
                message = f"""
🚨 <b>Pre-Pump Alpha Alert</b>

🪙 <b>Token:</b> {token_name} ({token_symbol})
🌐 <b>Network:</b> BSC
🏦 <b>DEX:</b> {dex}

💧 <b>Liquidity:</b> ${liquidity:,.0f}
📊 <b>Volume (5m):</b> ${volume_5m:,.0f}
📈 <b>Price Change (5m):</b> +{price_change_5m}%

⚠️ <i>Early movement detected – No recommendation yet</i>
🧠 <i>راقب السلوك قبل الانفجار</i>
"""
                send_alert(message)
                sent_pairs.add(pair_address)

        except Exception as e:
            print("Scan error:", e)

# ================== MAIN ==================
def main():
    print("🚀 SmartScannerLY started")

    send_alert(
        "🚀 <b>SmartScannerLY Bot is LIVE</b>\n\n"
        "🌐 Network: BSC\n"
        "🧠 Mode: Pre-Pump Alpha Scanner\n"
        "⏱ Timeframes: 5m / 15m\n"
        "⚠️ Alerts: Early Detection (No Signals)"
    )

    while True:
        scan_market()
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
