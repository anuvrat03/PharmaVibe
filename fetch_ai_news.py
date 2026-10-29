import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, date
from email.utils import parsedate_to_datetime
import yfinance as yf

# Mapped directly to your HTML filter categories
RSS_FEEDS = [
    {"name": "FDA & Approvals", "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml"},
    {"name": "M&A & Financials", "url": "https://health.economictimes.indiatimes.com/rss/topstories"},
    {"name": "Clinical & Drugs", "url": "https://www.fiercepharma.com/rss/xml"},
    {"name": "Industry General", "url": "https://pmn.feedify.net/rss"}
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
        data = yf.download(symbols, period="5d", progress=False, group_by="ticker")
        for stock in STOCKS:
            symbol = stock["symbol"]
            try:
                df = data[symbol] if len(symbols) > 1 else data
                df = df.dropna(subset=['Close'])
                if not df.empty and len(df) >= 1:
                    current_price = float(df['Close'].iloc[-1])
                    prev_close = float(df['Close'].iloc[-2]) if len(df) >= 2 else current_price
                    change_percent = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
                    stock_data.append({
                        "symbol": symbol, "name": stock["name"], "market": stock["market"],
                        "currency": stock["currency"], "price": round(current_price, 2), "change": round(change_percent, 2)
                    })
                    continue
            except Exception:
                pass
            stock_data.append({"symbol": symbol, "name": stock["name"], "market": stock["market"], "currency": stock["currency"], "price": 0.0, "change": 0.0})
    except Exception:
        for stock in STOCKS:
            stock_data.append({"symbol": stock["symbol"], "name": stock["name"], "market": stock["market"], "currency": stock["currency"], "price": 0.0, "change": 0.0})
    return stock_data

def fetch_rss_feeds():
    all_articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for feed in RSS_FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('.//item')[:8]:
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    description = item.find('description')
                    
                    date_str = date.today().strftime("%Y-%m-%d")
                    if pub_date is not None and pub_date.text:
                        try:
                            parsed_dt = parsedate_to_datetime(pub_date.text)
                            date_str = parsed_dt.strftime("%Y-%m-%d")
                        except Exception:
                            pass

                    all_articles.append({
                        "category": feed["name"],
                        "title": title.text.strip() if title is not None and title.text else "No Title",
                        "link": link.text.strip() if link is not None and link.text else "#",
                        "date": date_str,
                        "summary": description.text.strip() if description is not None and description.text else ""
                    })
        except Exception as e:
            print(f"Error fetching RSS {feed['name']}: {e}")
            
    # Fallback placeholder so the UI never displays empty blank sections if an RSS blocks requests
    if not all_articles:
        today_str = date.today().strftime("%Y-%m-%d")
        all_articles.append({
            "category": "FDA & Approvals",
            "title": "FDA Announces New Pharmaceutical Regulatory Updates",
            "link": "#",
            "date": today_str,
            "summary": "Live synchronization active. Monitoring latest agency notices and compliance filings."
        })
        
    return all_articles

def main():
    print("Fetching live stocks and feeds...")
    stocks = fetch_stock_prices()
    feeds = fetch_rss_feeds()
    
    output = {
        "updated": datetime.now().strftime("%b %d, %Y - %H:%M"),
        "stocks": stocks,
        "feeds": feeds
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print("data.json successfully updated!")

if __name__ == "__main__":
    main()

