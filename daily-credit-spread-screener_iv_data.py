**Create:** `touch iv_data.py`

**Query:**  `open -e iv_data.py`

```bash
# iv_data.py - Implied Volatility Collection
"""
Collects implied volatility for all options contracts.
Uses live Greeks data from TastyTrade for accurate IV values.
"""
import asyncio
import json
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from config import USERNAME, PASSWORD

async def collect_iv_data(mode, verbose=True):
    """Collect IV data for all options contracts in a mode"""
    if verbose:
        print(f"📈 Collecting IV Data - {mode.upper()}")
        print("=" * 60)
    
    # Load contracts from previous step
    try:
        with open(f"options_contracts_{mode}.json", "r") as f:
            contracts_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ options_contracts_{mode}.json not found. Run options_chains.py first.")
        return None
    
    # Extract all contract symbols
    all_symbols = []
    symbol_to_ticker = {}
    
    for ticker, ticker_data in contracts_data["contracts_by_ticker"].items():
        for exp_data in ticker_data["expiration_dates"].values():
            for contract in exp_data["contracts"]:
                symbol = contract["streamer_symbol"]
                all_symbols.append(symbol)
                symbol_to_ticker[symbol] = ticker
    
    if verbose:
        print(f"🎯 Collecting IV for {len(all_symbols):,} contracts...")
    
    sess = Session(USERNAME, PASSWORD)
    iv_data = {}
    
    # Process in batches to avoid overwhelming the connection
    batch_size = 800
    total_collected = 0
    
    async with DXLinkStreamer(sess) as streamer:
        for batch_start in range(0, len(all_symbols), batch_size):
            batch_end = min(batch_start + batch_size, len(all_symbols))
            batch_symbols = all_symbols[batch_start:batch_end]
            
            if verbose:
                batch_num = batch_start // batch_size + 1
                total_batches = (len(all_symbols) + batch_size - 1) // batch_size
                print(f"\n📦 Processing batch {batch_num}/{total_batches}")
                print(f"    Symbols {batch_start + 1} to {batch_end} of {len(all_symbols):,}")
            
            # Subscribe to this batch
            await streamer.subscribe(Greeks, batch_symbols)
            
            # Collect data for this batch
            batch_collected = 0
            start_time = asyncio.get_event_loop().time()
            no_data_timeout = 0
            
            # Collect for up to 45 seconds per batch
            while (asyncio.get_event_loop().time() - start_time) < 45 and no_data_timeout < 8:
                try:
                    greeks = await asyncio.wait_for(streamer.get_event(Greeks), timeout=1.5)
                    
                    if greeks and greeks.event_symbol in batch_symbols:
                        # Only collect if we haven't seen this symbol yet
                        if greeks.event_symbol not in iv_data:
                            iv = float(greeks.volatility or 0)
                            
                            if iv > 0:  # Valid IV
                                iv_data[greeks.event_symbol] = {
                                    'symbol': greeks.event_symbol,
                                    'ticker': symbol_to_ticker[greeks.event_symbol],
                                    'iv': round(iv, 4),
                                    'delta': round(float(greeks.delta or 0), 4),
                                    'theta': round(float(greeks.theta or 0), 4),
                                    'gamma': round(float(greeks.gamma or 0), 4),
                                    'vega': round(float(greeks.vega or 0), 4),
                                    'collected_at': datetime.now(timezone.utc).isoformat()
                                }
                                
                                batch_collected += 1
                                total_collected += 1
                                no_data_timeout = 0  # Reset timeout
                                
                                if verbose and batch_collected % 100 == 0:
                                    print(f"      📊 Batch progress: {batch_collected} IVs collected")
                
                except asyncio.TimeoutError:
                    no_data_timeout += 1
                    continue
                except Exception as e:
                    if verbose:
                        print(f"      ⚠️ Greeks error: {e}")
                    continue
            
            if verbose:
                elapsed = asyncio.get_event_loop().time() - start_time
                print(f"      ✅ Batch complete: {batch_collected} IVs in {elapsed:.1f}s")
            
            # Unsubscribe from this batch
            await streamer.unsubscribe(Greeks, batch_symbols)
            
            # Brief pause between batches
            await asyncio.sleep(0.5)
    
    # Organize results by ticker
    iv_by_ticker = {}
    for symbol, data in iv_data.items():
        ticker = data['ticker']
        if ticker not in iv_by_ticker:
            iv_by_ticker[ticker] = []
        iv_by_ticker[ticker].append(data)
    
    # Create output
    result = {
        'mode': mode,
        'collection_stats': {
            'total_symbols_requested': len(all_symbols),
            'ivs_collected': len(iv_data),
            'tickers_with_iv': len(iv_by_ticker),
            'success_rate': len(iv_data) / len(all_symbols) * 100 if all_symbols else 0,
            'avg_iv': sum(data['iv'] for data in iv_data.values()) / len(iv_data) if iv_data else 0
        },
        'iv_by_symbol': iv_data,
        'iv_by_ticker': iv_by_ticker,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"iv_data_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} IV Collection Results:")
        print(f"  ✅ Success: {len(iv_data):,}/{len(all_symbols):,} ({len(iv_data)/len(all_symbols)*100:.1f}%)")
        print(f"  📈 Average IV: {result['collection_stats']['avg_iv']:.3f}")
        print(f"  🏢 Tickers with IV: {len(iv_by_ticker)}")
        print(f"  📁 Saved: {filename}")
        
        if iv_by_ticker:
            # Show tickers with highest average IV
            ticker_avg_iv = {}
            for ticker, iv_list in iv_by_ticker.items():
                if iv_list:
                    avg_iv = sum(item['iv'] for item in iv_list) / len(iv_list)
                    ticker_avg_iv[ticker] = avg_iv
            
            top_iv_tickers = sorted(ticker_avg_iv.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  🔥 Highest IV tickers:")
            for ticker, avg_iv in top_iv_tickers:
                print(f"    {ticker}: {avg_iv:.3f}")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 IV Data Collector")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(collect_iv_data(mode))
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 iv_data.py`
