**Create:** `touch stock_prices.py`

**Query:** `open -e stock_prices.py`

```bash
# stock_prices_focused.py - Focused Stock Price Collection
"""
CHANGE - only process the final 18 selected tickers instead of all 72.
75% less work = much faster execution.
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD
from sectors import PerfTimer

async def collect_final_stock_prices(timeout=5):
    """Collect prices for final 18 tickers only"""
    print("💰 Collecting Stock Prices - Final 18 Tickers")
    print("=" * 60)
    
    # Load final universe
    try:
        with open("final_universe.json", "r") as f:
            universe_data = json.load(f)
    except FileNotFoundError:
        print("❌ final_universe.json not found. Run sector_selection.py first.")
        return None
    
    target_tickers = universe_data["tickers_for_credit_analysis"]
    print(f"🎯 Getting prices for {len(target_tickers)} final tickers")
    print(f"📋 Tickers: {', '.join(target_tickers)}")
    
    sess = Session(USERNAME, PASSWORD)
    stock_prices = {}
    events_received = 0
    
    with PerfTimer("Final stock price collection"):
        async with DXLinkStreamer(sess) as streamer:
            print("📡 Subscribing to quotes...")
            await streamer.subscribe(Quote, target_tickers)
            
            start_time = time.time()
            collected = set()
            
            while time.time() - start_time < timeout:
                elapsed = time.time() - start_time
                
                # Early exit when we have all prices
                if len(collected) >= len(target_tickers):
                    print("🚀 All prices collected!")
                    break
                
                # Early exit at 95% after 2 seconds
                if len(collected) >= len(target_tickers) * 0.95 and elapsed > 2:
                    print("🚀 Early exit at 95% coverage")
                    break
                
                try:
                    quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=0.3)
                    events_received += 1
                    
                    if quote and quote.event_symbol in target_tickers and quote.event_symbol not in collected:
                        bid, ask = float(quote.bid_price or 0), float(quote.ask_price or 0)
                        
                        if bid > 0 and ask > 0 and ask >= bid:
                            mid_price = (bid + ask) / 2
                            spread = ask - bid
                            
                            stock_prices[quote.event_symbol] = {
                                'ticker': quote.event_symbol,
                                'current_price': round(mid_price, 4),
                                'bid': round(bid, 4),
                                'ask': round(ask, 4),
                                'spread': round(spread, 4),
                                'spread_pct': round(100 * spread / mid_price, 3) if mid_price > 0 else 0,
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            }
                            collected.add(quote.event_symbol)
                            print(f"  💰 {quote.event_symbol}: ${mid_price:.2f}")
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"  ⚠️ Quote error: {e}")
                    continue
            
            await streamer.unsubscribe(Quote, target_tickers)
    
    elapsed = time.time() - start_time
    success_rate = len(stock_prices) / len(target_tickers) * 100
    
    # Enhanced results with universe context
    result = {
        'collection_stats': {
            'target_tickers': len(target_tickers),
            'prices_collected': len(stock_prices),
            'success_rate': round(success_rate, 1),
            'total_events': events_received,
            'elapsed_seconds': round(elapsed, 2)
        },
        'stock_prices': stock_prices,
        'missing_tickers': [t for t in target_tickers if t not in stock_prices],
        'universe_context': {
            'from_gpt_sectors': len([t for t in universe_data["ticker_list"] if t["mode"] == "gpt"]),
            'from_grok_sectors': len([t for t in universe_data["ticker_list"] if t["mode"] == "grok"]),
            'total_sectors_covered': len(set(t["sector"] for t in universe_data["ticker_list"]))
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = "final_stock_prices.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📊 Final Stock Price Results:")
    print(f"  ✅ Success: {len(stock_prices)}/{len(target_tickers)} ({success_rate:.1f}%)")
    print(f"  📡 Events: {events_received}")
    print(f"  ⏱️ Time: {elapsed:.1f}s")
    print(f"  📁 Saved: {filename}")
    
    if result['missing_tickers']:
        print(f"  ❌ Missing: {result['missing_tickers']}")
    
    # Show price range
    if stock_prices:
        prices = [data['current_price'] for data in stock_prices.values()]
        print(f"  💰 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"  🎯 Average price: ${sum(prices)/len(prices):.2f}")
    
    return result

def main():
    """Main function"""
    print("🚀 Focused Stock Price Collector")
    print("=" * 50)
    
    asyncio.run(collect_final_stock_prices())

if __name__ == "__main__":
    main()
```

**Run:** `python3 stock_prices.py`
