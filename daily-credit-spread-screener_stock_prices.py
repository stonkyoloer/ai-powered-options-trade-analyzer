**Create:** `touch stock_prices.py`

**Query:** `open -e stock_prices.py`

```bash
# stock_prices.py - Credit Spread Universe Stock Prices
"""
Gets live stock prices for all tickers in both GPT and Grok universes.
This feeds the credit spread analysis pipeline.
"""
import asyncio
import json
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD
from sectors import get_sectors

async def collect_universe_stock_prices(mode, verbose=True):
    """Collect stock prices for all tickers in a universe"""
    if verbose:
        print(f"💰 Collecting Stock Prices - {mode.upper()} Universe")
        print("=" * 60)
    
    # Get all tickers for this mode
    sectors = get_sectors(mode)
    all_tickers = []
    for sector_data in sectors.values():
        all_tickers.extend(sector_data["tickers"])
    
    # Remove duplicates while preserving order
    unique_tickers = []
    seen = set()
    for ticker in all_tickers:
        if ticker not in seen:
            unique_tickers.append(ticker)
            seen.add(ticker)
    
    if verbose:
        print(f"🎯 Getting prices for {len(unique_tickers)} tickers...")
        print(f"    Tickers: {', '.join(unique_tickers[:10])}{'...' if len(unique_tickers) > 10 else ''}")
    
    sess = Session(USERNAME, PASSWORD)
    stock_prices = {}
    quotes_received = 0
    
    async with DXLinkStreamer(sess) as streamer:
        if verbose:
            print("📡 Connecting to market data...")
        
        await streamer.subscribe(Quote, unique_tickers)
        
        if verbose:
            print("✅ Connected! Collecting prices...")
        
        collected = set()
        start_time = asyncio.get_event_loop().time()
        last_report = start_time
        
        # Collect for up to 30 seconds or until all prices collected
        while len(collected) < len(unique_tickers):
            now_time = asyncio.get_event_loop().time()
            elapsed = now_time - start_time
            
            # Progress report
            if verbose and now_time - last_report >= 3.0:
                print(f"  📈 Progress: {len(collected)}/{len(unique_tickers)} ({len(collected)/len(unique_tickers)*100:.1f}%) | {elapsed:.1f}s")
                last_report = now_time
            
            # Timeout check
            if elapsed >= 30.0:
                if verbose:
                    print("⏰ Timeout reached (30s)")
                break
            
            try:
                quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=2.0)
                quotes_received += 1
                
                if quote and quote.event_symbol in unique_tickers:
                    ticker = quote.event_symbol
                    
                    # Only take first valid quote per ticker
                    if ticker not in collected:
                        bid, ask = float(quote.bid_price or 0), float(quote.ask_price or 0)
                        
                        if bid > 0 and ask > 0 and ask >= bid:
                            mid_price = (bid + ask) / 2
                            spread = ask - bid
                            
                            stock_prices[ticker] = {
                                'ticker': ticker,
                                'current_price': round(mid_price, 4),
                                'bid': round(bid, 4),
                                'ask': round(ask, 4),
                                'spread': round(spread, 4),
                                'spread_pct': round(100 * spread / mid_price, 3) if mid_price > 0 else 0,
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            }
                            
                            collected.add(ticker)
                            
                            if verbose and len(collected) <= 5:
                                print(f"    💰 {ticker}: ${mid_price:.2f}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if verbose:
                    print(f"⚠️ Quote error: {e}")
                continue
        
        await streamer.unsubscribe(Quote, unique_tickers)
    
    # Results
    result = {
        'mode': mode,
        'collection_stats': {
            'tickers_requested': len(unique_tickers),
            'prices_collected': len(stock_prices),
            'total_quotes_received': quotes_received,
            'success_rate': len(stock_prices) / len(unique_tickers) * 100,
            'collection_time_seconds': elapsed
        },
        'stock_prices': stock_prices,
        'missing_tickers': [t for t in unique_tickers if t not in stock_prices]
    }
    
    # Save results
    filename = f"stock_prices_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Stock Price Results:")
        print(f"  ✅ Success: {len(stock_prices)}/{len(unique_tickers)} ({len(stock_prices)/len(unique_tickers)*100:.1f}%)")
        print(f"  📡 Total quotes: {quotes_received}")
        print(f"  📁 Saved: {filename}")
        
        if result['missing_tickers']:
            print(f"  ⚠️ Missing: {result['missing_tickers']}")
        
        # Show price range
        if stock_prices:
            prices = [data['current_price'] for data in stock_prices.values()]
            print(f"  💰 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Stock Price Collector for Credit Spreads")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(collect_universe_stock_prices(mode))
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 stock_prices.py`
