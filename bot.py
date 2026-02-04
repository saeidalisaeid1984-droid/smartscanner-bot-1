import requests
import time

# ==============================
# CONFIG
# ==============================
BOT_TOKEN = "8415018020:AAFXXLuwjWzCmAVm6IjkYb3a27JDx-Yerkc"
CHAT_ID = "5837332461"

DEX_API = "https://api.dexscreener.com/latest/dex/pairs/bsc"

MIN_LIQUIDITY = 20000
CHECK_INTERVAL = 30  # seconds

seen_tokens = set()

# ==============================
# TELEGRAM
# ==============================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=10)

# ==============================
# FETCH DATA
# ==============================
def fetch_pairs():
    try:
        r = requests.get(DEX_API, timeout=15)
        return r.json().get("pairs", [])
    except:
        return []

# ==============================
# SCORE SYSTEM
# ==============================
def calculate_score(pair):
    score = 0

    liquidity = pair.get("liquidity", {}).get("usd", 0)
    volume5m = pair.get("volume", {}).get("m5", 0)
    price_change = pair.get("priceChange", {}).get("m5", 0)
    created_at = pair.get("pairCreatedAt", 0)

    # Liquidity
    if liquidity >= 50000:
        score += 30
    elif liquidity >= 20000:
        score += 20

    # Volume
    if volume5m >= 50000:
        score += 30
    elif volume5m >= 20000:
        score += 20

    # Price movement (healthy)
    if 3 <= price_change <= 15:
        score += 20

    # New pair bonus
    if created_at:
        score += 20

    return score

# ==============================
# ANALYZE
# ==============================
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

        score = calculate_score(pair)

        key = f"SCORE-{address}"
        if score >= 75 and key not in seen_tokens:
            seen_tokens.add(key)

            send(
                f"🟡 <b>إنذار مبكر (Alpha)</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"🪙 <b>التوكن:</b> {token}\n"
                f"🌐 الشبكة: BSC\n"
                f"🧠 التقييم: <b>{score}/100</b>\n"
                f"💧 السيولة: ${liquidity:,.0f}\n"
                f"📊 الفوليوم (5د): ${volume5m:,.0f}\n"
                f"📈 التغير السعري: +{price_change}%\n"
                f"💲 السعر: ${price}\n"
                f"⚠️ <i>مراقبة فقط – لا دخول بعد</i>"
            )

    except:
        return

# ==============================
# MAIN LOOP
# ==============================
def run():
    send("🚀 <b>بوت Alpha Scanner شغّال</b>\n📡 BSC | إنذارات ذكية فقط")
    while True:
        pairs = fetch_pairs()
        for pair in pairs:
            analyze(pair)
        time.sleep(CHECK_INTERVAL)

# ==============================
# START
# ==============================
run()
