**Create:** `touch universe.py`

**Query:** `open -e universe.py`

```bash
# build_universe.py - Options Chain Validation
"""
Validates which tickers actually have tradeable options chains.
Only keeps tickers with real options data.
"""
import json
import collections
from pathlib import Path
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD
from sectors import get_sectors

def validate_universe(mode, verbose=True):
    """Validate options chains for a specific universe (gpt/grok)"""
    if verbose:
        print(f"🔨 Validating {mode.upper()} Universe Options Chains")
        print("=" * 60)
    
    # Get tickers for this mode
    sectors = get_sectors(mode)
    sess = Session(USERNAME, PASSWORD)
    
    valid_tickers = []
    failed_tickers = []
    
    for sector_name, sector_data in sectors.items():
        if verbose:
            print(f"\n📂 {sector_name}:")
        
        for ticker in sector_data["tickers"]:
            try:
                chain = get_option_chain(sess, ticker)
                if chain and len(chain) > 0:
                    valid_tickers.append({
                        "ticker": ticker,
                        "sector": sector_name,
                        "status": "ok",
                        "expiries": len(chain)
                    })
                    if verbose:
                        print(f"  ✅ {ticker}: {len(chain)} expiries")
                else:
                    failed_tickers.append({
                        "ticker": ticker,
                        "sector": sector_name,
                        "status": "no_chain"
                    })
                    if verbose:
                        print(f"  ❌ {ticker}: No options chain")
                        
            except Exception as e:
                failed_tickers.append({
                    "ticker": ticker,
                    "sector": sector_name,
                    "status": f"error: {str(e)[:50]}"
                })
                if verbose:
                    print(f"  ❌ {ticker}: {e}")
    
    result = {
        "mode": mode,
        "valid_tickers": valid_tickers,
        "failed_tickers": failed_tickers,
        "summary": {
            "total_attempted": len(valid_tickers) + len(failed_tickers),
            "valid": len(valid_tickers),
            "failed": len(failed_tickers),
            "success_rate": len(valid_tickers) / (len(valid_tickers) + len(failed_tickers)) * 100
        }
    }
    
    # Save results
    filename = f"universe_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Results:")
        print(f"  ✅ Valid: {len(valid_tickers)}/{len(valid_tickers) + len(failed_tickers)}")
        print(f"  📁 Saved: {filename}")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Options Universe Validator")
    print("=" * 50)
    
    # Validate both universes
    for mode in ["gpt", "grok"]:
        validate_universe(mode, verbose=True)
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 universe.py`
