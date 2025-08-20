# ticker_ranker.py - Ticker Liquidity Ranking for Credit Spreads
"""
FIXED - Ranks all validated tickers by options liquidity quality.
Focuses on metrics that matter for credit spreads: tight spreads, high OI, good volume.
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

# Liquidity scoring parameters for credit spreads
LIQUID_BENCHMARK_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL"]
HIGH_VOL_TICKERS = {"TSLA", "NVDA", "AMD", "ROKU", "SNAP", "GME", "AMC"}

def calculate_credit_spread_liquidity_score(metrics):
    """Calculate liquidity score optimized for credit spreads (0-100)"""
    score = 0
    
    # ATM options spread (45 points) - MOST IMPORTANT for credit spreads
    atm_spread_pct = metrics.get("atm_spread_pct", 100)
    if atm_spread_pct <= 1.0:
        score += 45
    elif atm_spread_pct <= 2.0:
        score += 35
    elif atm_spread_pct <= 3.0:
        score += 25
    elif atm_spread_pct <= 5.0:
        score += 15
    elif atm_spread_pct <= 8.0:
        score += 5
    
    # Open interest (30 points) - Critical for credit spread exits
    avg_oi = metrics.get("avg_open_interest", 0)
    if avg_oi >= 3000:
        score += 30
    elif avg_oi >= 1500:
        score += 25
    elif avg_oi >= 800:
        score += 20
    elif avg_oi >= 400:
        score += 15
    elif avg_oi >= 200:
        score += 10
    elif avg_oi > 0:
        score += 5
    
    # Volume (15 points) - Daily activity
    avg_volume = metrics.get("avg_volume", 0)
    if avg_volume >= 800:
        score += 15
    elif avg_volume >= 400:
        score += 12
    elif avg_volume >= 200:
        score += 9
    elif avg_volume >= 100:
        score += 6
    elif avg_volume >= 50:
        score += 3
    
    # Chain depth (10 points) - More strikes = better spread opportunities
    chain_depth = metrics.get("contracts_analyzed", 0)
    if chain_depth >= 40:
        score += 10
    elif chain_depth >= 25:
        score += 7
    elif chain_depth >= 15:
        score += 4
    elif chain_depth >= 8:
        score += 2
    
    return min(100, round(score, 1))

async def analyze_ticker_for_credit_spreads(ticker, spot_price, sess, timeout=12):
    """Analyze a ticker's suitability for credit spreads"""
    print(f"  🔍 {ticker}: Analyzing credit spread liquidity...")
    
    try:
        # Get options chain
        chain = get_option_chain(sess, ticker)
        if not chain:
            return {"ticker": ticker, "status": "no_chain"}
        
        # Find optimal expiry for credit spreads (30-45 DTE)
        today = datetime.now(timezone.utc).date()
        target_exp = None
        for exp_date in sorted(chain.keys()):
            dte = (exp_date - today).days
            if 30 <= dte <= 45:
                target_exp = exp_date
                break
        
        if not target_exp:
            # Fallback to 21-60 DTE range
            for exp_date in sorted(chain.keys()):
                dte = (exp_date - today).days
                if 21 <= dte <= 60:
                    target_exp = exp_date
                    break
        
        if not target_exp:
            return {"ticker": ticker, "status": "no_suitable_expiry"}
        
        options = chain[target_exp]
        dte = (target_exp - today).days
        
        # Find ATM and near-money options (critical for credit spreads)
        atm_call = min([opt for opt in options if opt.option_type.value == "C"], 
                      key=lambda x: abs(float(x.strike_price) - spot_price), 
                      default=None)
        atm_put = min([opt for opt in options if opt.option_type.value == "P"],
                     key=lambda x: abs(float(x.strike_price) - spot_price),
                     default=None)
        
        if not atm_call or not atm_put:
            return {"ticker": ticker, "status": "no_atm_options"}
        
        # Sample options for credit spread analysis (focus on 85%-115% of spot)
        credit_spread_options = []
        strike_range = (spot_price * 0.85, spot_price * 1.15)
        for opt in options:
            strike = float(opt.strike_price)
            if strike_range[0] <= strike <= strike_range[1]:
                credit_spread_options.append(opt)
        
        # Limit sample size for performance
        credit_spread_options = credit_spread_options[:30]
        
        if len(credit_spread_options) < 8:
            return {"ticker": ticker, "status": "insufficient_credit_spread_options"}
        
        symbols = [opt.streamer_symbol for opt in credit_spread_options]
        atm_symbols = [atm_call.streamer_symbol, atm_put.streamer_symbol]
        
        print(f"    📡 Analyzing {len(symbols)} credit spread candidates...")
        
        # Collect market data
        quotes = {}
        summaries = {}
        greeks = {}
        
        async with DXLinkStreamer(sess) as streamer:
            # Subscribe to data feeds
            await streamer.subscribe(Quote, symbols)
            await streamer.subscribe(Summary, symbols) 
            await streamer.subscribe(Greeks, atm_symbols)
            
            start_time = time.time()
            no_data_count = 0
            
            while time.time() - start_time < timeout:
                try:
                    # Collect quotes (bid/ask for spreads)
                    quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=0.3)
                    if quote and quote.event_symbol in symbols:
                        bid, ask = float(quote.bid_price or 0), float(quote.ask_price or 0)
                        if bid > 0 and ask > 0 and ask >= bid:
                            quotes[quote.event_symbol] = {
                                "bid": bid, "ask": ask, "mid": (bid + ask) / 2,
                                "spread": ask - bid, "spread_pct": 100 * (ask - bid) / ((bid + ask) / 2)
                            }
                            no_data_count = 0
                except asyncio.TimeoutError:
                    no_data_count += 1
                    if no_data_count > 10:
                        break
                    continue
                
                try:
                    # Collect summaries (OI and volume)
                    summary = await asyncio.wait_for(streamer.get_event(Summary), timeout=0.3)
                    if summary and summary.event_symbol in symbols:
                        summaries[summary.event_symbol] = {
                            "open_interest": int(summary.open_interest or 0),
                            "volume": int(summary.prev_day_volume or 0)
                        }
                except asyncio.TimeoutError:
                    continue
                
                try:
                    # Collect ATM Greeks (for IV analysis)
                    greek = await asyncio.wait_for(streamer.get_event(Greeks), timeout=0.3)
                    if greek and greek.event_symbol in atm_symbols:
                        greeks[greek.event_symbol] = {
                            "iv": float(greek.volatility or 0),
                            "delta": float(greek.delta or 0)
                        }
                except asyncio.TimeoutError:
                    continue
                
                # Early exit if we have good coverage
                quote_coverage = len(quotes) / len(symbols)
                summary_coverage = len(summaries) / len(symbols)
                if quote_coverage >= 0.7 and summary_coverage >= 0.5 and len(greeks) >= 1:
                    print(f"    ✅ Good coverage achieved early")
                    break
            
            # Cleanup subscriptions
            await streamer.unsubscribe(Quote, symbols)
            await streamer.unsubscribe(Summary, symbols)
            await streamer.unsubscribe(Greeks, atm_symbols)
        
        # Calculate liquidity metrics
        if not quotes:
            return {"ticker": ticker, "status": "no_quote_data"}
        
        # ATM spread analysis (critical for credit spreads)
        atm_call_quote = quotes.get(atm_call.streamer_symbol, {})
        atm_put_quote = quotes.get(atm_put.streamer_symbol, {})
        atm_spreads = []
        if atm_call_quote:
            atm_spreads.append(atm_call_quote["spread_pct"])
        if atm_put_quote:
            atm_spreads.append(atm_put_quote["spread_pct"])
        atm_spread_pct = statistics.median(atm_spreads) if atm_spreads else 100
        
        # Average OI and volume (for credit spread liquidity)
        oi_values = [s.get("open_interest", 0) for s in summaries.values() if s.get("open_interest", 0) > 0]
        vol_values = [s.get("volume", 0) for s in summaries.values() if s.get("volume", 0) > 0]
        avg_oi = statistics.mean(oi_values) if oi_values else 0
        avg_volume = statistics.mean(vol_values) if vol_values else 0
        
        # IV analysis
        atm_ivs = [g["iv"] for g in greeks.values() if g["iv"] > 0]
        avg_iv = statistics.mean(atm_ivs) if atm_ivs else 0
        
        # Compile metrics for credit spread analysis
        metrics = {
            "atm_spread_pct": round(atm_spread_pct, 2),
            "avg_open_interest": round(avg_oi, 0),
            "avg_volume": round(avg_volume, 0),
            "avg_iv": round(avg_iv, 3),
            "contracts_analyzed": len(quotes),
            "dte_target": dte,
            "data_quality": {
                "quote_coverage": round(len(quotes) / len(symbols) * 100, 1),
                "summary_coverage": round(len(summaries) / len(symbols) * 100, 1),
                "greeks_collected": len(greeks)
            }
        }
        
        # Calculate credit spread liquidity score
        liquidity_score = calculate_credit_spread_liquidity_score(metrics)
        
        print(f"    🏆 Score: {liquidity_score:.1f} | Spread: {atm_spread_pct:.1f}% | OI: {avg_oi:.0f} | Vol: {avg_volume:.0f}")
        
        return {
            "ticker": ticker,
            "status": "analyzed", 
            "spot_price": spot_price,
            "dte": dte,
            "liquidity_score": liquidity_score,
            "metrics": metrics,
            "credit_spread_suitability": "excellent" if liquidity_score >= 80 else "good" if liquidity_score >= 60 else "fair" if liquidity_score >= 40 else "poor",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"    ❌ Error: {str(e)[:60]}")
        return {"ticker": ticker, "status": f"error: {str(e)[:60]}"}

