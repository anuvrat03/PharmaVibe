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
                
                # Calculate percentage change
                change_percent = 0.0
                if current_price and previous_close:
                    change_percent = ((current_price - previous_close) / previous_close) * 100

                stock_data.append({
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "market": stock["market"],
                    "currency": stock.get("currency", "INR" if stock["market"] == "IN" else "USD"),
                    "price": round(current_price, 2) if current_price else 0.0,
                    "change": round(change_percent, 2)
                })
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            # Fallback structure so the UI doesn't break if a request fails
            stock_data.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "market": stock["market"],
                "currency": stock.get("currency", "INR" if stock["market"] == "IN" else "USD"),
                "price": 0.0,
                "change": 0.0
            })
            
    return stock_data
