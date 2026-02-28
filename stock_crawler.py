#!/usr/bin/env python3
"""US Stock Daily - 57 Tickers + AI News via Felo"""
import os, requests, time
from datetime import datetime

STOCKS = ["ADBE","FISV","AMZN","CHYM","VKTX","FIG","ONDS","EOSE","NVTS","IGV","U","SNOW","NBIS","IREN","CRWV","PLTR","MSFT","FCX","TSLA","SMR","AVGO","ORCL","SE","MRVL","LEU","CELH","OKLO","NU","TSM","RBRK","CAVA","ACVA","GRAB","BROS","TMDX","KLAR","CRM","GLW","NFLX","KTOS","VRT","VST","CRDO","CDLR","S","AMD","GOOG","NVDA","ALAB","OSCR","PYPL","BYRN","IOT","GLXY","CAN","BRZE","GSHD"]

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
FELO_API_KEY = os.environ.get("FELO_API_KEY", "")

def get_stock(symbol):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        d = r.json()
        if "chart" in d and d["chart"]["result"]:
            m = d["chart"]["result"][0]["meta"]
            p, c = m.get("regularMarketPrice",0), m.get("previousClose",0)
            if p and c: return {"s":symbol,"p":round(p,2),"c":round(p-c,2),"cp":round((p-c)/c*100,2),"ok":1}
    except: pass
    return {"s":symbol,"ok":0}

def get_felo_news(query):
    """Get AI-powered news via Felo API"""
    if not FELO_API_KEY:
        return []
    
    try:
        url = "https://api.felo.ai/v2/chat"
        headers = {
            "Authorization": f"Bearer {FELO_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": f"Search for latest {query} news today. Give me 3 short headlines with sources."}
            ],
            "search": True,
            "stream": False
        }
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            # Extract content from Felo response
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.split("\n")[:3] if content else []
    except Exception as e:
        print(f"Felo error: {e}")
    return []

def main():
    print(f"Fetching {len(STOCKS)} stocks...")
    results = [get_stock(s) for s in STOCKS]
    ok = [r for r in results if r.get("ok")]
    ok.sort(key=lambda x:x["cp"], reverse=True)
    
    now = datetime.now().strftime("%m/%d %H:%M")
    msg = f"📈 **US Stock Daily** - {now}\n"
    msg += "```\n"
    msg += f"{'Ticker':<8} {'Price':>10} {'Change':>10} {'%':>8}\n"
    msg += "-"*40 + "\n"
    
    for r in ok:
        sign = "+" if r["cp"] > 0 else ""
        msg += f"{r['s']:<8} ${r['p']:>9.2f} {sign}{r['c']:>8.2f} {sign}{r['cp']:>6.2f}%\n"
    
    msg += "```\n"
    
    gain = [r for r in ok if r["cp"]>0]
    loss = [r for r in ok if r["cp"]<0]
    msg += f"📊 **Summary:** {len(gain)} ▲ | {len(loss)} ▼\n"
    
    if gain[:3]:
        msg += "🟢 **Top Gainers:** " + ", ".join([f"{r['s']} +{r['cp']}%" for r in gain[:3]]) + "\n"
    if loss[-3:]:
        msg += "🔴 **Top Losers:** " + ", ".join([f"{r['s']} {r['cp']}%" for r in loss[-3:]]) + "\n"
    
    # Get AI news
    if FELO_API_KEY:
        msg += "\n🤖 **AI Market News:**\n"
        news = get_felo_news("US stock market today")
        for n in news:
            if n.strip():
                msg += n.strip()[:200] + "\n"
    
    if len(msg) <= 2000 and WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={"content":msg}, timeout=10)
            print("✅ Sent to Discord!")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(msg[:500])

if __name__=="__main__": main()
