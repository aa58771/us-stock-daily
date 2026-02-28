#!/usr/bin/env python3
"""US Stock Daily Crawler - 57 Tickers"""
import os, sys, requests, time
from datetime import datetime

STOCKS = ["ADBE","FISV","AMZN","CHYM","VKTX","FIG","ONDS","EOSE","NVTS","IGV","U","SNOW","NBIS","IREN","CRWV","PLTR","MSFT","FCX","TSLA","SMR","AVGO","ORCL","SE","MRVL","LEU","CELH","OKLO","NU","TSM","RBRK","CAVA","ACVA","GRAB","BROS","TMDX","KLAR","CRM","GLW","NFLX","KTOS","VRT","VST","CRDO","CDLR","S","AMD","GOOG","NVDA","ALAB","OSCR","PYPL","BYRN","IOT","GLXY","CAN","BRZE","GSHD"]

# 直接從環境變數讀取，確保有值
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
print(f"DEBUG: WEBHOOK_URL = '{WEBHOOK_URL}'")

if not WEBHOOK_URL or WEBHOOK_URL == "":
    print("ERROR: DISCORD_WEBHOOK_URL is not set!")
    sys.exit(1)

def get_stock(symbol):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        d = r.json()
        if "chart" in d and d["chart"]["result"]:
            m = d["chart"]["result"][0]["meta"]
            p, c = m.get("regularMarketPrice",0), m.get("previousClose",0)
            if p and c: return {"s":symbol,"p":p,"c":c,"cp":round((p-c)/c*100,2),"ok":1}
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return {"s":symbol,"ok":0}

def main():
    print(f"Fetching {len(STOCKS)} stocks...")
    results = [get_stock(s) for s in STOCKS]
    ok = [r for r in results if r.get("ok")]
    ok.sort(key=lambda x:x["cp"], reverse=True)
    
    # Build compact message
    msg = f"📈 **US Stock Daily** {datetime.now().strftime('%m/%d %H:%M')}\n"
    
    gain = [r for r in ok if r["cp"]>0][:5]
    if gain: msg += "🟢 " + " ".join([f"{r['s']}+{r['cp']}%" for r in gain])
    
    loss = [r for r in ok if r["cp"]<0][-5:]
    if loss: msg += "\n🔴 " + " ".join([f"{r['s']}{r['cp']}%" for r in loss])
    
    up = len([r for r in ok if r["cp"]>0])
    dn = len([r for r in ok if r["cp"]<0])
    msg += f"\n📊 {up}↑ {dn}↓"
    
    print(f"Message length: {len(msg)} chars")
    
    # Send to Discord
    if len(msg) <= 2000:
        try:
            resp = requests.post(WEBHOOK_URL, json={"content":msg}, timeout=10)
            print(f"Discord response: {resp.status_code}")
            if resp.status_code in [200, 204]:
                print("✅ Sent to Discord!")
            else:
                print(f"❌ Discord error: {resp.text}")
        except Exception as e:
            print(f"❌ Error sending to Discord: {e}")
    else:
        print("❌ Message too long!")

if __name__=="__main__":
    main()
