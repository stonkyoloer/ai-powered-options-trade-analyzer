**Create:** `touch market_prices.py`

**Query:** `open -e market_prices.py`

```bash
# market_prices.py - Real-time Bid/Ask Prices for Credit Spreads
"""
Collects real-time bid/ask prices for all options contracts.
Essential for calculating credit spreads and actual executable prices.
"""
import asyncio
import json
from datetime import datetime, timezone
from collections import defaultdict
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

async def collect_market_prices(mode, verbose=True):
    """Collect market prices for all options contracts"""
    if verbose:
        print(f"💰 Collecting Market Prices - {mode.upper()}")
        print("=" * 60)
    
    # Load contracts from options_chains.py
    try:
        with open(f"options_contracts_{mode}.json", "r") as f:
            contracts_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ options_contracts_{mode}.json not found. Run options_chains.py first.")
        return None
    
    # Extract all contract symbols
    all_symbols = []
    symbol_info = {}
    
    for ticker, ticker_data in contracts_data["contracts_by_ticker"].items():
        for exp_data in ticker_data["expiration_dates"].values():
            for contract in exp_data["contracts"]:
                symbol = contract["streamer_symbol"]
                all_symbols.append(symbol)
                symbol_info[symbol] = {
                    "ticker": ticker,
                    "strike": contract["strike"],
                    "type": contract["option_type"],
                    "dte": contract["dte"]
                }
    
    if verbose:
        print(f"🎯 Getting prices for {len(all_symbols):,} contracts...")
    
    sess = Session(USERNAME, PASSWORD)
    market_prices = {}
    
    # Process in batches
    batch_size = 500
    total_collected = 0
    
    async with DXLinkStreamer(sess) as streamer:
        for batch_start in range(0, len(all_symbols), batch_size):
            batch_end = min(batch_start + batch_size, len(all_symbols))
            batch_symbols = all_symbols[batch_start:batch_end]
            
            if verbose:
                batch_num = batch_start // batch_size + 1
                total_batches = (len(all_symbols) + batch_size - 1) // batch_size
                print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch_symbols)} symbols)")
            
            # Subscribe to quotes
            await streamer.subscribe(Quote, batch_symbols)
            
            # Collect prices for this batch
            batch_prices = {}
            start_time = asyncio.get_event_loop().time()
            last_report = start_time
            
            while (asyncio.get_event_loop().time() - start_time) < 30:
                now = asyncio.get_event_loop().time()
                
                # Progress report
                if verbose and now - last_report >= 5:
                    print(f"    📊 Batch progress: {len(batch_prices)}/{len(batch_symbols)} prices")
                    last_report = now
                
                # Check if we have all prices
                if len(batch_prices) >= len(batch_symbols):
                    if verbose:
                        print(f"    ✅ All prices collected for batch!")
                    break
                
                try:
                    quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=1.0)
                    
                    if quote and quote.event_symbol in batch_symbols:
                        # Only save first valid quote per symbol
                        if quote.event_symbol not in batch_prices:
                            bid = float(quote.bid_price or 0)
                            ask = float(quote.ask_price or 0)
                            
                            if bid > 0 and ask > 0 and ask >= bid:
                                info = symbol_info[quote.event_symbol]
                                
                                batch_prices[quote.event_symbol] = {
                                    "symbol": quote.event_symbol,
                                    "ticker": info["ticker"],
                                    "strike": info["strike"],
                                    "type": info["type"],
                                    "dte": info["dte"],
                                    "bid": round(bid, 4),
                                    "ask": round(ask, 4),
                                    "mid": round((bid + ask) / 2, 4),
                                    "spread": round(ask - bid, 4),
                                    "spread_pct": round(100 * (ask - bid) / ((bid + ask) / 2), 3) if (bid + ask) > 0 else 0,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                                total_collected += 1
                
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    if verbose:
                        print(f"    ⚠️ Quote error: {e}")
                    continue
            
            # Unsubscribe from batch
            await streamer.unsubscribe(Quote, batch_symbols)
            
            # Merge batch results
            market_prices.update(batch_prices)
            
            if verbose:
                elapsed = asyncio.get_event_loop().time() - start_time
                print(f"    ✅ Batch complete: {len(batch_prices)} prices in {elapsed:.1f}s")
            
            # Brief pause between batches
            await asyncio.sleep(0.5)
    
    # Organize by ticker
    prices_by_ticker = defaultdict(list)
    for symbol, price_data in market_prices.items():
        prices_by_ticker[price_data["ticker"]].append(price_data)
    
    # Calculate statistics
    stats = {
        "total_requested": len(all_symbols),
        "prices_collected": len(market_prices),
        "success_rate": len(market_prices) / len(all_symbols) * 100 if all_symbols else 0,
        "tickers_with_prices": len(prices_by_ticker),
        "avg_spread": sum(p["spread"] for p in market_prices.values()) / len(market_prices) if market_prices else 0,
        "avg_spread_pct": sum(p["spread_pct"] for p in market_prices.values()) / len(market_prices) if market_prices else 0
    }
    
    # Create output
    result = {
        "mode": mode,
        "collection_stats": stats,
        "market_prices": market_prices,
        "prices_by_ticker": dict(prices_by_ticker),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"market_prices_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Market Price Results:")
        print(f"  ✅ Success: {len(market_prices):,}/{len(all_symbols):,} ({stats['success_rate']:.1f}%)")
        print(f"  💰 Avg spread: ${stats['avg_spread']:.3f} ({stats['avg_spread_pct']:.2f}%)")
        print(f"  🏢 Tickers with prices: {len(prices_by_ticker)}")
        print(f"  📁 Saved: {filename}")
        
        # Show tightest spreads
        if market_prices:
            tight_spreads = sorted(market_prices.values(), key=lambda x: x["spread_pct"])[:5]
            print(f"  🎯 Tightest spreads:")
            for price in tight_spreads:
                print(f"    {price['ticker']} ${price['strike']:.0f} {price['type']}: {price['spread_pct']:.2f}% (${price['spread']:.3f})")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Market Price Collector")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(collect_market_prices(mode))
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 market_prices.py`
