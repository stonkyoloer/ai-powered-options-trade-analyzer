**Create:** `touch stock_prices.py`

**Query:** `open -e stock_prices.py`

```bash
# Step 1: Get Stock Prices - Like checking price tags!
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

# Our 9 favorite companies to trade
COMPANIES = [
    'NVDA',  # NVIDIA (makes computer chips)
    'TSLA',  # Tesla (electric cars)
    'AMZN',  # Amazon (online shopping)
    'ISRG',  # Intuitive Surgical (robot surgery)
    'PLTR',  # Palantir (data analysis)
    'ENPH',  # Enphase Energy (solar power)
    'XOM',   # Exxon Mobil (oil company)
    'DE',    # John Deere (farm equipment)
    'CAT'    # Caterpillar (construction equipment)
]

async def get_stock_prices():
    print("🏪 STEP 1: Getting Stock Prices")
    print("=" * 50)
    print("📋 Checking prices for our 9 favorite companies...")
    
    session = Session(USERNAME, PASSWORD)
    stock_prices = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to the stock market...")
        await streamer.subscribe(Quote, COMPANIES)
        print("✅ Connected! Now listening for prices...")
        
        collected = set()
        start_time = asyncio.get_event_loop().time()
        
        while len(collected) < len(COMPANIES) and (asyncio.get_event_loop().time() - start_time) < 30:
            try:
                quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=5.0)
                
                if quote and quote.event_symbol in COMPANIES and quote.event_symbol not in collected:
                    company = quote.event_symbol
                    price = float((quote.bid_price + quote.ask_price) / 2)
                    
                    stock_prices[company] = {
                        'company_name': company,
                        'current_price': price,
                        'buy_price': float(quote.bid_price),
                        'sell_price': float(quote.ask_price),
                        'when_checked': datetime.now().isoformat()
                    }
                    
                    collected.add(company)
                    print(f"   💰 {company}: ${price:.2f}")
                    
            except asyncio.TimeoutError:
                continue
    
    # Save our results
    result = {
        'step': 1,
        'what_we_did': 'Got current stock prices',
        'timestamp': datetime.now().isoformat(),
        'companies_checked': len(stock_prices),
        'stock_prices': stock_prices
    }
    
    filename = 'step1_stock_prices.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved stock prices to: {filename}")
    print(f"📊 Found prices for {len(stock_prices)} companies!")
    return result

if __name__ == "__main__":
    asyncio.run(get_stock_prices())
```

**Run:** `python3 stock_prices.py`
