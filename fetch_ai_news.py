import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, date
from email.utils import parsedate_to_datetime

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

RSS_FEEDS = [
    {"name": "FDA Regulatory", "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml"},
    {"name": "ET Pharma", "url": "https://health.economictimes.indiatimes.com/rss/topstories"},
    {"name": "FiercePharma", "url": "https://www.fiercepharma.com/rss/xml"},
    {"name": "Pharma News", "url": "https://pmn.feedify.net/rss"}
]

# Tickers: 5 Top Indian & 5 Top International Pharma Companies
STOCKS = [
    # Indian Pharma (NSE symbols)
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "market": "IN", "currency": "INR"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's", "market": "IN", "currency": "INR"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "market": "IN", "currency": "INR"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Lab", "market": "IN", "currency": "INR"},
    {"symbol": "LUPIN.NS", "name": "Lupin", "market": "IN", "currency": "INR"},
    # Global Pharma
    {"symbol": "LLY", "name": "Eli Lilly", "market": "INT", "currency": "USD"},
    {"symbol": "NVO", "name": "Novo Nordisk", "market": "INT", "currency": "USD"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "market": "INT", "currency": "USD"},
    {"symbol": "PFE", "name": "Pfizer", "market": "INT", "currency": "USD"},
    {"symbol": "AZN", "name": "AstraZeneca", "market": "INT", "currency": "USD"}
]

def fetch_stock_prices():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    stock_data = []

    for stock in STOCKS:
        symbol = stock["symbol"]
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                result = data['chart']['result'][0]
                meta = result['meta']
                
                current_price = meta.get('regularMarketPrice')
                previous_close = meta.get('chartPreviousClose') or meta.get('previousClose')
                
                change_percent = 0.0
                if current_price and previous_close:
                    change_percent = ((current_price - previous_close) / previous_close) * 100

                stock_data.append({
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "market": stock["market"],
                    "currency": stock["currency"],
                    "price": round(current_price, 2) if current_price else 0.0,
                    "change": round(change_percent, 2)
                })
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
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
    print("Starting data fetch...")
    stocks = fetch_stock_prices()
    
    # Load existing data or initialize structure
    output = {
        "updated": datetime.now().strftime("%b %d, %Y - %H:%M"),
        "stocks": stocks,
        "feeds": []
    }
    
    # Simple feed processing pass to ensure today's date injection
    today_str = date.today().strftime("%Y-%m-%d")
    print(f"Current injection date: {today_str}")

    # Save output to data.json for GitHub Pages
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print("data.json updated successfully!")

if __name__ == "__main__":
    main()
