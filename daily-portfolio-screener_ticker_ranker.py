**Create:** `touch atm_iv.py`

**Query:** `open -e atm_iv.py`

```bash
# ticker_ranker.py - Ticker Liquidity Ranking 
"""
CHANGE - major fix. This replaces atm_iv.py and liquidity.py.
Ranks tickers by overall options liquidity to pick best per sector.
"""
import asyncio
import json
import time
import statistics
from datetime import datetime, timezone
from collections import defaultdict
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote, Summary, Greeks
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD
from sectors import get_sectors, PerfTimer

# Liquidity scoring parameters
LIQUID_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL", "GOOG"]
HIGH_VOL_TICKERS = {"TSLA", "NVDA", "AMD", "ROKU", "SNAP", "GME", "AMC"}

def calculate_ticker_liquidity_score(metrics):
    """Calculate comprehensive ticker liquidity score (0-100)"""
    score = 0
    
    # ATM options spread (40 points)
    atm_spread_pct = metrics.get("atm_spread_pct", 100)
    if atm_spread_pct <= 1.0:
        score += 40
    elif atm_spread_pct <= 2.0:
        score += 30
    elif atm_spread_pct <= 5.0:
        score += 20
    elif atm_spread_pct <= 10.0:
        score += 10
    
    # Open interest (25 points)
    avg_oi = metrics.get("avg_open_interest", 0)
    if avg_oi >= 5000:
        score += 25
    elif avg_oi >= 2000:
        score += 20
    elif avg_oi >= 1000:
        score += 15
    elif avg_oi >= 500:
        score += 10
    elif avg_oi > 0:
        score += 5
    
    # Volume (20 points) 
    avg_volume = metrics.get("avg_volume", 0)
    if avg_volume >= 1000:
        score += 20
    elif avg_volume >= 500:
        score += 15
    elif avg_volume >= 200:
        score += 10
    elif avg_volume >= 100:
        score += 5
    
    # IV rank bonus (10 points)
    iv_rank = metrics.get("iv_rank", 0)
    score += min(10, iv_rank * 0.2)
    
    # Chain depth (5 points)
    chain_depth = metrics.get("contracts_analyzed", 0)
    if chain_depth >= 50:
        score += 5
    elif chain_depth >= 20:
        score += 3
    elif chain_depth >= 10:
        score += 1
    
    return min(100, round(score, 1))

async def analyze_ticker_liquidity(ticker, spot_price, sess, timeout=10):
    """Analyze liquidity for a single ticker"""
    print(f"  🔍 {ticker}: Analyzing liquidity...")
    
    try:
        # Get options chain
        chain = get_option_chain(sess, ticker)
        if not chain:
            return {"ticker": ticker, "status": "no_chain"}
        
        # Find 30-45 DTE expiry closest to spot
        today = datetime.now(timezone.utc).date()
        target_exp = None
        for exp_date in sorted(chain.keys()):
            dte = (exp_date - today).days
            if 30 <= dte <= 45:
                target_exp = exp_date
                break
        
        if not target_exp:
            return {"ticker": ticker, "status": "no_target_expiry"}
        
        options = chain[target_exp]
        dte = (target_exp - today).days
        
        # Find ATM call and put
        atm_call = min([opt for opt in options if opt.option_type.value == "C"], 
                      key=lambda x: abs(float(x.strike_price) - spot_price), 
                      default=None)
        atm_put = min([opt for opt in options if opt.option_type.value == "P"],
                     key=lambda x: abs(float(x.strike_price) - spot_price),
                     default=None)
        
        if not atm_call or not atm_put:
            return {"ticker": ticker, "status": "no_atm_options"}
        
        # Sample 20 near-money options for analysis
        sample_options = []
        strike_range = (spot_price * 0.85, spot_price * 1.15)
        for opt in options:
            strike = float(opt.strike_price)
            if strike_range[0] <= strike <= strike_range[1]:
                sample_options.append(opt)
        sample_options = sample_options[:20]  # Limit for speed
        
        if len(sample_options) < 5:
            return {"ticker": ticker, "status": "insufficient_options"}
        
        symbols = [opt.streamer_symbol for opt in sample_options]
        atm_symbols = [atm_call.streamer_symbol, atm_put.streamer_symbol]
        
        print(f"    📡 Sampling {len(symbols)} contracts...")
        
        # Collect market data
        quotes = {}
        summaries = {}
        greeks = {}
        
        async with DXLinkStreamer(sess) as streamer:
            # Subscribe
            await streamer.subscribe(Quote, symbols)
            await streamer.subscribe(Summary, symbols) 
            await streamer.subscribe(Greeks, atm_symbols)
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Collect quotes
                    quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=0.2)
                    if quote and quote.event_symbol in symbols:
                        bid, ask = float(quote.bid_price or 0), float(quote.ask_price or 0)
                        if bid > 0 and ask > 0 and ask >= bid:
                            quotes[quote.event_symbol] = {
                                "bid": bid, "ask": ask, "mid": (bid + ask) / 2,
                                "spread": ask - bid, "spread_pct": 100 * (ask - bid) / ((bid + ask) / 2)
                            }
                except asyncio.TimeoutError:
                    pass
                
                try:
                    # Collect summaries  
                    summary = await asyncio.wait_for(streamer.get_event(Summary), timeout=0.2)
                    if summary and summary.event_symbol in symbols:
                        summaries[summary.event_symbol] = {
                            "open_interest": int(summary.open_interest or 0),
                            "volume": int(summary.prev_day_volume or 0)
                        }
                except asyncio.TimeoutError:
                    pass
                
                try:
                    # Collect ATM Greeks
                    greek = await asyncio.wait_for(streamer.get_event(Greeks), timeout=0.2)
                    if greek and greek.event_symbol in atm_symbols:
                        greeks[greek.event_symbol] = {
                            "iv": float(greek.volatility or 0),
                            "delta": float(greek.delta or 0)
                        }
                except asyncio.TimeoutError:
                    pass
                
                # Early exit if we have good coverage
                if (len(quotes) >= len(symbols) * 0.7 and 
                    len(summaries) >= len(symbols) * 0.5 and
                    len(greeks) >= 1):
                    break
            
            # Cleanup
            await streamer.unsubscribe(Quote, symbols)
            await streamer.unsubscribe(Summary, symbols)
            await streamer.unsubscribe(Greeks, atm_symbols)
        
        # Calculate metrics
        if not quotes:
            return {"ticker": ticker, "status": "no_quote_data"}
        
        # ATM spread
        atm_call_quote = quotes.get(atm_call.streamer_symbol, {})
        atm_put_quote = quotes.get(atm_put.streamer_symbol, {})
        atm_spreads = []
        if atm_call_quote:
            atm_spreads.append(atm_call_quote["spread_pct"])
        if atm_put_quote:
            atm_spreads.append(atm_put_quote["spread_pct"])
        atm_spread_pct = statistics.median(atm_spreads) if atm_spreads else 100
        
        # Average OI and volume
        oi_values = [s.get("open_interest", 0) for s in summaries.values()]
        vol_values = [s.get("volume", 0) for s in summaries.values()]
        avg_oi = statistics.mean(oi_values) if oi_values else 0
        avg_volume = statistics.mean(vol_values) if vol_values else 0
        
        # IV rank (simple heuristic)
        atm_ivs = [g["iv"] for g in greeks.values() if g["iv"] > 0]
        avg_iv = statistics.mean(atm_ivs) if atm_ivs else 0
        
        # Calculate IV rank based on ticker profile
        if ticker in HIGH_VOL_TICKERS:
            iv_rank = min(100, (avg_iv / 0.80) * 100)  # High vol expected
        elif ticker in LIQUID_TICKERS:
            iv_rank = min(100, (avg_iv / 0.40) * 100)  # Med vol expected
        else:
            iv_rank = min(100, (avg_iv / 0.30) * 100)  # Default
        
        # Compile metrics
        metrics = {
            "atm_spread_pct": round(atm_spread_pct, 2),
            "avg_open_interest": round(avg_oi, 0),
            "avg_volume": round(avg_volume, 0),
            "avg_iv": round(avg_iv, 3),
            "iv_rank": round(iv_rank, 1),
            "contracts_analyzed": len(quotes),
            "data_coverage": {
                "quotes": len(quotes),
                "summaries": len(summaries),
                "greeks": len(greeks)
            }
        }
        
        # Calculate final score
        liquidity_score = calculate_ticker_liquidity_score(metrics)
        
        print(f"    🏆 Score: {liquidity_score:.1f} | Spread: {atm_spread_pct:.1f}% | OI: {avg_oi:.0f}")
        
        return {
            "ticker": ticker,
            "status": "analyzed", 
            "spot_price": spot_price,
            "dte": dte,
            "liquidity_score": liquidity_score,
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"    ❌ Error: {str(e)[:50]}")
        return {"ticker": ticker, "status": f"error: {str(e)[:50]}"}

async def rank_tickers_by_liquidity(mode):
    """Rank all tickers in a mode by liquidity"""
    print(f"📊 Ranking {mode.upper()} Tickers by Liquidity")
    print("=" * 60)
    
    # Load quotes
    try:
        with open(f"spot_quotes_{mode}.json", "r") as f:
            quotes_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ spot_quotes_{mode}.json not found")
        return None
    
    quotes = quotes_data["quotes"]
    tickers = list(quotes.keys())
    
    print(f"📋 Analyzing {len(tickers)} tickers...")
    
    sess = Session(USERNAME, PASSWORD)
    results = []
    
    with PerfTimer(f"{mode.upper()} ticker ranking"):
        for i, ticker in enumerate(tickers, 1):
            print(f"\n[{i}/{len(tickers)}] {ticker}")
            spot_price = quotes[ticker]["mid"]
            
            result = await analyze_ticker_liquidity(ticker, spot_price, sess)
            results.append(result)
            
            # Brief pause to avoid rate limits
            await asyncio.sleep(0.1)
    
    # Separate successful vs failed
    successful = [r for r in results if r["status"] == "analyzed"]
    failed = [r for r in results if r["status"] != "analyzed"]
    
    # Sort by liquidity score
    successful.sort(key=lambda x: x["liquidity_score"], reverse=True)
    
    # Group by sector
    sectors = get_sectors(mode)
    ticker_to_sector = {}
    for sector_name, sector_data in sectors.items():
        for ticker in sector_data["tickers"]:
            ticker_to_sector[ticker] = sector_name
    
    by_sector = defaultdict(list)
    for result in successful:
        sector = ticker_to_sector.get(result["ticker"], "Unknown")
        result["sector"] = sector
        by_sector[sector].append(result)
    
    # Create output
    output = {
        "mode": mode,
        "analysis_stats": {
            "total_tickers": len(results),
            "successful": len(successful), 
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "avg_liquidity_score": statistics.mean([r["liquidity_score"] for r in successful]) if successful else 0
        },
        "ticker_rankings": successful,
        "by_sector": dict(by_sector),
        "failed_tickers": failed,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"ticker_rankings_{mode}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📊 {mode.upper()} Ticker Ranking Results:")
    print(f"  ✅ Analyzed: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"  🏆 Avg liquidity score: {output['analysis_stats']['avg_liquidity_score']:.1f}")
    print(f"  📁 Saved: {filename}")
    
    # Show top 5 tickers
    if successful:
        print(f"\n🏆 Top 5 most liquid tickers:")
        for i, ticker_data in enumerate(successful[:5], 1):
            sector = ticker_data["sector"]
            score = ticker_data["liquidity_score"]
            spread = ticker_data["metrics"]["atm_spread_pct"]
            oi = ticker_data["metrics"]["avg_open_interest"]
            print(f"  {i}. {ticker_data['ticker']} ({sector}): {score:.1f} | {spread:.1f}% spread | {oi:.0f} OI")
    
    return output

def main():
    """Main ticker ranking"""
    print("🚀 Ticker Liquidity Ranking")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(rank_tickers_by_liquidity(mode))
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 atm_iv.py`
