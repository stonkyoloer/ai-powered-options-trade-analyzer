# build_universe.py - Optimized Universe Builder
"""
KEEP - optimize for 20min runtime target.
Validates options chains with early exit at 95% success.
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from tastytrade.instruments import get_option_chain
from get_session import get_or_create_session
from config import USERNAME, PASSWORD
from sectors import get_sectors, alias_candidates, PORTFOLIO_MODE, PerfTimer

BUILD_MODES = ["gpt", "grok", "claude"]

def validate_chain_fast(sess, sym, timeout=3):
    """Fast chain validation with timeout"""
    start_time = time.time()
    
    for alias in alias_candidates(sym):
        if time.time() - start_time > timeout:
            break
            
        try:
            chain = get_option_chain(sess, alias)
            if chain and len(chain) > 0:
                print(f"  ✅ {sym} -> {alias}")
                return alias
        except Exception as e:
            print(f"  ❌ {sym} -> {alias} ({str(e)[:30]})")
            continue
    
    print(f"  ⚠️ {sym} -> NO CHAIN")
    return None

def build_universe_optimized(sess, mode):
    """Build universe with optimized validation"""
    print(f"\n🔨 Building {mode.upper()} universe...")
    
    with PerfTimer(f"{mode.upper()} universe build"):
        sectors = get_sectors(mode)
        validated_tickers = []
        failed_tickers = []
        
        # Get all tickers
        all_tickers = []
        ticker_to_sector = {}
        for sector, meta in sectors.items():
            for ticker in meta["tickers"]:
                all_tickers.append(ticker)
                ticker_to_sector[ticker] = sector
        
        print(f"📋 Validating {len(all_tickers)} tickers...")
        
        # Process with early exit
        for i, ticker in enumerate(all_tickers, 1):
            print(f"[{i}/{len(all_tickers)}] {ticker}:")
            
            validated_alias = validate_chain_fast(sess, ticker)
            
            record = {
                "ticker": validated_alias or ticker,
                "requested": ticker,
                "sector": ticker_to_sector[ticker],
                "status": "ok" if validated_alias else "no_chain"
            }
            
            if validated_alias:
                validated_tickers.append(record)
            else:
                failed_tickers.append(record)
            
            # Early exit at 95% if we have enough
            success_rate = len(validated_tickers) / i
            if i >= 20 and success_rate >= 0.95:
                print(f"🚀 Early exit at 95% success rate ({i} processed)")
                break
    
    all_results = validated_tickers + failed_tickers
    
    print(f"📊 Results: {len(validated_tickers)} OK, {len(failed_tickers)} failed")
    if failed_tickers:
        failed_symbols = [f["requested"] for f in failed_tickers]
        print(f"❌ Failed: {failed_symbols}")
    
    return all_results

def main(two_fa_code):
    """Main universe builder"""
    start_time = time.time()
    print("🚀 Optimized Universe Builder")
    print(f"📅 Target: 20min runtime | Mode: {PORTFOLIO_MODE}")
    
    # Reuse a cached session when possible; falls back to 2FA once
    sess = get_or_create_session(two_fa_code)
    
    for mode in BUILD_MODES:
        results = build_universe_optimized(sess, mode)
        
        # Save results
        filename = f"universe_{mode}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Saved: {filename}")
    
    # Set active universe
    active_file = f"universe_{PORTFOLIO_MODE}.json"
    if Path(active_file).exists():
        with open(active_file, "r") as f:
            active_data = f.read()
        with open("universe_active.json", "w") as f:
            f.write(active_data)
        print(f"🔗 Active: universe_active.json -> {PORTFOLIO_MODE}")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Total time: {total_time:.1f}s")
    print(f"🎯 Next: python spot.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("two_fa_code", help="2FA code for tastytrade")
    args = parser.parse_args()
    main(args.two_fa_code)
