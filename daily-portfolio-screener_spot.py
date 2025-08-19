**Create:** `touch spot.py`

**Query:** `open -e spot.py`

```bash
# spot.py - Live Stock Quote Collection
"""
Streams live stock quotes for all valid tickers.
Gets real-time bid/ask/mid prices.
"""
import asyncio
import json
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

async def collect_live_quotes(tickers, mode, verbose=True):
    """Collect live quotes for a list of tickers"""
    if verbose:
        print(f"📊 Collecting Live Quotes - {mode.upper()}")
        print("=" * 60)
        print(f"🎯 Streaming quotes for {len(tickers)} tickers...")
    
    sess = Session(USERNAME, PASSWORD)
    quotes = {}
    quotes_received = 0
    
    async with DXLinkStreamer(sess) as streamer:
        if verbose:
            print("🔌 Connected to live market data")
        
        await streamer.subscribe(Quote, tickers)
        if verbose:
            print(f"📡 Subscribed to {len(tickers)} symbols")
        
        start_time = asyncio.get_event_loop().time()
        last_report = start_time
        
        # Collect for up to 15 seconds or until we have all quotes
        while True:
            now_time = asyncio.get_event_loop().time()
            elapsed = now_time - start_time
            
            # Progress report every 3 seconds
            if verbose and now_time - last_report >= 3.0:
                coverage = len(quotes)
                print(f"📈 Progress: {coverage}/{len(tickers)} quotes ({coverage/len(tickers)*100:.1f}%) | {elapsed:.1f}s elapsed")
                last_report = now_time
            
            # Exit conditions
            if elapsed >= 15.0:
                if verbose:
                    print("⏰ Time limit reached (15s)")
                break
            if len(quotes) >= len(tickers):
                if verbose:
                    print("✅ All quotes collected!")
                break
            
            try:
                q = await asyncio.wait_for(streamer.get_event(Quote), timeout=1.0)
                quotes_received += 1
                
                if q and q.event_symbol in tickers:
                    bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
                    
                    if bid > 0 and ask > 0 and ask >= bid:
                        if q.event_symbol not in quotes:  # First valid quote wins
                            mid = (bid + ask) / 2
                            spread = ask - bid
                            quotes[q.event_symbol] = {
                                "ticker": q.event_symbol,
                                "bid": round(bid, 4),
                                "ask": round(ask, 4),
                                "mid": round(mid, 4),
                                "spread": round(spread, 4),
                                "spread_pct": round(100 * spread / mid, 3) if mid > 0 else 0,
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                            
                            if verbose and len(quotes) <= 5:
                                print(f"  💰 {q.event_symbol}: ${mid:.2f} (spread: {spread:.3f})")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if verbose:
                    print(f"⚠️ Quote error: {e}")
                continue
        
        await streamer.unsubscribe(Quote, tickers)
    
    # Results
    result = {
        "mode": mode,
        "collection_stats": {
            "tickers_requested": len(tickers),
            "quotes_collected": len(quotes),
            "total_events_received": quotes_received,
            "success_rate": len(quotes) / len(tickers) * 100,
            "collection_time_seconds": elapsed
        },
        "quotes": quotes,
        "missing_tickers": [t for t in tickers if t not in quotes]
    }
    
    # Save results
    filename = f"spot_quotes_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Quote Collection Results:")
        print(f"  ✅ Success: {len(quotes)}/{len(tickers)} ({len(quotes)/len(tickers)*100:.1f}%)")
        print(f"  📡 Events received: {quotes_received}")
        print(f"  📁 Saved: {filename}")
        
        if result["missing_tickers"]:
            print(f"  ⚠️ Missing: {result['missing_tickers']}")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Live Quote Collector")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        # Load valid tickers from previous step
        try:
            with open(f"universe_{mode}.json", "r") as f:
                universe_data = json.load(f)
            
            tickers = [t["ticker"] for t in universe_data["valid_tickers"]]
            if tickers:
                asyncio.run(collect_live_quotes(tickers, mode))
            else:
                print(f"❌ No valid tickers found for {mode}")
                
        except FileNotFoundError:
            print(f"❌ universe_{mode}.json not found. Run build_universe.py first.")
        except Exception as e:
            print(f"❌ Error loading {mode} universe: {e}")

if __name__ == "__main__":
    main()
```

**Run:** `python3 spot.py`
