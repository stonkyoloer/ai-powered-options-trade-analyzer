**Create:** `touch spot.py`

**Query:** `open -e spot.py`

```bash
# spot.py - Optimized Live Quote Collection
"""
CHANGE - optimize for 20min runtime with aggressive timeouts.
Gets quotes for all 72 tickers (36 GPT + 36 Grok).
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD
from sectors import PerfTimer

async def collect_quotes_fast(tickers, mode, timeout=8):
    """Collect quotes with aggressive timeout"""
    print(f"📊 Collecting quotes for {len(tickers)} {mode.upper()} tickers")
    print(f"⏱️ Timeout: {timeout}s")
    
    sess = Session(USERNAME, PASSWORD)
    quotes = {}
    events_received = 0
    
    with PerfTimer(f"{mode.upper()} quote collection"):
        async with DXLinkStreamer(sess) as streamer:
            print("📡 Subscribing to quotes...")
            await streamer.subscribe(Quote, tickers)
            
            start_time = time.time()
            last_report = start_time
            collected = set()
            
            while time.time() - start_time < timeout:
                elapsed = time.time() - start_time
                
                # Progress report every 2s
                if time.time() - last_report >= 2:
                    rate = len(collected) / len(tickers) * 100
                    print(f"  📈 {len(collected)}/{len(tickers)} ({rate:.1f}%) | {elapsed:.1f}s")
                    last_report = time.time()
                
                # Early exit at 95% after 3s
                if len(collected) >= len(tickers) * 0.95 and elapsed > 3:
                    print("  🚀 Early exit at 95%")
                    break
                
                try:
                    quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=0.3)
                    events_received += 1
                    
                    if quote and quote.event_symbol in tickers and quote.event_symbol not in collected:
                        bid, ask = float(quote.bid_price or 0), float(quote.ask_price or 0)
                        
                        if bid > 0 and ask > 0 and ask >= bid:
                            mid = (bid + ask) / 2
                            spread = ask - bid
                            
                            quotes[quote.event_symbol] = {
                                "ticker": quote.event_symbol,
                                "bid": round(bid, 4),
                                "ask": round(ask, 4), 
                                "mid": round(mid, 4),
                                "spread": round(spread, 4),
                                "spread_pct": round(100 * spread / mid, 3) if mid > 0 else 0,
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                            collected.add(quote.event_symbol)
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"  ⚠️ Quote error: {e}")
                    continue
            
            await streamer.unsubscribe(Quote, tickers)
    
    # Results summary
    success_rate = len(quotes) / len(tickers) * 100
    elapsed = time.time() - start_time
    
    result = {
        "mode": mode,
        "stats": {
            "requested": len(tickers),
            "collected": len(quotes),
            "success_rate": round(success_rate, 1),
            "events_received": events_received,
            "elapsed_seconds": round(elapsed, 2)
        },
        "quotes": quotes,
        "missing": [t for t in tickers if t not in quotes]
    }
    
    # Save results
    filename = f"spot_quotes_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"📊 {mode.upper()} Results: {len(quotes)}/{len(tickers)} ({success_rate:.1f}%)")
    print(f"📁 Saved: {filename}")
    
    if result["missing"]:
        print(f"❌ Missing: {result['missing']}")
    
    return result

def main():
    """Main quote collection"""
    print("🚀 Optimized Quote Collector")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        try:
            # Load universe
            with open(f"universe_{mode}.json", "r") as f:
                universe = json.load(f)
            
            # Extract valid tickers
            valid_tickers = [
                item["ticker"] for item in universe 
                if isinstance(item, dict) and item.get("status") == "ok"
            ]
            
            if valid_tickers:
                asyncio.run(collect_quotes_fast(valid_tickers, mode))
            else:
                print(f"❌ No valid tickers for {mode}")
                
        except FileNotFoundError:
            print(f"❌ universe_{mode}.json not found")
        except Exception as e:
            print(f"❌ Error processing {mode}: {e}")

if __name__ == "__main__":
    main()
```

**Run:** `python3 spot.py`
