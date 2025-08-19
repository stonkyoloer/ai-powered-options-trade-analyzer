**Create:** `touch liquidity.py`
**Query:** `open -e liquidity.py`

```bash
# liquidity.py - Options Liquidity Analysis & Basket Creation
"""
Analyzes delta-30 options liquidity and creates final trading baskets.
Selects best ticker from each sector for portfolio construction.
"""
import asyncio
import json
import statistics
from datetime import datetime, timezone
from collections import defaultdict, deque
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote, Summary, Greeks
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD
from sectors import get_sectors

# Liquidity scoring thresholds
REF_INSIDE_RATIO = 0.70
REF_NBBO_AGE_MS = 1500
REF_TPM = 25
REF_SPREAD_ABS = 0.05
REF_OI_MIN = 1000

# Option selection parameters
SAMPLE_SEC = 15.0
MAX_OPT_SYMBOLS = 50
MONEYNESS_WIDTH = 0.50

def med(a): return statistics.median(a) if a else 0.0

def calculate_liquidity_score(metrics, ivr=0):
    """Calculate composite liquidity score (0-100)"""
    spread_med = metrics.get("spread_med_delta30", 999)
    inside_ratio = metrics.get("inside_ratio", 0)
    ticks_pm = metrics.get("ticks_per_min", 0)
    nbbo_age_ms = metrics.get("nbbo_age_ms", 99999)
    oi_min = metrics.get("oi_min", 0)
    
    # Component scores (0-100 each)
    spread_score = max(0, min(100, 100 * (1 - spread_med / max(REF_SPREAD_ABS * 10, 0.01))))
    inside_score = min(100, 100 * inside_ratio / REF_INSIDE_RATIO)
    tick_score = min(100, 100 * ticks_pm / REF_TPM)
    freshness_score = max(0, min(100, 100 * (1 - nbbo_age_ms / (REF_NBBO_AGE_MS * 10))))
    oi_score = min(100, 100 * oi_min / REF_OI_MIN)
    ivr_score = min(100, ivr * 0.05)  # Small IV rank bonus
    
    # Weighted composite
    composite = (
        spread_score * 0.25 +
        inside_score * 0.20 +
        tick_score * 0.20 +
        freshness_score * 0.15 +
        oi_score * 0.15 +
        ivr_score * 0.05
    )
    
    return round(composite, 1)

def choose_options_subset(options, spot):
    """Choose options near the money for analysis"""
    calls, puts = [], []
    lo, hi = spot * (1.0 - MONEYNESS_WIDTH), spot * (1.0 + MONEYNESS_WIDTH)
    
    for opt in options:
        strike = float(opt.strike_price)
        if lo <= strike <= hi:
            if opt.option_type.value == "C":
                calls.append(opt)
            else:
                puts.append(opt)
    
    # Sort by distance from spot, take closest
    calls.sort(key=lambda x: abs(float(x.strike_price) - spot))
    puts.sort(key=lambda x: abs(float(x.strike_price) - spot))
    
    return calls[:MAX_OPT_SYMBOLS//2] + puts[:MAX_OPT_SYMBOLS//2]

def nearest_delta(target_sign, target_abs, greeks_data, option_meta):
    """Find option closest to target delta"""
    best_symbol, best_diff = None, float('inf')
    
    for symbol, greeks in greeks_data.items():
        delta = float(greeks.get("delta", 0))
        option_type = option_meta[symbol]["type"]
        
        # Check sign compatibility
        if target_sign > 0 and option_type != "C":
            continue
        if target_sign < 0 and option_type != "P":
            continue
        
        diff = abs(abs(delta) - target_abs)
        if diff < best_diff:
            best_symbol, best_diff = symbol, diff
    
    return best_symbol

def analyze_leg_stats(symbol, quotes_data, sample_time):
    """Analyze liquidity stats for one option leg"""
    quote_list = quotes_data.get(symbol, [])
    if not quote_list:
        return None
    
    spreads = [ask - bid for bid, ask in quote_list if ask >= bid > 0]
    mids = [(ask + bid) / 2 for bid, ask in quote_list if ask >= bid > 0]
    
    if not spreads or not mids:
        return None
    
    spread_med = med(spreads)
    mid_med = med(mids)
    
    # Inside ratio (spreads <= reasonable threshold)
    tight_threshold = min(0.20, 0.40 * max(mid_med, 1e-9))
    inside_ratio = sum(1 for s in spreads if s <= tight_threshold) / len(spreads)
    
    ticks_pm = 60 * len(quote_list) / max(sample_time, 1)
    nbbo_age_ms = 1000 * (sample_time / max(len(quote_list), 1))
    
    return {
        "spread_med": spread_med,
        "mid_med": mid_med,
        "inside_ratio": inside_ratio,
        "ticks_per_min": ticks_pm,
        "nbbo_age_ms": nbbo_age_ms,
        "n_quotes": len(quote_list)
    }

async def analyze_ticker_liquidity(ticker_data, mode, verbose=True):
    """Analyze liquidity for one ticker"""
    ticker = ticker_data["ticker"]
    spot = ticker_data["spot"]
    exp_iso = ticker_data["target_expiry"]
    ivr = ticker_data.get("ivr", 0)
    
    if verbose:
        print(f"  🔍 {ticker}: Analyzing delta-30 liquidity...")
    
    sess = Session(USERNAME, PASSWORD)
    
    try:
        async with DXLinkStreamer(sess) as streamer:
            # Get options chain
            chain = get_option_chain(sess, ticker)
            if not chain:
                return {"ticker": ticker, "status": "no_chain"}
            
            # Find target expiry
            target_exp = None
            for exp_date in chain.keys():
                if exp_date.isoformat() == exp_iso:
                    target_exp = exp_date
                    break
            
            if not target_exp:
                return {"ticker": ticker, "status": "no_expiry"}
            
            # Select options subset
            options = choose_options_subset(chain[target_exp], spot)
            if not options:
                return {"ticker": ticker, "status": "no_options"}
            
            symbols = [opt.streamer_symbol for opt in options]
            option_meta = {
                opt.streamer_symbol: {
                    "strike": float(opt.strike_price),
                    "type": opt.option_type.value
                }
                for opt in options
            }
            
            if verbose:
                print(f"    📡 Subscribing to {len(symbols)} options...")
            
            # Subscribe to data feeds
            await streamer.subscribe(Quote, symbols)
            await asyncio.sleep(0.5)
            await streamer.subscribe(Greeks, symbols)
            await asyncio.sleep(0.5)
            await streamer.subscribe(Summary, symbols)
            await asyncio.sleep(0.5)
            
            # Collect data
            quotes = defaultdict(list)
            greeks = {}
            summary = {}
            
            start_time = asyncio.get_event_loop().time()
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= SAMPLE_SEC:
                    break
                
                # Collect quotes
                try:
                    q = await asyncio.wait_for(streamer.get_event(Quote), timeout=0.3)
                    if q and q.event_symbol in option_meta:
                        bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
                        if bid > 0 and ask > 0 and ask >= bid:
                            quotes[q.event_symbol].append((bid, ask))
                except asyncio.TimeoutError:
                    pass
                
                # Collect Greeks
                try:
                    g = await asyncio.wait_for(streamer.get_event(Greeks), timeout=0.3)
                    if g and g.event_symbol in option_meta:
                        greeks[g.event_symbol] = {
                            "delta": float(g.delta or 0),
                            "iv": float(g.volatility or 0)
                        }
                except asyncio.TimeoutError:
                    pass
                
                # Collect Summary
                try:
                    s = await asyncio.wait_for(streamer.get_event(Summary), timeout=0.3)
                    if s and s.event_symbol in option_meta:
                        summary[s.event_symbol] = {"oi": int(s.open_interest or 0)}
                except asyncio.TimeoutError:
                    pass
            
            # Cleanup
            await streamer.unsubscribe(Quote, symbols)
            await streamer.unsubscribe(Greeks, symbols)
            await streamer.unsubscribe(Summary, symbols)
            
            if verbose:
                print(f"    📊 Collected: {len(quotes)} quotes, {len(greeks)} greeks, {len(summary)} summaries")
            
            # Find delta-30 options
            call30 = nearest_delta(+1, 0.30, greeks, option_meta)
            put30 = nearest_delta(-1, 0.30, greeks, option_meta)
            
            if not call30 or not put30:
                return {"ticker": ticker, "status": "no_delta30"}
            
            # Analyze legs
            call_stats = analyze_leg_stats(call30, quotes, elapsed)
            put_stats = analyze_leg_stats(put30, quotes, elapsed)
            
            if not call_stats or not put_stats:
                return {"ticker": ticker, "status": "insufficient_data"}
            
            # Calculate combined metrics
            spread_med_delta30 = max(call_stats["spread_med"], put_stats["spread_med"])
            mid_med_delta30 = med([call_stats["mid_med"], put_stats["mid_med"]])
            inside_ratio = (call_stats["inside_ratio"] + put_stats["inside_ratio"]) / 2
            ticks_pm = (call_stats["ticks_per_min"] + put_stats["ticks_per_min"]) / 2
            nbbo_age_ms = med([call_stats["nbbo_age_ms"], put_stats["nbbo_age_ms"]])
            oi_min = min(
                summary.get(call30, {}).get("oi", 0),
                summary.get(put30, {}).get("oi", 0)
            )
            
            # Create metrics dict
            metrics = {
                "spread_med_delta30": round(spread_med_delta30, 4),
                "mid_med_delta30": round(mid_med_delta30, 4),
                "inside_ratio": round(inside_ratio, 3),
                "ticks_per_min": round(ticks_pm, 2),
                "nbbo_age_ms": round(nbbo_age_ms, 0),
                "oi_min": int(oi_min)
            }
            
            # Calculate liquidity score
            liquidity_score = calculate_liquidity_score(metrics, ivr)
            
            if verbose:
                print(f"    🏆 Score: {liquidity_score:.1f} | Spread: ${spread_med_delta30:.3f} | TPM: {ticks_pm:.1f}")
            
            return {
                "ticker": ticker,
                "status": "analyzed",
                "liquidity_score": liquidity_score,
                "metrics": metrics,
                "delta30_symbols": {"call": call30, "put": put30},
                "ivr": ivr,
                "spot": spot
            }
            
    except Exception as e:
        if verbose:
            print(f"    ❌ Error: {str(e)[:100]}")
        return {"ticker": ticker, "status": f"error: {str(e)[:100]}"}

async def create_sector_baskets(mode, verbose=True):
    """Create trading baskets by selecting best ticker from each sector"""
    if verbose:
        print(f"🏆 Creating {mode.upper()} Trading Basket")
        print("=" * 60)
    
    # Load ATM IV data
    try:
        with open(f"atm_iv_{mode}.json", "r") as f:
            iv_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ atm_iv_{mode}.json not found. Run atm_iv.py first.")
        return None
    
    # Filter successful IV calculations
    valid_tickers = [r for r in iv_data["results"] if r["status"] == "ok"]
    
    if not valid_tickers:
        print(f"❌ No valid tickers found for {mode}")
        return None
    
    if verbose:
        print(f"📋 Analyzing {len(valid_tickers)} tickers with valid IV data")
    
    # Get sector mapping
    sectors = get_sectors(mode)
    ticker_to_sector = {}
    for sector_name, sector_data in sectors.items():
        for ticker in sector_data["tickers"]:
            ticker_to_sector[ticker] = sector_name
    
    # Analyze liquidity for each ticker
    liquidity_results = []
    for i, ticker_data in enumerate(valid_tickers, 1):
        if verbose:
            print(f"\n[{i}/{len(valid_tickers)}] Processing {ticker_data['ticker']}...")
        
        result = await analyze_ticker_liquidity(ticker_data, mode, verbose)
        
        # Add sector information
        result["sector"] = ticker_to_sector.get(ticker_data["ticker"], "Unknown")
        
        liquidity_results.append(result)
        await asyncio.sleep(0.1)  # Brief pause
    
    # Group by sector and select best from each
    sector_results = defaultdict(list)
    for result in liquidity_results:
        if result["status"] == "analyzed":
            sector_results[result["sector"]].append(result)
    
    # Create final basket (1 ticker per sector)
    final_basket = {}
    for sector, tickers in sector_results.items():
        if tickers:
            # Sort by liquidity score, pick best
            best_ticker = max(tickers, key=lambda x: x["liquidity_score"])
            final_basket[sector] = {
                "ticker": best_ticker["ticker"],
                "liquidity_score": best_ticker["liquidity_score"],
                "ivr": best_ticker["ivr"],
                "metrics": best_ticker["metrics"]
            }
    
    # Create output
    output = {
        "mode": mode,
        "analysis_stats": {
            "total_analyzed": len(liquidity_results),
            "successful": len([r for r in liquidity_results if r["status"] == "analyzed"]),
            "sectors_covered": len(final_basket),
            "avg_liquidity_score": sum(data["liquidity_score"] for data in final_basket.values()) / len(final_basket) if final_basket else 0
        },
        "all_results": liquidity_results,
        "sector_basket": final_basket
    }
    
    # Save results
    filename = f"liquidity_basket_{mode}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Basket Results:")
        print(f"  ✅ Analyzed: {output['analysis_stats']['successful']}/{output['analysis_stats']['total_analyzed']}")
        print(f"  🎯 Final basket: {len(final_basket)}/9 sectors")
        print(f"  📁 Saved: {filename}")
        
        if final_basket:
            # Show basket sorted by score
            basket_sorted = sorted(final_basket.items(), key=lambda x: x[1]["liquidity_score"], reverse=True)
            print(f"\n🏆 {mode.upper()} TRADING BASKET:")
            for sector, data in basket_sorted:
                score = data["liquidity_score"]
                ivr = data["ivr"]
                print(f"    {data['ticker']:6} ({sector[:20]}): Score {score:.1f}, IVR {ivr:.1f}%")
    
    return output

def main():
    """Main function for standalone execution"""
    print("🚀 Liquidity Analysis & Basket Creation")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(create_sector_baskets(mode))
        print()

if __name__ == "__main__":
    main()
```
**Run:** `python3 liquidity.py`