async def rank_all_tickers_for_credit_spreads(mode):
    """Rank all tickers in mode by credit spread liquidity"""
    print(f"📊 Ranking {mode.upper()} Tickers for Credit Spread Liquidity")
    print("=" * 70)
    
    # Load spot quotes from previous step
    try:
        with open(f"spot_quotes_{mode}.json", "r") as f:
            quotes_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ spot_quotes_{mode}.json not found. Run spot.py first.")
        return None
    
    quotes = quotes_data["quotes"]
    tickers = list(quotes.keys())
    
    print(f"📋 Analyzing {len(tickers)} tickers for credit spread opportunities...")
    
    sess = Session(USERNAME, PASSWORD)
    results = []
    
    with PerfTimer(f"{mode.upper()} credit spread liquidity ranking"):
        for i, ticker in enumerate(tickers, 1):
            print(f"\n[{i}/{len(tickers)}] {ticker}")
            spot_price = quotes[ticker]["mid"]
            
            result = await analyze_ticker_for_credit_spreads(ticker, spot_price, sess)
            results.append(result)
            
            # Brief pause to avoid overwhelming the API
            await asyncio.sleep(0.2)
    
    # Separate successful vs failed analyses
    successful = [r for r in results if r["status"] == "analyzed"]
    failed = [r for r in results if r["status"] != "analyzed"]
    
    # Sort by liquidity score (best for credit spreads first)
    successful.sort(key=lambda x: x["liquidity_score"], reverse=True)
    
    # Group by sector for analysis
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
    
    # Create comprehensive output
    output = {
        "mode": mode,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "analysis_stats": {
            "total_tickers": len(results),
            "successfully_analyzed": len(successful), 
            "failed_analysis": len(failed),
            "success_rate": round(len(successful) / len(results) * 100, 1) if results else 0,
            "avg_liquidity_score": round(statistics.mean([r["liquidity_score"] for r in successful]), 1) if successful else 0,
            "excellent_tickers": len([r for r in successful if r["liquidity_score"] >= 80]),
            "good_tickers": len([r for r in successful if 60 <= r["liquidity_score"] < 80]),
            "fair_tickers": len([r for r in successful if 40 <= r["liquidity_score"] < 60]),
            "poor_tickers": len([r for r in successful if r["liquidity_score"] < 40])
        },
        "ticker_rankings": successful,
        "by_sector": dict(by_sector),
        "failed_tickers": failed
    }
    
    # Save results
    filename = f"ticker_rankings_{mode}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📊 {mode.upper()} Credit Spread Liquidity Analysis Complete:")
    print(f"  ✅ Analyzed: {len(successful)}/{len(results)} ({output['analysis_stats']['success_rate']:.1f}%)")
    print(f"  🏆 Avg liquidity score: {output['analysis_stats']['avg_liquidity_score']:.1f}")
    print(f"  ⭐ Excellent (≥80): {output['analysis_stats']['excellent_tickers']}")
    print(f"  ✅ Good (60-79): {output['analysis_stats']['good_tickers']}")
    print(f"  ⚠️ Fair (40-59): {output['analysis_stats']['fair_tickers']}")
    print(f"  ❌ Poor (<40): {output['analysis_stats']['poor_tickers']}")
    print(f"  📁 Saved: {filename}")
    
    # Show top performers
    if successful:
        print(f"\n🏆 Top 5 Credit Spread Candidates:")
        for i, ticker_data in enumerate(successful[:5], 1):
            ticker = ticker_data["ticker"]
            sector = ticker_data["sector"]
            score = ticker_data["liquidity_score"]
            spread = ticker_data["metrics"]["atm_spread_pct"]
            oi = ticker_data["metrics"]["avg_open_interest"]
            vol = ticker_data["metrics"]["avg_volume"]
            print(f"  {i}. {ticker} ({sector}): {score:.1f} | {spread:.1f}% spread | {oi:.0f} OI | {vol:.0f} vol")
    
    return output

def main():
    """Main ticker ranking for credit spreads"""
    print("🚀 Credit Spread Liquidity Analyzer")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        result = asyncio.run(rank_all_tickers_for_credit_spreads(mode))
        if result:
            excellent = result["analysis_stats"]["excellent_tickers"]
            good = result["analysis_stats"]["good_tickers"]
            print(f"🎯 {mode.upper()}: {excellent + good} tickers ready for credit spreads")
        print()

if __name__ == "__main__":
    main()
