# options_chains.py - Options Contract Discovery for Credit Spreads
"""
FIXED - Discovers options contracts for validated tickers with good liquidity.
Focuses on contracts suitable for credit spreads (7-60 DTE, reasonable strikes).
"""
import json
from datetime import datetime, timezone
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD
from sectors import PerfTimer

def discover_credit_spread_contracts(mode, verbose=True):
    """Discover options contracts suitable for credit spreads"""
    if verbose:
        print(f"🎰 Discovering Credit Spread Contracts - {mode.upper()}")
        print("=" * 70)
    
    # Load ticker rankings from previous step
    try:
        with open(f"ticker_rankings_{mode}.json", "r") as f:
            rankings_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ ticker_rankings_{mode}.json not found. Run ticker_ranker.py first.")
        return None
    
    # Filter to only good liquidity tickers (score >= 40)
    good_tickers = [
        ticker_data for ticker_data in rankings_data["ticker_rankings"]
        if ticker_data["liquidity_score"] >= 40
    ]
    
    if not good_tickers:
        print(f"❌ No tickers with sufficient liquidity (score >= 40)")
        return None
    
    if verbose:
        print(f"📋 Processing {len(good_tickers)} liquid tickers")
        excellent = len([t for t in good_tickers if t["liquidity_score"] >= 80])
        good = len([t for t in good_tickers if 60 <= t["liquidity_score"] < 80])
        fair = len([t for t in good_tickers if 40 <= t["liquidity_score"] < 60])
        print(f"  ⭐ Excellent: {excellent} | ✅ Good: {good} | ⚠️ Fair: {fair}")
    
    sess = Session(USERNAME, PASSWORD)
    all_contracts = {}
    total_contracts = 0
    
    with PerfTimer(f"{mode.upper()} contract discovery"):
        for i, ticker_data in enumerate(good_tickers, 1):
            ticker = ticker_data["ticker"]
            current_price = ticker_data["spot_price"]
            
            if verbose:
                print(f"\n[{i}/{len(good_tickers)}] {ticker} (Score: {ticker_data['liquidity_score']:.1f})")
            
            try:
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
                    'liquidity_score': ticker_data['liquidity_score'],
                    'sector': ticker_data['sector'],
                    'expiration_dates': {},
                    'summary': {
                        'total_contracts': 0,
                        'total_calls': 0,
                        'total_puts': 0,
                        'expiration_count': 0,
                        'suitable_expirations': 0
                    }
                }
                
                # Process expirations suitable for credit spreads
                today = datetime.now(timezone.utc).date()
                suitable_expirations = []
                
                for exp_date in sorted(chain.keys()):
                    dte = (exp_date - today).days
                    # Credit spreads work best with 7-60 DTE
                    if 7 <= dte <= 60:
                        suitable_expirations.append((exp_date, dte))
                
                # Limit to first 8 expirations for performance
                suitable_expirations = suitable_expirations[:8]
                
                for exp_date, dte in suitable_expirations:
                    options = chain[exp_date]
                    exp_str = exp_date.isoformat()
                    
                    contracts = []
                    calls = puts = 0
                    
                    # Focus on strikes suitable for credit spreads
                    # For credit spreads, we want strikes from 70% to 130% of current price
                    strike_range = (current_price * 0.70, current_price * 1.30)
                    
                    for option in options:
                        strike = float(option.strike_price)
                        
                        if strike_range[0] <= strike <= strike_range[1]:
                            # Calculate distance from current price
                            distance_pct = abs(strike - current_price) / current_price * 100
                            
                            contract_info = {
                                'symbol': option.symbol,
                                'streamer_symbol': option.streamer_symbol,
                                'strike': strike,
                                'option_type': option.option_type.value,  # 'C' or 'P'
                                'dte': dte,
                                'distance_from_current': round(distance_pct, 1),
                                'moneyness': 'ITM' if (option.option_type.value == 'C' and strike < current_price) or (option.option_type.value == 'P' and strike > current_price) else 'OTM'
                            }
                            
                            contracts.append(contract_info)
                            
                            if option.option_type.value == 'C':
                                calls += 1
                            else:
                                puts += 1
                    
                    if contracts:
                        ticker_contracts['expiration_dates'][exp_str] = {
                            'expiration_date': exp_str,
                            'dte': dte,
                            'contracts': contracts,
                            'calls': calls,
                            'puts': puts,
                            'total': len(contracts),
                            'otm_calls': len([c for c in contracts if c['option_type'] == 'C' and c['moneyness'] == 'OTM']),
                            'otm_puts': len([c for c in contracts if c['option_type'] == 'P' and c['moneyness'] == 'OTM'])
                        }
                        
                        ticker_contracts['summary']['total_contracts'] += len(contracts)
                        ticker_contracts['summary']['total_calls'] += calls
                        ticker_contracts['summary']['total_puts'] += puts
                        ticker_contracts['summary']['suitable_expirations'] += 1
                        
                        if verbose:
                            otm_calls = ticker_contracts['expiration_dates'][exp_str]['otm_calls']
                            otm_puts = ticker_contracts['expiration_dates'][exp_str]['otm_puts']
                            print(f"    📋 {exp_str} ({dte}DTE): {calls}C + {puts}P = {len(contracts)} | OTM: {otm_calls}C + {otm_puts}P")
                
                ticker_contracts['summary']['expiration_count'] = len(ticker_contracts['expiration_dates'])
                total_contracts += ticker_contracts['summary']['total_contracts']
                
                if ticker_contracts['summary']['total_contracts'] > 0:
                    all_contracts[ticker] = ticker_contracts
                    
                    if verbose:
                        total = ticker_contracts['summary']['total_contracts']
                        suitable = ticker_contracts['summary']['suitable_expirations']
                        print(f"  🎯 Total for {ticker}: {total} contracts across {suitable} expirations")
                else:
                    if verbose:
                        print(f"  ⚠️ No suitable contracts found for {ticker}")
            
            except Exception as e:
                if verbose:
                    print(f"  ❌ Error processing {ticker}: {str(e)[:100]}")
                continue
    
    # Create comprehensive output
    result = {
        'mode': mode,
        'discovery_stats': {
            'input_tickers': len(good_tickers),
            'tickers_with_contracts': len(all_contracts),
            'total_contracts_found': total_contracts,
            'success_rate': round(len(all_contracts) / len(good_tickers) * 100, 1) if good_tickers else 0,
            'avg_contracts_per_ticker': round(total_contracts / len(all_contracts), 1) if all_contracts else 0,
            'liquidity_filter_applied': True,
            'min_liquidity_score': 40
        },
        'contracts_by_ticker': all_contracts,
        'credit_spread_analysis': {
            'tickers_ready_for_spreads': len(all_contracts),
            'total_potential_spread_legs': total_contracts,
            'avg_expirations_per_ticker': round(sum(data['summary']['suitable_expirations'] for data in all_contracts.values()) / len(all_contracts), 1) if all_contracts else 0
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    # Save results
    filename = f"options_contracts_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Options Discovery Results:")
        print(f"  ✅ Tickers with contracts: {len(all_contracts)}/{len(good_tickers)}")
        print(f"  🎰 Total contracts: {total_contracts:,}")
        print(f"  📈 Avg per ticker: {result['discovery_stats']['avg_contracts_per_ticker']:.1f}")
        print(f"  ⏱️ Avg expirations: {result['credit_spread_analysis']['avg_expirations_per_ticker']:.1f}")
        print(f"  📁 Saved: {filename}")
        
        if all_contracts:
            # Show top tickers by contract count
            top_tickers = sorted(all_contracts.items(), 
                               key=lambda x: x[1]['summary']['total_contracts'], 
                               reverse=True)[:5]
            print(f"  🏆 Most contracts:")
            for ticker, data in top_tickers:
                count = data['summary']['total_contracts']
                score = data['liquidity_score']
                exps = data['summary']['suitable_expirations']
                print(f"    {ticker}: {count:,} contracts, {exps} expirations (Score: {score:.1f})")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Credit Spread Contract Discovery")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        result = discover_credit_spread_contracts(mode)
        if result:
            contracts = result['discovery_stats']['total_contracts_found']
            tickers = result['discovery_stats']['tickers_with_contracts']
            print(f"🎯 {mode.upper()}: {tickers} tickers ready with {contracts:,} contracts")
        print()

if __name__ == "__main__":
    main()
