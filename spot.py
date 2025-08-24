# spot.py - Live Quote Collection for All Validated Tickers
"""
FIXED - Collects quotes for all validated tickers from build_universe.py
Gets real-time stock prices needed for liquidity analysis and credit spreads.
"""
import asyncio
import json
import time
from datetime import datetime, timezone
import sys
from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD
from sectors import PerfTimer
import getpass # Ensure getpass is imported
import asyncio # Ensure asyncio is imported
from get_session import get_or_create_session
# Note: Avoid importing TastytradeError to support different tastytrade versions

async def collect_quotes_for_validated_tickers(mode, sess, timeout=10):
    """Collect quotes for all validated tickers from universe file"""
    print(f"📊 Collecting quotes for {mode.upper()} validated tickers")
    print("=" * 60)
    
    # Load validated universe from build_universe.py
    try:
        with open(f"universe_{mode}.json", "r") as f:
            universe_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ universe_{mode}.json not found. Run build_universe.py first.")
        return None
    
    # Extract validated tickers only (status = "ok")
    validated_tickers = [
        item["ticker"] for item in universe_data 
        if isinstance(item, dict) and item.get("status") == "ok"
    ]
    
    if not validated_tickers:
        print(f"❌ No validated tickers found in universe_{mode}.json")
        return None
    
    print(f"🎯 Getting quotes for {len(validated_tickers)} validated tickers")
    print(f"📋 Tickers: {', '.join(validated_tickers)}")
    print(f"⏱️ Timeout: {timeout}s")
    
    
    quotes = {}
    events_received = 0
    
    with PerfTimer(f"{mode.upper()} quote collection"):
        async with DXLinkStreamer(sess) as streamer:
            print("📡 Subscribing to quotes...")
            await streamer.subscribe(Quote, validated_tickers)
            
            start_time = time.time()
            last_report = start_time
            collected = set()
            
            while time.time() - start_time < timeout:
                elapsed = time.time() - start_time
                
                # Progress report every 3s
                if time.time() - last_report >= 3:
                    rate = len(collected) / len(validated_tickers) * 100
                    print(f"  📈 Progress: {len(collected)}/{len(validated_tickers)} ({rate:.1f}%) | {elapsed:.1f}s")
                    last_report = time.time()
                
                # Early exit at 95% after 4s
                if len(collected) >= len(validated_tickers) * 0.95 and elapsed > 4:
                    print("  🚀 Early exit at 95% coverage")
                    break
                
                try:
                    quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=0.4)
                    events_received += 1
                    
                    if quote and quote.event_symbol in validated_tickers and quote.event_symbol not in collected:
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
                            print(f"  💰 {quote.event_symbol}: ${mid:.2f} (spread: {100 * spread / mid:.2f}%)")
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"  ⚠️ Quote error: {e}")
                    continue
            
            await streamer.unsubscribe(Quote, validated_tickers)
    
    # Calculate results
    success_rate = len(quotes) / len(validated_tickers) * 100
    elapsed = time.time() - start_time
    
    # Map tickers back to sectors for analysis
    ticker_to_sector = {}
    for item in universe_data:
        if item.get("status") == "ok":
            ticker_to_sector[item["ticker"]] = item["sector"]
    
    # Add sector info to quotes
    for ticker, quote_data in quotes.items():
        quote_data["sector"] = ticker_to_sector.get(ticker, "Unknown")
    
    result = {
        "mode": mode,
        "collection_stats": {
            "validated_tickers": len(validated_tickers),
            "quotes_collected": len(quotes),
            "success_rate": round(success_rate, 1),
            "events_received": events_received,
            "elapsed_seconds": round(elapsed, 2)
        },
        "quotes": quotes,
        "missing_tickers": [t for t in validated_tickers if t not in quotes],
        "sectors_represented": list(set(quote_data["sector"] for quote_data in quotes.values())),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"spot_quotes_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📊 {mode.upper()} Quote Collection Results:")
    print(f"  ✅ Success: {len(quotes)}/{len(validated_tickers)} ({success_rate:.1f}%)")
    print(f"  📡 Events: {events_received}")
    print(f"  ⏱️ Time: {elapsed:.1f}s")
    print(f"  🏢 Sectors: {len(result['sectors_represented'])}")
    print(f"  📁 Saved: {filename}")
    
    if result["missing_tickers"]:
        print(f"  ❌ Missing: {result['missing_tickers']}")
    
    # Show price range and sector breakdown
    if quotes:
        prices = [data["mid"] for data in quotes.values()]
        print(f"  💰 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        
        # Show quotes per sector
        sector_counts = {}
        for quote_data in quotes.values():
            sector = quote_data["sector"]
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        print(f"  📊 Quotes per sector:")
        for sector, count in sorted(sector_counts.items()):
            print(f"    {sector}: {count}")
    
    return result

def main():  # Modified: supports optional CLI 2FA argument
    """Main quote collection for both modes"""
    print("🚀 Stock Quote Collector - All Validated Tickers")
    print("=" * 50)
    
    # Optional 2FA code passed via CLI (from master.py)
    two_fa_arg = sys.argv[1] if len(sys.argv) > 1 else None

    # Get or reuse session (cached across steps)
    try:
        sess = get_or_create_session(two_fa_arg)
    except Exception as e:
        print(f"Authentication error creating session: {e}")
        return
    
    for mode in ["gpt", "grok", "claude"]:
        result = asyncio.run(collect_quotes_for_validated_tickers(mode, sess))
        if result:
            print(f"\n🎯 {mode.upper()}: Ready for liquidity analysis")
        else:
            print(f"\n❌ {mode.upper()}: Failed - check universe file")
        print()

if __name__ == "__main__":
    main()
