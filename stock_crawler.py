#!/usr/bin/env python3
"""US Stock Daily Crawler - 57 Tickers + News"""
import os, requests, time
from datetime import datetime

STOCKS = ["ADBE","FISV","AMZN","CHYM","VKTX","FIG","ONDS","EOSE","NVTS","IGV","U","SNOW","NBIS","IREN","CRWV","PLTR","MSFT","FCX","TSLA","SMR","AVGO","ORCL","SE","MRVL","LEU","CELH","OKLO","NU","TSM","RBRK","CAVA","ACVA","GRAB","BROS","TMDX","KLAR","CRM","GLW","NFLX","KTOS","VRT","VST","CRDO","CDLR","S","AMD","GOOG","NVDA","ALAB","OSCR","PYPL","BYRN","IOT","GLXY","CAN","BRZE","GSHD"]

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

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

def get_news():
    """Get key market news"""
    news = []
    try:
        # Yahoo Finance news
        r = requests.get("https://newsapi.org/v2/top-headlines?category=business&country=us&apiKey=demo", timeout=5)
        if r.status_code == 200:
            data = r.json()
            for article in data.get("articles", [])[:3]:
                title = article.get("title", "")
                if title and len(title) < 100:
                    news.append(f"📰 {title}")
    except:
        pass
    return news

def main():
    print(f"Fetching {len(STOCKS)} stocks...")
    results = [get_stock(s) for s in STOCKS]
    ok = [r for r in results if r.get("ok")]
    ok.sort(key=lambda x:x["cp"], reverse=True)
    
    now = datetime.now().strftime("%m/%d %H:%M")
    msg = f"📈 **US Stock Daily** - {now}\n"
    msg += "```\n"
    
    # Header
    msg += f"{'Ticker':<8} {'Price':>10} {'Change':>10} {'%':>8}\n"
    msg += "-"*40 + "\n"
    
    # All stocks (compact)
    for r in ok:
        sign = "+" if r["cp"] > 0 else ""
        msg += f"{r['s']:<8} ${r['p']:>9.2f} {sign}{r['c']:>8.2f} {sign}{r['cp']:>6.2f}%\n"
    
    msg += "```\n"
    
    # Summary
    gain = [r for r in ok if r["cp"]>0]
    loss = [r for r in ok if r["cp"]<0]
    msg += f"📊 **Summary:** {len(gain)} ▲ | {len(loss)} ▼\n"
    
    # Top gainers
    if gain[:3]:
        msg += "🟢 **Top Gainers:** " + ", ".join([f"{r['s']} +{r['cp']}%" for r in gain[:3]]) + "\n"
    
    # Top losers  
    if loss[-3:]:
        msg += "🔴 **Top Losers:** " + ", ".join([f"{r['s']} {r['cp']}%" for r in loss[-3:]]) + "\n"
    
    # News
    news = get_news()
    if news:
        msg += "\n📰 **Market News:**\n" + "\n".join(news)
    
    # Send
    if len(msg) <= 2000 and WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={"content":msg}, timeout=10)
            print("✅ Sent to Discord!")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(msg[:500])

if __name__=="__main__": main()
