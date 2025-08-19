**Create:** `touch risk_analysis.py`

**Query:** `open -e risk_analysis.py`

```bash
# risk_analysis.py - Greeks-based Risk Analysis
"""
Comprehensive risk analysis using Greeks for all options contracts.
Calculates delta, theta, gamma, vega for risk assessment.
"""
import asyncio
import json
from datetime import datetime, timezone
from collections import defaultdict
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from config import USERNAME, PASSWORD

async def analyze_risk_metrics(mode, verbose=True):
    """Analyze risk using Greeks for all options"""
    if verbose:
        print(f"🧮 Analyzing Risk Metrics - {mode.upper()}")
        print("=" * 60)
    
    # Load market prices from previous step
    try:
        with open(f"market_prices_{mode}.json", "r") as f:
            price_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ market_prices_{mode}.json not found. Run market_prices.py first.")
        return None
    
    # Get symbols that have prices
    symbols_with_prices = list(price_data["market_prices"].keys())
    
    if verbose:
        print(f"🎯 Analyzing risk for {len(symbols_with_prices):,} priced contracts...")
    
    sess = Session(USERNAME, PASSWORD)
    greeks_data = {}
    
    # Process in batches
    batch_size = 500
    total_analyzed = 0
    
    async with DXLinkStreamer(sess) as streamer:
        for batch_start in range(0, len(symbols_with_prices), batch_size):
            batch_end = min(batch_start + batch_size, len(symbols_with_prices))
            batch_symbols = symbols_with_prices[batch_start:batch_end]
            
            if verbose:
                batch_num = batch_start // batch_size + 1
                total_batches = (len(symbols_with_prices) + batch_size - 1) // batch_size
                print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch_symbols)} symbols)")
            
            # Subscribe to Greeks
            await streamer.subscribe(Greeks, batch_symbols)
            
            # Collect Greeks for this batch
            batch_greeks = {}
            start_time = asyncio.get_event_loop().time()
            no_data_timeout = 0
            
            while (asyncio.get_event_loop().time() - start_time) < 30 and no_data_timeout < 8:
                try:
                    greek = await asyncio.wait_for(streamer.get_event(Greeks), timeout=1.5)
                    
                    if greek and greek.event_symbol in batch_symbols:
                        if greek.event_symbol not in batch_greeks:
                            # Get price info
                            price_info = price_data["market_prices"][greek.event_symbol]
                            
                            batch_greeks[greek.event_symbol] = {
                                "symbol": greek.event_symbol,
                                "ticker": price_info["ticker"],
                                "strike": price_info["strike"],
                                "type": price_info["type"],
                                "dte": price_info["dte"],
                                "delta": round(float(greek.delta or 0), 4),
                                "theta": round(float(greek.theta or 0), 4),
                                "gamma": round(float(greek.gamma or 0), 4),
                                "vega": round(float(greek.vega or 0), 4),
                                "rho": round(float(greek.rho or 0), 4),
                                "iv": round(float(greek.volatility or 0), 4),
                                "price": price_info["mid"],
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                            
                            total_analyzed += 1
                            no_data_timeout = 0
                            
                            if verbose and len(batch_greeks) % 50 == 0:
                                print(f"    📊 Progress: {len(batch_greeks)} Greeks analyzed")
                
                except asyncio.TimeoutError:
                    no_data_timeout += 1
                    continue
                except Exception as e:
                    if verbose:
                        print(f"    ⚠️ Greeks error: {e}")
                    continue
            
            # Unsubscribe from batch
            await streamer.unsubscribe(Greeks, batch_symbols)
            
            # Merge batch results
            greeks_data.update(batch_greeks)
            
            if verbose:
                elapsed = asyncio.get_event_loop().time() - start_time
                print(f"    ✅ Batch complete: {len(batch_greeks)} Greeks in {elapsed:.1f}s")
            
            # Brief pause between batches
            await asyncio.sleep(0.5)
    
    # Organize by ticker and calculate risk metrics
    risk_by_ticker = defaultdict(lambda: {
        "contracts": [],
        "summary": {}
    })
    
    for symbol, greek_data in greeks_data.items():
        ticker = greek_data["ticker"]
        risk_by_ticker[ticker]["contracts"].append(greek_data)
    
    # Calculate summary statistics for each ticker
    for ticker, data in risk_by_ticker.items():
        contracts = data["contracts"]
        if contracts:
            # Separate calls and puts
            calls = [c for c in contracts if c["type"] == "C"]
            puts = [c for c in contracts if c["type"] == "P"]
            
            data["summary"] = {
                "total_contracts": len(contracts),
                "calls_analyzed": len(calls),
                "puts_analyzed": len(puts),
                "avg_iv": sum(c["iv"] for c in contracts) / len(contracts) if contracts else 0,
                "avg_call_iv": sum(c["iv"] for c in calls) / len(calls) if calls else 0,
                "avg_put_iv": sum(c["iv"] for c in puts) / len(puts) if puts else 0,
                "max_theta": max((c["theta"] for c in contracts), default=0),
                "min_theta": min((c["theta"] for c in contracts), default=0),
                "high_gamma_contracts": len([c for c in contracts if abs(c["gamma"]) > 0.05]),
                "high_vega_contracts": len([c for c in contracts if abs(c["vega"]) > 0.5])
            }
    
    # Find high-risk and high-opportunity contracts
    all_contracts = []
    for ticker_data in risk_by_ticker.values():
        all_contracts.extend(ticker_data["contracts"])
    
    # Sort by various risk metrics
    high_theta_decay = sorted([c for c in all_contracts if c["theta"] < -0.05], 
                              key=lambda x: x["theta"])[:20]
    high_gamma = sorted([c for c in all_contracts if abs(c["gamma"]) > 0.05], 
                        key=lambda x: abs(x["gamma"]), reverse=True)[:20]
    high_vega = sorted([c for c in all_contracts if abs(c["vega"]) > 0.5], 
                       key=lambda x: abs(x["vega"]), reverse=True)[:20]
    
    # Create output
    result = {
        "mode": mode,
        "analysis_stats": {
            "total_analyzed": len(greeks_data),
            "tickers_analyzed": len(risk_by_ticker),
            "avg_iv": sum(c["iv"] for c in all_contracts) / len(all_contracts) if all_contracts else 0,
            "contracts_with_high_theta": len([c for c in all_contracts if c["theta"] < -0.05]),
            "contracts_with_high_gamma": len([c for c in all_contracts if abs(c["gamma"]) > 0.05]),
            "contracts_with_high_vega": len([c for c in all_contracts if abs(c["vega"]) > 0.5])
        },
        "greeks_data": greeks_data,
        "risk_by_ticker": dict(risk_by_ticker),
        "high_risk_contracts": {
            "high_theta_decay": high_theta_decay,
            "high_gamma": high_gamma,
            "high_vega": high_vega
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"risk_analysis_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Risk Analysis Results:")
        print(f"  ✅ Greeks analyzed: {len(greeks_data):,}/{len(symbols_with_prices):,}")
        print(f"  🏢 Tickers analyzed: {len(risk_by_ticker)}")
        print(f"  📈 Average IV: {result['analysis_stats']['avg_iv']:.3f}")
        print(f"  ⏰ High theta decay: {len(high_theta_decay)}")
        print(f"  🚀 High gamma: {len(high_gamma)}")
        print(f"  📊 High vega: {len(high_vega)}")
        print(f"  📁 Saved: {filename}")
        
        # Show some high-risk examples
        if high_theta_decay:
            print(f"\n  ⚠️ Highest Theta Decay (avoid selling):")
            for c in high_theta_decay[:3]:
                print(f"    {c['ticker']} ${c['strike']:.0f} {c['type']}: θ={c['theta']:.3f}")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Risk Analysis Engine")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(analyze_risk_metrics(mode))
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 risk_analysis.py`
