import requests
import time
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8415018020:AAFXXLuwjWzCmAVm6IjkYb3a27JDx-Yerkc"
CHAT_ID = "5837332461"

DEX_API = "https://api.dexscreener.com/latest/dex/pairs/bsc"
BINANCE_SYMBOLS_API = "https://api.binance.com/api/v3/exchangeInfo"

CHECK_INTERVAL = 30  # seconds
MIN_LIQUIDITY = 20000
SCORE_THRESHOLD = 75

seen_pairs = set()
binance_symbols = set()

# =========================
# TELEGRAM
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=10)

# =========================
# BINANCE
# =========================
def load_binance_symbols():
    global binance_symbols
    try:
        r = requests.get(BINANCE_SYMBOLS_API, timeout=15)
        data = r.json()
        for s in data.get("symbols", []):
            binance_symbols.add(s["baseAsset"])
    except:
        pass

def on_binance(symbol):
    return symbol.upper() in binance_symbols

# =========================
# DEX
# =========================
def fetch_pairs():
    try:
        r = requests.get(DEX_API, timeout=15)
        return r.json().get("pairs", [])
    except:
        return []

# =========================
# SCORE
# =========================
def score_pair(pair):
    score = 0
    liq = pair.get("liquidity", {}).get("usd", 0)
    vol5 = pair.get("volume", {}).get("m5", 0)
    vol15 = pair.get("volume", {}).get("m15", 0)
    pc5 = pair.get("priceChange", {}).get("m5", 0)

    if liq >= 50000: score += 30
    elif liq >= 20000: score += 20

    if vol5 >= 50000: score += 25
    elif vol5 >= 20000: score += 15

    if vol15 >= 80000: score += 10

    if 2 <= pc5 <= 12: score += 20

    return score

# =========================
# ANALYZE
# =========================
def analyze(pair):
    try:
        base = pair["baseToken"]["symbol"]
        address = pair["pairAddress"]

        if address in seen_pairs:
            return

        liq = pair["liquidity"]["usd"]
        if liq < MIN_LIQUIDITY:
            return

        score = score_pair(pair)
        if score < SCORE_THRESHOLD:
            return

        seen_pairs.add(address)

        price = pair.get("priceUsd", "N/A")
        vol5 = pair.get("volume", {}).get("m5", 0)
        vol15 = pair.get("volume", {}).get("m15", 0)
        pc5 = pair.get("priceChange", {}).get("m5", 0)

        now_utc = datetime.now(timezone.utc)
        now_txt = now_utc.strftime("%Y-%m-%d %H:%M UTC")

        binance_status = "✔️ مدرجة في Binance" if on_binance(base) else "❌ غير مدرجة في Binance"

        send(
            f"🤖 <b>SmartScannerLY v1.0</b>\n"
            f"🟡 <b>إنذار مبكر – قبل الانفجار</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🪙 العملة: <b>{base}</b>\n"
            f"🌐 الشبكة: BSC\n"
            f"🏪 المنصات:\n"
            f"• DexScreener\n"
            f"• {binance_status}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💧 السيولة: ${liq:,.0f}\n"
            f"📊 الفوليوم 5د: ${vol5:,.0f}\n"
            f"📊 الفوليوم 15د: ${vol15:,.0f}\n"
            f"📈 التغير 5د: +{pc5}%\n"
            f"💲 السعر: ${price}\n"
            f"━━━━━━━━━━━━━━\n"
            f"🧠 التقييم: <b>{score}/100</b>\n"
            f"🕒 وقت الإشارة: {now_txt}\n"
            f"⚠️ <i>مراقبة فقط – القرار عليك</i>"
        )
    except:
        return

# =========================
# MAIN
# =========================
def run():
    load_binance_symbols()
    send("🚀 <b>SmartScannerLY v1.0 شغّال</b>\n📡 BSC | Pre-Pump Alpha فقط")
    while True:
        for p in fetch_pairs():
            analyze(p)
        time.sleep(CHECK_INTERVAL)

run()
