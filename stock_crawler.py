#!/usr/bin/env python3
"""
US Stock Daily Crawler
Crawls stock performance and sends to Discord webhook
"""

import os
import sys
import json
import requests
from datetime import datetime
import time

# Stock list
STOCKS = [
    "ADBE", "FISV", "AMZN", "CHYM", "VKTX", "FIG", "ONDS", "EOSE", "NVTS", "IGV",
    "U", "SNOW", "NBIS", "IREN", "CRWV", "PLTR", "MSFT", "FCX", "TSLA", "SMR",
    "AVGO", "ORCL", "SE", "MRVL", "LEU", "CELH", "OKLO", "NU", "TSM", "RBRK",
    "CAVA", "ACVA", "GRAB", "BROS", "TMDX", "KLAR", "CRM", "GLW", "NFLX", "KTOS",
    "VRT", "VST", "CRDO", "CDLR", "S", "AMD", "GOOG", "NVDA", "ALAB", "OSCR",
    "PYPL", "BYRN", "IOT", "GLXY", "CAN", "BRZE", "GSHD"
]

# Discord webhook (set via environment variable)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

def get_stock_data(symbol):
    """Get stock data from Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
            result = data["chart"]["result"][0]
            meta = result.get("meta", {})
            
            current_price = meta.get("regularMarketPrice", 0)
            previous_close = meta.get("previousClose", 0)
            
            if current_price and previous_close:
                change = current_price - previous_close
                change_pct = (change / previous_close) * 100
                
                return {
                    "symbol": symbol,
                    "price": current_price,
                    "change": change,
                    "change_pct": change_pct,
                    "success": True
                }
        
        return {"symbol": symbol, "success": False, "error": "No data"}
    
    except Exception as e:
        return {"symbol": symbol, "success": False, "error": str(e)}

def format_message(stock_results):
    """Format results for Discord"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Sort by percentage change
    sorted_stocks = sorted(
        [s for s in stock_results if s.get("success")],
        key=lambda x: x.get("change_pct", 0),
        reverse=True
    )
    
    message = f"📈 **US Stock Daily Update** ({now})\n\n"
    
    # Top gainers
    message += "🟢 **Top Gainers:**\n"
    for stock in sorted_stocks[:5]:
        if stock.get("change_pct", 0) > 0:
            message += f"  {stock['symbol']}: ${stock['price']:.2f} (+{stock['change_pct']:.2f}%)\n"
    
    # Top losers
    message += "\n🔴 **Top Losers:**\n"
    for stock in sorted_stocks[-5:]:
        if stock.get("change_pct", 0) < 0:
            message += f"  {stock['symbol']}: ${stock['price']:.2f} ({stock['change_pct']:.2f}%)\n"
    
    # Summary
    gainers = len([s for s in sorted_stocks if s.get("change_pct", 0) > 0])
    losers = len([s for s in sorted_stocks if s.get("change_pct", 0) < 0])
    
    message += f"\n📊 **Summary:** {gainers} ▲ | {losers} ▼"
    
    return message

def send_discord(message):
    """Send message to Discord webhook"""
    if not DISCORD_WEBHOOK_URL:
        print("ERROR: DISCORD_WEBHOOK_URL not set")
        return False
    
    try:
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"Discord send error: {e}")
        return False

def main():
    print(f"Fetching data for {len(STOCKS)} stocks...")
    
    results = []
    for i, stock in enumerate(STOCKS):
        print(f"  [{i+1}/{len(STOCKS)}] {stock}...", end=" ")
        data = get_stock_data(stock)
        if data.get("success"):
            print(f"${data['price']:.2f} ({data['change_pct']:+.2f}%)")
        else:
            print(f"Failed: {data.get('error')}")
        results.append(data)
        time.sleep(0.5)  # Rate limiting
    
    # Send to Discord
    message = format_message(results)
    print("\nSending to Discord...")
    
    if send_discord(message):
        print("✅ Successfully sent to Discord!")
    else:
        print("❌ Failed to send to Discord")
        # Print message for debugging
        print("\nMessage preview:")
        print(message[:500] + "..." if len(message) > 500 else message)

if __name__ == "__main__":
    main()
