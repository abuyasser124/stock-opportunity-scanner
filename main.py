from fastapi import FastAPI
import requests
import os

app = FastAPI()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")

# -------------------------------
# جلب الأسهم النشطة من Polygon
# -------------------------------
def get_active_stocks():
    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={POLYGON_API_KEY}"
    res = requests.get(url).json()
    tickers = res.get("tickers", [])
    return [t["ticker"] for t in tickers[:100]]  # أول 100 سهم

# -------------------------------
# فلتر شرعي بسيط (مبدئي)
# -------------------------------
def halal_filter(symbol):
    url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}"
    res = requests.get(url).json()

    if not res:
        return False

    sector = res[0].get("sector", "").lower()

    haram_sectors = [
        "financial",
        "bank",
        "insurance",
        "gambling",
        "alcohol",
        "tobacco"
    ]

    return not any(h in sector for h in haram_sectors)

# -------------------------------
# تحليل بسيط (مبدئي)
# -------------------------------
def analyze_stock(symbol):
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?apiKey={POLYGON_API_KEY}"
    res = requests.get(url).json()

    if "results" not in res:
        return None

    data = res["results"][0]

    price = data["c"]
    volume = data["v"]

    # منطق بسيط
    score = 50
    if volume > 1000000:
        score += 10

    return {
        "symbol": symbol,
        "price": price,
        "volume": volume,
        "score": score
    }

# -------------------------------
# الرادار الرئيسي
# -------------------------------
@app.get("/scan")
def scan_market():
    symbols = get_active_stocks()

    results = []

    for s in symbols:
        if halal_filter(s):
            analysis = analyze_stock(s)
            if analysis:
                results.append(analysis)

    return {
        "count": len(results),
        "results": results[:20]
    }

# -------------------------------
# تحليل سهم واحد
# -------------------------------
@app.get("/analyze/{symbol}")
def analyze_single(symbol: str):
    if not halal_filter(symbol):
        return {"error": "السهم غير متوافق شرعيًا"}

    return analyze_stock(symbol)
