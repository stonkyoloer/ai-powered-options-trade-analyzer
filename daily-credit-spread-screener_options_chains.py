**Create:** `touch options_chains.py`

**Query:** `open -e options_chains.py`

```bash
# options_chains.py - Options Contract Discovery
"""
Discovers all available options contracts for credit spread analysis.
Focuses on contracts with 7-45 DTE for optimal credit spread opportunities.
"""
import json
from datetime import datetime, timezone
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

def discover_options_contracts(mode, verbose=True):
    """Discover options contracts for all tickers in a mode"""
    if verbose:
        print(f"🎰 Discovering Options Contracts - {mode.upper()}")
        print("=" * 60)
    
    # Load stock prices from previous step
    try:
        with open(f"stock_prices_{mode}.json", "r") as f:
            price_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ stock_prices_{mode}.json not found. Run stock_prices.py first.")
        return None
    
    stock_prices = price_data["stock_prices"]
    tickers = list(stock_prices.keys())
    
    if verbose:
        print(f"📋 Processing {len(tickers)} tickers with valid prices")
    
    sess = Session(USERNAME, PASSWORD)
    all_contracts = {}
    total_contracts = 0
    
    for i, ticker in enumerate(tickers, 1):
        if verbose:
            print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
        
        try:
            current_price = stock_prices[ticker]["current_price"]
            
            # Get options chain
            chain = get_option_chain(sess, ticker)
            if not chain:
                if verbose:
                    print(f"  ❌ No options chain found")
                continue
            
            if verbose:
                print(f"  📅 Found {len(chain)} expiration dates")
            
            ticker_contracts = {
                'ticker': ticker,
                'current_price': current_price,
                'expiration_dates': {},
                'summary': {
                    'total_contracts': 0,
                    'total_calls': 0,
                    'total_puts': 0,
                    'expiration_count': 0
                }
            }
            
            # Process each expiration (limit to reasonable timeframe)
            today = datetime.now(timezone.utc).date()
            valid_expirations = []
            
            for exp_date in sorted(chain.keys()):
                dte = (exp_date - today).days
                if 7 <= dte <= 45:  # Focus on near-term expirations for credit spreads
                    valid_expirations.append((exp_date, dte))
            
            # Limit to first 6 expirations to avoid overload
            valid_expirations = valid_expirations[:6]
            
            for exp_date, dte in valid_expirations:
                options = chain[exp_date]
                exp_str = exp_date.isoformat()
                
                contracts = []
                calls = puts = 0
                
                # Process each option contract
                for option in options:
                    strike = float(option.strike_price)
                    
                    # Focus on strikes within reasonable range of current price
                    if 0.7 * current_price <= strike <= 1.3 * current_price:
                        contract_info = {
                            'symbol': option.symbol,
                            'streamer_symbol': option.streamer_symbol,
                            'strike': strike,
                            'option_type': option.option_type.value,  # 'C' or 'P'
                            'dte': dte
                        }
                        
                        contracts.append(contract_info)
                        
                        if option.option_type.value == 'C':
                            calls += 1
                        else:
                            puts += 1
                
                if contracts:  # Only save if we have contracts
                    ticker_contracts['expiration_dates'][exp_str] = {
                        'expiration_date': exp_str,
                        'dte': dte,
                        'contracts': contracts,
                        'calls': calls,
                        'puts': puts,
                        'total': len(contracts)
                    }
                    
                    ticker_contracts['summary']['total_contracts'] += len(contracts)
                    ticker_contracts['summary']['total_calls'] += calls
                    ticker_contracts['summary']['total_puts'] += puts
                    
                    if verbose:
                        print(f"    📋 {exp_str} ({dte}DTE): {calls}C + {puts}P = {len(contracts)} contracts")
            
            ticker_contracts['summary']['expiration_count'] = len(ticker_contracts['expiration_dates'])
            total_contracts += ticker_contracts['summary']['total_contracts']
            
            if ticker_contracts['summary']['total_contracts'] > 0:
                all_contracts[ticker] = ticker_contracts
                
                if verbose:
                    print(f"  🎯 Total for {ticker}: {ticker_contracts['summary']['total_contracts']} contracts")
            else:
                if verbose:
                    print(f"  ⚠️ No suitable contracts found for {ticker}")
        
        except Exception as e:
            if verbose:
                print(f"  ❌ Error processing {ticker}: {str(e)[:100]}")
            continue
    
    # Create output
    result = {
        'mode': mode,
        'discovery_stats': {
            'tickers_processed': len(tickers),
            'tickers_with_contracts': len(all_contracts),
            'total_contracts_found': total_contracts,
            'success_rate': len(all_contracts) / len(tickers) * 100 if tickers else 0
        },
        'contracts_by_ticker': all_contracts,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"options_contracts_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Options Discovery Results:")
        print(f"  ✅ Tickers with contracts: {len(all_contracts)}/{len(tickers)}")
        print(f"  🎰 Total contracts: {total_contracts:,}")
        print(f"  📁 Saved: {filename}")
        
        if all_contracts:
            # Show top tickers by contract count
            top_tickers = sorted(all_contracts.items(), 
                               key=lambda x: x[1]['summary']['total_contracts'], 
                               reverse=True)[:3]
            print(f"  🏆 Most contracts:")
            for ticker, data in top_tickers:
                count = data['summary']['total_contracts']
                print(f"    {ticker}: {count:,} contracts")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Options Contract Discovery")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        discover_options_contracts(mode)
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 options_chains.py`
