**Create:** `touch market_prices.py`

**Query:** `open -e market_prices.py`

```bash
import asyncio
import json
from datetime import datetime
from decimal import Decimal
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def safe_float_convert(value):
    """Safely convert any numeric value to float"""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

async def get_market_prices():
    print("💰 STEP 4: Getting Market Prices")
    print("=" * 50)
    print("🏪 Finding out what people will actually pay vs. sell for...")
    
    # Load our contracts from Step 2
    with open('step2_options_contracts.json', 'r') as f:
        step2_data = json.load(f)
    
    # Collect all contract symbols
    all_contracts = []
    for company_data in step2_data['options_by_company'].values():
        for exp_data in company_data['expiration_dates'].values():
            for contract in exp_data['contracts']:
                all_contracts.append(contract['streamer_symbol'])
    
    print(f"🎯 Getting prices for {len(all_contracts)} contracts...")
    
    session = Session(USERNAME, PASSWORD)
    market_prices = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to get market prices...")
        await streamer.subscribe(Quote, all_contracts)
        print("✅ Connected! Getting buy/sell prices...")
        
        collected_quotes = []
        start_time = asyncio.get_event_loop().time()
        
        # Collect for 2 minutes
        while (asyncio.get_event_loop().time() - start_time) < 120:
            try:
                quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=3.0)
                
                if quote:
                    collected_quotes.append(quote)
                    
                    # Show progress every 100 quotes
                    if len(collected_quotes) % 100 == 0:
                        print(f"   💰 Prices collected: {len(collected_quotes)}")
                        
            except asyncio.TimeoutError:
                continue
        
        print(f"✅ Collected {len(collected_quotes)} market prices!")
        
        # Process quotes with proper decimal handling
        for quote in collected_quotes:
            # Safely convert all numeric values to float
            buy_price = safe_float_convert(quote.bid_price)
            sell_price = safe_float_convert(quote.ask_price)
            bid_size = safe_float_convert(getattr(quote, 'bid_size', 0))
            ask_size = safe_float_convert(getattr(quote, 'ask_size', 0))
            
            if buy_price > 0 and sell_price > 0:
                market_prices[quote.event_symbol] = {
                    'contract_name': quote.event_symbol,
                    'what_buyers_pay': buy_price,      # Bid price
                    'what_sellers_want': sell_price,   # Ask price
                    'fair_price': (buy_price + sell_price) / 2,  # Middle price
                    'price_difference': sell_price - buy_price,  # Spread
                    'buyers_willing': bid_size,
                    'sellers_available': ask_size
                }
    
    # Organize by company
    companies = ['NVDA', 'TSLA', 'AMZN', 'ISRG', 'PLTR', 'ENPH', 'XOM', 'DE', 'CAT']
    prices_by_company = {}
    
    for company in companies:
        prices_by_company[company] = []
        
    for symbol, price_data in market_prices.items():
        for company in companies:
            if company in symbol:
                prices_by_company[company].append(price_data)
                break
    
    # Save our results with decimal handling
    result = {
        'step': 4,
        'what_we_did': 'Got buy/sell prices for all options',
        'timestamp': datetime.now().isoformat(),
        'total_prices_collected': len(market_prices),
        'companies_with_prices': len([c for c in prices_by_company.values() if c]),
        'prices_by_company': prices_by_company,
        'price_explanations': {
            'what_buyers_pay': 'The highest price someone will pay (BID)',
            'what_sellers_want': 'The lowest price someone will sell for (ASK)',
            'fair_price': 'The middle price between buy and sell',
            'price_difference': 'The gap between buy and sell prices (SPREAD)'
        }
    }
    
    filename = 'step4_market_prices.json'
    
    # Use custom JSON encoder to handle any remaining Decimal objects
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super(DecimalEncoder, self).default(obj)
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2, cls=DecimalEncoder)
    
    print(f"\n✅ Saved market prices to: {filename}")
    print(f"💰 Got prices for {len(market_prices)} contracts!")
    
    # Show some examples
    print(f"\n💰 PRICE EXAMPLES:")
    sample_prices = list(market_prices.items())[:5]
    for symbol, price_data in sample_prices:
        buy = price_data['what_buyers_pay']
        sell = price_data['what_sellers_want']
        diff = price_data['price_difference']
        print(f"   {symbol[-10:]:10}: Buy=${buy:.2f}, Sell=${sell:.2f}, Gap=${diff:.3f}")
    
    return result

if __name__ == "__main__":
    asyncio.run(get_market_prices())
```

**Run:** `python3 market_prices.py`
