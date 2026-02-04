import os
import time
import requests

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DEX_API = "https://api.dexscreener.com/latest/dex/search?q=BSC"

CHECK_INTERVAL = 300  # 5 minutes
MIN_VOLUME_5M = 100000   # 100k$
MIN_LIQUIDITY = 50000    # 50k$
MIN_PRICE_CHANGE = 8     # %

sent_tokens = set()

# ================== TELEGRAM ==================
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
    requests.post(url, json=payload)

# ================== DEXSCREENER ==================
def fetch_pairs():
    try:
        r = requests.get(DEX_API, timeout=15)
        data = r.json()
        return data.get("pairs", [])
    except Exception as e:
        print("Dex error:", e)
        return []

# ================== SCANNER ==================
def scan():
    pairs = fetch_pairs()

    for p in pairs:
        try:
            if p.get("chainId") != "bsc":
                continue

            token = p["baseToken"]["symbol"]
            pair_address = p["pairAddress"]

            if pair_address in sent_tokens:
                continue

            price_change = p["priceChange"]["m5"]
            volume = p["volume"]["m5"]
            liquidity = p["liquidity"]["usd"]

            if (
                price_change >= MIN_PRICE_CHANGE
                and volume >= MIN_VOLUME_5M
                and liquidity >= MIN_LIQUIDITY
            ):
                msg = f"""
🚨 <b>Early Alpha Alert</b>

🪙 <b>Token:</b> {token}
🌐 <b>Network:</b> BSC
💧 <b>Liquidity:</b> ${liquidity:,.0f}
📊 <b>Volume (5m):</b> ${volume:,.0f}
📈 <b>Price Change (5m):</b> +{price_change}%

⚠️ <i>Early movement detected</i>
📡 Monitoring for confirmation...
"""
                send_alert(msg)
                sent_tokens.add(pair_address)

        except Exception as e:
            print("Scan error:", e)

# ================== MAIN ==================
def main():
    send_alert("🚀 <b>SmartScannerLY</b> started\n🕵️‍♂️ BSC Early Alpha Scanner ACTIVE")
    while True:
        scan()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
