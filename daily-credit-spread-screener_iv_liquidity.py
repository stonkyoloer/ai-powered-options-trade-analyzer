**Create:** `touch iv_liquidity.py`

**Query:** `touch iv_liquidity.py`

```bash
# iv_liquidity.py - Advanced IV & Liquidity Analysis
"""
Comprehensive IV analysis and liquidity scoring for credit spread selection.
Combines multiple data sources for optimal contract selection.
"""
import asyncio
import json
import numpy as np
from datetime import datetime, timezone
from collections import defaultdict
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Summary
from config import USERNAME, PASSWORD

def calculate_liquidity_score(open_interest, volume, spread, spread_pct, ticker):
    """Calculate comprehensive liquidity score (0-100)"""
    score = 0
    
    # Open interest component (40 points)
    if open_interest >= 1000:
        score += 40
    elif open_interest >= 500:
        score += 30
    elif open_interest >= 100:
        score += 20
    elif open_interest > 0:
        score += min(20, (open_interest / 100) * 20)
    
    # Volume component (25 points)
    if volume >= 1000:
        score += 25
    elif volume >= 500:
        score += 20
    elif volume >= 100:
        score += 15
    elif volume >= 50:
        score += 10
    elif volume > 0:
        score += min(10, (volume / 50) * 10)
    
    # Spread component (35 points)
    # Adjust thresholds based on ticker liquidity
    liquid_tickers = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL"]
    
    if ticker in liquid_tickers:
        # Tighter spreads expected for liquid names
        if spread <= 0.05:
            score += 35
        elif spread <= 0.10:
            score += 25
        elif spread <= 0.20:
            score += 15
        elif spread <= 0.50:
            score += 5
    else:
        # More lenient for other tickers
        if spread <= 0.10:
            score += 35
        elif spread <= 0.20:
            score += 25
        elif spread <= 0.50:
            score += 15
        elif spread <= 1.00:
            score += 5
    
    return min(100, score)

async def analyze_iv_liquidity(mode, verbose=True):
    """Perform advanced IV and liquidity analysis"""
    if verbose:
        print(f"📊 Advanced IV & Liquidity Analysis - {mode.upper()}")
        print("=" * 60)
    
    # Load previous data
    try:
        with open(f"market_prices_{mode}.json", "r") as f:
            price_data = json.load(f)
        
        with open(f"risk_analysis_{mode}.json", "r") as f:
            risk_data = json.load(f)
        
        with open(f"iv_data_{mode}.json", "r") as f:
            iv_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Missing required file: {e}")
        print("   Run market_prices.py and risk_analysis.py first.")
        return None
    
    # Get all symbols with complete data
    symbols_with_data = set(price_data["market_prices"].keys()) & set(risk_data["greeks_data"].keys())
    
    if verbose:
        print(f"🎯 Analyzing {len(symbols_with_data):,} contracts with complete data...")
    
    sess = Session(USERNAME, PASSWORD)
    summary_data = {}
    
    # Convert to list for batching
    symbols_list = list(symbols_with_data)
    batch_size = 500
    
    async with DXLinkStreamer(sess) as streamer:
        for batch_start in range(0, len(symbols_list), batch_size):
            batch_end = min(batch_start + batch_size, len(symbols_list))
            batch_symbols = symbols_list[batch_start:batch_end]
            
            if verbose:
                batch_num = batch_start // batch_size + 1
                total_batches = (len(symbols_list) + batch_size - 1) // batch_size
                print(f"\n📦 Batch {batch_num}/{total_batches} - Getting Summary data")
            
            # Subscribe to Summary
            await streamer.subscribe(Summary, batch_symbols)
            
            # Collect Summary data
            batch_summary = {}
            start_time = asyncio.get_event_loop().time()
            no_data_timeout = 0
            
            while (asyncio.get_event_loop().time() - start_time) < 30 and no_data_timeout < 5:
                try:
                    summary = await asyncio.wait_for(streamer.get_event(Summary), timeout=1.0)
                    
                    if summary and summary.event_symbol in batch_symbols:
                        if summary.event_symbol not in batch_summary:
                            batch_summary[summary.event_symbol] = {
                                "open_interest": int(summary.open_interest or 0),
                                "volume": int(summary.prev_day_volume or 0),
                                "day_high": float(summary.day_high_price or 0),
                                "day_low": float(summary.day_low_price or 0)
                            }
                            no_data_timeout = 0
                
                except asyncio.TimeoutError:
                    no_data_timeout += 1
                    continue
            
            # Unsubscribe
            await streamer.unsubscribe(Summary, batch_symbols)
            
            summary_data.update(batch_summary)
            
            if verbose:
                print(f"    ✅ Collected {len(batch_summary)} summaries")
            
            await asyncio.sleep(0.5)
    
    # Combine all data and calculate scores
    enhanced_contracts = {}
    
    for symbol in symbols_with_data:
        price_info = price_data["market_prices"][symbol]
        greek_info = risk_data["greeks_data"][symbol]
        
        # Get summary data or use defaults
        if symbol in summary_data:
            sum_info = summary_data[symbol]
        else:
            sum_info = {"open_interest": 0, "volume": 0}
        
        # Calculate liquidity score
        liquidity_score = calculate_liquidity_score(
            sum_info["open_interest"],
            sum_info["volume"],
            price_info["spread"],
            price_info["spread_pct"],
            price_info["ticker"]
        )
        
        enhanced_contracts[symbol] = {
            "symbol": symbol,
            "ticker": price_info["ticker"],
            "strike": price_info["strike"],
            "type": price_info["type"],
            "dte": price_info["dte"],
            "bid": price_info["bid"],
            "ask": price_info["ask"],
            "mid": price_info["mid"],
            "spread": price_info["spread"],
            "spread_pct": price_info["spread_pct"],
            "iv": greek_info["iv"],
            "delta": greek_info["delta"],
            "theta": greek_info["theta"],
            "gamma": greek_info["gamma"],
            "vega": greek_info["vega"],
            "open_interest": sum_info["open_interest"],
            "volume": sum_info["volume"],
            "liquidity_score": liquidity_score,
            "is_liquid": liquidity_score >= 70
        }
    
    # Organize by ticker
    contracts_by_ticker = defaultdict(list)
    for contract in enhanced_contracts.values():
        contracts_by_ticker[contract["ticker"]].append(contract)
    
    # Calculate ticker-level statistics
    ticker_stats = {}
    for ticker, contracts in contracts_by_ticker.items():
        liquid_contracts = [c for c in contracts if c["is_liquid"]]
        
        ticker_stats[ticker] = {
            "ticker": ticker,
            "total_contracts": len(contracts),
            "liquid_contracts": len(liquid_contracts),
            "avg_iv": np.mean([c["iv"] for c in contracts]) if contracts else 0,
            "avg_liquidity_score": np.mean([c["liquidity_score"] for c in contracts]) if contracts else 0,
            "max_open_interest": max((c["open_interest"] for c in contracts), default=0),
            "max_volume": max((c["volume"] for c in contracts), default=0),
            "contracts_30_45_dte": len([c for c in contracts if 30 <= c["dte"] <= 45]),
            "high_iv_contracts": len([c for c in contracts if c["iv"] > 0.30])
        }
    
    # Find best contracts for credit spreads
    # Focus on 30-45 DTE with good liquidity
    credit_spread_candidates = []
    for contract in enhanced_contracts.values():
        if (30 <= contract["dte"] <= 45 and 
            contract["is_liquid"] and 
            contract["iv"] > 0.20):
            credit_spread_candidates.append(contract)
    
    # Sort by liquidity score
    credit_spread_candidates.sort(key=lambda x: x["liquidity_score"], reverse=True)
    
    # Create output
    result = {
        "mode": mode,
        "analysis_stats": {
            "total_contracts_analyzed": len(enhanced_contracts),
            "contracts_with_summary": len(summary_data),
            "liquid_contracts": len([c for c in enhanced_contracts.values() if c["is_liquid"]]),
            "tickers_analyzed": len(ticker_stats),
            "credit_spread_candidates": len(credit_spread_candidates),
            "avg_liquidity_score": np.mean([c["liquidity_score"] for c in enhanced_contracts.values()]) if enhanced_contracts else 0
        },
        "enhanced_contracts": enhanced_contracts,
        "ticker_stats": ticker_stats,
        "credit_spread_candidates": credit_spread_candidates[:100],  # Top 100
        "liquidity_thresholds": {
            "min_score": 70,
            "min_open_interest": 100,
            "max_spread_liquid": 0.10,
            "max_spread_other": 0.50
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"iv_liquidity_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} IV & Liquidity Results:")
        print(f"  ✅ Contracts analyzed: {len(enhanced_contracts):,}")
        print(f"  💧 Liquid contracts: {result['analysis_stats']['liquid_contracts']:,}")
        print(f"  🎯 Credit spread candidates: {len(credit_spread_candidates)}")
        print(f"  📈 Avg liquidity score: {result['analysis_stats']['avg_liquidity_score']:.1f}")
        print(f"  📁 Saved: {filename}")
        
        # Show top tickers by liquidity
        if ticker_stats:
            top_tickers = sorted(ticker_stats.values(), 
                               key=lambda x: x["avg_liquidity_score"], reverse=True)[:5]
            print(f"\n  🏆 Top tickers by liquidity:")
            for t in top_tickers:
                print(f"    {t['ticker']}: Score {t['avg_liquidity_score']:.1f}, {t['liquid_contracts']}/{t['total_contracts']} liquid")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Advanced IV & Liquidity Analyzer")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(analyze_iv_liquidity(mode))
        print()

if __name__ == "__main__":
    main()
```
**Run:** `python3 iv_liquidity.py`
