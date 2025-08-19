**Create:** `touch atm_iv.py`

**Query:** `open -e atm_iv.py`

```bash
# atm_iv.py - ATM Implied Volatility Calculation
"""
Computes 30-45 DTE ATM implied volatility and IV rank for each ticker.
Uses live Greeks data from TastyTrade.
"""
import asyncio
import json
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

# Target DTE range
WIN_MIN, WIN_MAX = 30, 45

# IV rank calculation (heuristic ranges by volatility profile)
HIGH_VOL_TICKERS = {"TSLA", "NVDA", "AMD", "ROKU", "SNAP", "GME", "AMC", "RBLX", "PLTR"}
MED_VOL_TICKERS = {"AAPL", "MSFT", "AMZN", "META", "GOOGL", "GOOG", "NFLX", "QQQ", "SPY"}

def pick_target_expiry(chain):
    """Pick best expiry in 30-45 DTE range"""
    today = datetime.now(timezone.utc).date()
    target_dte = (WIN_MIN + WIN_MAX) // 2  # Aim for ~37 DTE
    
    best_exp, best_diff = None, float('inf')
    
    for exp_date in chain.keys():
        dte = (exp_date - today).days
        if WIN_MIN <= dte <= WIN_MAX:
            diff = abs(dte - target_dte)
            if diff < best_diff:
                best_exp, best_diff = exp_date, diff
    
    if best_exp:
        dte = (best_exp - today).days
        return best_exp, dte
    return None, None

def calculate_iv_rank(ticker, iv):
    """Calculate heuristic IV rank based on ticker profile"""
    if not iv or iv <= 0:
        return 0.0, "no_iv"
    
    # Assign volatility profile
    if ticker in HIGH_VOL_TICKERS:
        low, high, profile = 0.40, 1.20, "high_vol"
    elif ticker in MED_VOL_TICKERS:
        low, high, profile = 0.20, 0.60, "med_vol"
    else:
        low, high, profile = 0.15, 0.50, "default"
    
    # Linear interpolation
    if iv <= low:
        return 0.0, profile
    elif iv >= high:
        return 100.0, profile
    else:
        ivr = 100 * (iv - low) / (high - low)
        return round(ivr, 1), profile

async def compute_atm_iv(ticker, spot_price, mode, verbose=True):
    """Compute ATM IV for a single ticker"""
    sess = Session(USERNAME, PASSWORD)
    
    try:
        # Get options chain
        chain = get_option_chain(sess, ticker)
        if not chain:
            return {"ticker": ticker, "status": "no_chain"}
        
        # Pick target expiry
        exp_date, dte = pick_target_expiry(chain)
        if not exp_date:
            return {"ticker": ticker, "status": "no_target_expiry"}
        
        # Find ATM option (closest strike to spot)
        options = chain[exp_date]
        atm_option = min(options, key=lambda opt: abs(float(opt.strike_price) - spot_price))
        atm_symbol = atm_option.streamer_symbol
        
        if verbose:
            print(f"  🎯 {ticker}: ATM {atm_symbol} (K=${atm_option.strike_price}, {dte}DTE)")
        
        # Get IV from live Greeks
        async with DXLinkStreamer(sess) as streamer:
            await streamer.subscribe(Greeks, [atm_symbol])
            
            iv = None
            start_time = asyncio.get_event_loop().time()
            
            # Wait up to 5 seconds for Greeks data
            while asyncio.get_event_loop().time() - start_time < 5.0:
                try:
                    greeks = await asyncio.wait_for(streamer.get_event(Greeks), timeout=1.0)
                    if greeks and greeks.event_symbol == atm_symbol:
                        iv = float(greeks.volatility or 0)
                        if iv > 0:
                            break
                except asyncio.TimeoutError:
                    continue
            
            await streamer.unsubscribe(Greeks, [atm_symbol])
        
        if not iv or iv <= 0:
            return {"ticker": ticker, "status": "no_iv_data"}
        
        # Calculate IV rank
        ivr, ivr_method = calculate_iv_rank(ticker, iv)
        
        if verbose:
            print(f"    📊 IV: {iv:.3f} | IVR: {ivr:.1f}% ({ivr_method})")
        
        return {
            "ticker": ticker,
            "status": "ok",
            "spot": spot_price,
            "target_expiry": exp_date.isoformat(),
            "dte": dte,
            "atm_symbol": atm_symbol,
            "atm_strike": float(atm_option.strike_price),
            "atm_iv": round(iv, 4),
            "ivr": ivr,
            "ivr_method": ivr_method,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {"ticker": ticker, "status": f"error: {str(e)[:100]}"}

async def process_atm_iv_batch(mode, verbose=True):
    """Process ATM IV for all tickers in a mode"""
    if verbose:
        print(f"📈 Computing ATM IV - {mode.upper()}")
        print("=" * 60)
    
    # Load quotes from previous step
    try:
        with open(f"spot_quotes_{mode}.json", "r") as f:
            quotes_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ spot_quotes_{mode}.json not found. Run spot.py first.")
        return None
    
    quotes = quotes_data["quotes"]
    tickers = list(quotes.keys())
    
    if verbose:
        print(f"📋 Processing {len(tickers)} tickers with valid quotes")
    
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        if verbose:
            print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
        
        spot_price = quotes[ticker]["mid"]
        result = await compute_atm_iv(ticker, spot_price, mode, verbose)
        results.append(result)
        
        # Brief pause between tickers
        await asyncio.sleep(0.2)
    
    # Summary
    successful = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] != "ok"]
    
    output = {
        "mode": mode,
        "processing_stats": {
            "total_tickers": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0
        },
        "results": results,
        "high_ivr_tickers": [r for r in successful if r["ivr"] >= 30]
    }
    
    # Save results
    filename = f"atm_iv_{mode}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} ATM IV Results:")
        print(f"  ✅ Success: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"  🔥 High IVR (≥30%): {len(output['high_ivr_tickers'])}")
        print(f"  📁 Saved: {filename}")
        
        if successful:
            # Show top 3 by IVR
            top_ivr = sorted(successful, key=lambda x: x["ivr"], reverse=True)[:3]
            print(f"  🏆 Top IVR:")
            for r in top_ivr:
                print(f"    {r['ticker']}: {r['ivr']:.1f}% (IV: {r['atm_iv']:.3f})")
    
    return output

def main():
    """Main function for standalone execution"""
    print("🚀 ATM IV Calculator")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        asyncio.run(process_atm_iv_batch(mode))
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 atm_iv.py`
