#!/usr/bin/env python3
"""US Stock Daily Crawler - 57 Tickers"""
import os, sys, requests, time
from datetime import datetime

STOCKS = ["ADBE","FISV","AMZN","CHYM","VKTX","FIG","ONDS","EOSE","NVTS","IGV","U","SNOW","NBIS","IREN","CRWV","PLTR","MSFT","FCX","TSLA","SMR","AVGO","ORCL","SE","MRVL","LEU","CELH","OKLO","NU","TSM","RBRK","CAVA","ACVA","GRAB","BROS","TMDX","KLAR","CRM","GLW","NFLX","KTOS","VRT","VST","CRDO","CDLR","S","AMD","GOOG","NVDA","ALAB","OSCR","PYPL","BYRN","IOT","GLXY","CAN","BRZE","GSHD"]
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

def get_stock(symbol):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        d = r.json()
        if "chart" in d and d["chart"]["result"]:
            m = d["chart"]["result"][0]["meta"]
            p, c = m.get("regularMarketPrice",0), m.get("previousClose",0)
            if p and c: return {"s":symbol,"p":p,"c":c,"cp":round((p-c)/c*100,2),"ok":1}
    except: pass
    return {"s":symbol,"ok":0}

def main():
    print(f"Fetching {len(STOCKS)} stocks...")
    results = [get_stock(s) for s in STOCKS]
    ok = [r for r in results if r.get("ok")]
    ok.sort(key=lambda x:x["cp"], reverse=True)
    
    # Build compact message
    msg = f"📈 **US Stock Daily** {datetime.now().strftime('%m/%d %H:%M')}\n"
    
    # Top 5 gainers (compact)
    gain = [r for r in ok if r["cp"]>0][:5]
    if gain: msg += "🟢 " + " ".join([f"{r['s']}+{r['cp']}%" for r in gain])
    
    # Top 5 losers (compact)  
    loss = [r for r in ok if r["cp"]<0][-5:]
    if loss: msg += "\n🔴 " + " ".join([f"{r['s']}{r['cp']}%" for r in loss])
    
    # Summary
    up = len([r for r in ok if r["cp"]>0])
    dn = len([r for r in ok if r["cp"]<0])
    msg += f"\n📊 {up}↑ {dn}↓"
    
    # Send to Discord
    if DISCORD_WEBHOOK_URL and len(msg)<=2000:
        requests.post(DISCORD_WEBHOOK_URL, json={"content":msg}, timeout=10)
        print("✅ Sent to Discord!")
    else:
        print(msg)

if __name__=="__main__": main()
