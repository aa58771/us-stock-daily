#!/usr/bin/env python3
"""US Stock Daily Crawler - 57 Tickers"""
import os, requests
from datetime import datetime

STOCKS = ["ADBE","FISV","AMZN","CHYM","VKTX","FIG","ONDS","EOSE","NVTS","IGV","U","SNOW","NBIS","IREN","CRWV","PLTR","MSFT","FCX","TSLA","SMR","AVGO","ORCL","SE","MRVL","LEU","CELH","OKLO","NU","TSM","RBRK","CAVA","ACVA","GRAB","BROS","TMDX","KLAR","CRM","GLW","NFLX","KTOS","VRT","VST","CRDO","CDLR","S","AMD","GOOG","NVDA","ALAB","OSCR","PYPL","BYRN","IOT","GLXY","CAN","BRZE","GSHD"]

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

print(f"DEBUG: webhook = '{WEBHOOK_URL[:20]}...' " if WEBHOOK_URL else "DEBUG: webhook = ''")

def get_stock(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        d = r.json()
        if "chart" in d and d["chart"]["result"]:
            m = d["chart"]["result"][0]["meta"]
            p, c = m.get("regularMarketPrice",0), m.get("previousClose",0)
            if p and c: return {"s":sym,"p":round(p,2),"cp":round((p-c)/c*100,2),"ok":1}
    except: pass
    return {"s":sym,"ok":0}

def main():
    results = [get_stock(s) for s in STOCKS]
    ok = [r for r in results if r.get("ok")]
    ok.sort(key=lambda x:x["cp"], reverse=True)
    
    now = datetime.now().strftime("%m/%d %H:%M")
    msg = f"📈 **US Stock Daily** - {now}\n```\n"
    msg += f"{'Ticker':<8} {'Price':>10} {'%':>8}\n" + "-"*30 + "\n"
    for r in ok[:10]:
        sign = "+" if r["cp"] > 0 else ""
        msg += f"{r['s']:<8} ${r['p']:>8.2f} {sign}{r['cp']:>6.2f}%\n"
    msg += "```\n"
    
    up = len([r for r in ok if r["cp"]>0])
    dn = len([r for r in ok if r["cp"]<0])
    msg += f"📊 **Summary:** {up} ▲ | {dn} ▼"
    
    if not WEBHOOK_URL:
        print("ERROR: DISCORD_WEBHOOK_URL not set!")
        print(msg)
        return
    
    try:
        resp = requests.post(WEBHOOK_URL, json={"content":msg}, timeout=10)
        print(f"✅ Sent! Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__=="__main__": main()
