import os
import json
from datetime import datetime, date
import yfinance as yf

RSS_FEEDS = [
    {"name": "FDA Regulatory", "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml"},
    {"name": "ET Pharma", "url": "https://health.economictimes.indiatimes.com/rss/topstories"},
    {"name": "FiercePharma", "url": "https://www.fiercepharma.com/rss/xml"},
    {"name": "Pharma News", "url": "https://pmn.feedify.net/rss"}
]

STOCKS = [
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "market": "IN", "currency": "INR"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's", "market": "IN", "currency": "INR"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "market": "IN", "currency": "INR"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Lab", "market": "IN", "currency": "INR"},
    {"symbol": "LUPIN.NS", "name": "Lupin", "market": "IN", "currency": "INR"},
    {"symbol": "LLY", "name": "Eli Lilly", "market": "INT", "currency": "USD"},
    {"symbol": "NVO", "name": "Novo Nordisk", "market": "INT", "currency": "USD"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "market": "INT", "currency": "USD"},
    {"symbol": "PFE", "name": "Pfizer", "market": "INT", "currency": "USD"},
    {"symbol": "AZN", "name": "AstraZeneca", "market": "INT", "currency": "USD"}
]

def fetch_stock_prices():
    stock_data = []
    symbols = [stock["symbol"] for stock in STOCKS]
    
    try:
        # Download multi-ticker historical data for the last 5 days to reliably capture the latest close and previous close
        data = yf.download(symbols, period="5d", progress=False, group_by="ticker")
        
        for stock in STOCKS:
            symbol = stock["symbol"]
            try:
                # Extract individual ticker data frame
                df = data[symbol] if len(symbols) > 1 else data
                df = df.dropna(subset=['Close'])
                
                if not df.empty and len(df) >= 1:
                    current_price = float(df['Close'].iloc[-1])
                    prev_close = float(df['Close'].iloc[-2]) if len(df) >= 2 else current_price
                    
                    change_percent = 0.0
                    if prev_close > 0:
                        change_percent = ((current_price - prev_close) / prev_close) * 100
                        
                    stock_data.append({
                        "symbol": symbol,
                        "name": stock["name"],
                        "market": stock["market"],
                        "currency": stock["currency"],
                        "price": round(current_price, 2),
                        "change": round(change_percent, 2)
                    })
                    continue
            except Exception as inner_e:
                print(f"Error parsing {symbol}: {inner_e}")
                
            # Fallback if specific ticker fails
            stock_data.append({
                "symbol": symbol,
                "name": stock["name"],
                "market": stock["market"],
                "currency": stock["currency"],
                "price": 0.0,
                "change": 0.0
            })
    except Exception as e:
        print(f"Error downloading stock batch: {e}")
        for stock in STOCKS:
            stock_data.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "market": stock["market"],
                "currency": stock["currency"],
                "price": 0.0,
                "change": 0.0
            })
            
    return stock_data

def main():
    print("Starting data fetch with yfinance...")
    stocks = fetch_stock_prices()
    
    output = {
        "updated": datetime.now().strftime("%b %d, %Y - %H:%M"),
        "stocks": stocks,
        "feeds": []
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print("data.json updated successfully with live stocks!")

if __name__ == "__main__":
    main()
