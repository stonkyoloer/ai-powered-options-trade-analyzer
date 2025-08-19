**Create:** `touch find_tendies.py`

**Query:** `open -e find_tendies.py`

```bash
# enhanced_find_tendies.py - STEP 7: Both Call and Put Credit Spreads
import json
import numpy as np
from datetime import datetime
from scipy.stats import norm

class EliteCreditSpreadScanner:
    """Advanced credit spread scanner for BOTH calls and puts"""
    
    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate
    
    def black_scholes_probability(self, S, K, T, sigma, option_type='call'):
        """Calculate probability of staying OTM for calls or puts"""
        if T <= 0 or sigma <= 0:
            return 0
        
        d2 = (np.log(S / K) + (self.risk_free_rate - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        if option_type == 'call':
            # Probability call stays OTM (stock stays below K)
            return norm.cdf(-d2) * 100
        else:
            # Probability put stays OTM (stock stays above K)  
            return norm.cdf(d2) * 100
    
    def scan_call_spreads(self, liquid_contracts, current_price, company, price_lookup, avg_iv):
        """Scan for bear call credit spreads (calls above current price)"""
        call_spreads = []
        
        # Get calls above current price
        calls_above = []
        for contract in liquid_contracts:
            if (contract['type'] == 'CALL' and 
                contract['strike'] > current_price and
                contract['liquid'] and
                contract['symbol'] in price_lookup):
                calls_above.append(contract)
        
        calls_above.sort(key=lambda x: x['strike'])
        
        # Create call spreads
        for i in range(len(calls_above) - 1):
            short_call = calls_above[i]
            long_call = calls_above[i + 1]
            
            spread = self.analyze_credit_spread(
                short_call, long_call, current_price, company, 
                price_lookup, avg_iv, 'BEAR_CALL'
            )
            if spread:
                call_spreads.append(spread)
        
        return call_spreads
    
    def scan_put_spreads(self, liquid_contracts, current_price, company, price_lookup, avg_iv):
        """Scan for bull put credit spreads (puts below current price)"""
        put_spreads = []
        
        # Get puts below current price
        puts_below = []
        for contract in liquid_contracts:
            if (contract['type'] == 'PUT' and 
                contract['strike'] < current_price and
                contract['liquid'] and
                contract['symbol'] in price_lookup):
                puts_below.append(contract)
        
        puts_below.sort(key=lambda x: x['strike'], reverse=True)  # Highest to lowest
        
        # Create put spreads
        for i in range(len(puts_below) - 1):
            short_put = puts_below[i]      # Higher strike (short)
            long_put = puts_below[i + 1]   # Lower strike (long)
            
            spread = self.analyze_credit_spread(
                short_put, long_put, current_price, company, 
                price_lookup, avg_iv, 'BULL_PUT'
            )
            if spread:
                put_spreads.append(spread)
        
        return put_spreads
    
    def analyze_credit_spread(self, short_option, long_option, current_price, 
                            company, price_lookup, avg_iv, spread_type):
        """Analyze a credit spread (works for both calls and puts)"""
        
        strike_width = abs(long_option['strike'] - short_option['strike'])
        if strike_width > 10:
            return None
        
        short_symbol = short_option['symbol']
        long_symbol = long_option['symbol']
        
        # Get price data
        short_price = price_lookup[short_symbol]
        long_price = price_lookup[long_symbol]
        
        # Calculate credit (what we collect)
        credit = short_price['what_buyers_pay'] - long_price['what_sellers_want']
        if credit <= 0:
            return None
        
        max_risk = strike_width - credit
        roi = (credit / max_risk * 100) if max_risk > 0 else 0
        
        # Skip low ROI
        if roi < 10:
            return None
        
        # Get IV for probability calculation
        short_iv = short_option.get('current_iv', avg_iv)
        time_to_exp = short_option['days_to_exp'] / 365
        
        # Calculate probability based on spread type
        if spread_type == 'BEAR_CALL':
            # For bear call: want stock to stay BELOW short strike
            prob_profit = self.black_scholes_probability(
                current_price, short_option['strike'], time_to_exp, short_iv, 'call'
            )
            distance_from_money = ((short_option['strike'] - current_price) / current_price) * 100
        else:  # BULL_PUT
            # For bull put: want stock to stay ABOVE short strike  
            prob_profit = self.black_scholes_probability(
                current_price, short_option['strike'], time_to_exp, short_iv, 'put'
            )
            distance_from_money = ((current_price - short_option['strike']) / current_price) * 100
        
        # Skip low probability
        if prob_profit < 65:
            return None
        
        # Check minimum liquidity
        min_oi = min(short_option['open_interest'], long_option['open_interest'])
        if min_oi < 500:
            return None
        
        return {
            'company': company,
            'spread_type': spread_type,
            'short_strike': short_option['strike'],
            'long_strike': long_option['strike'],
            'strike_width': strike_width,
            'days_to_expiration': short_option['days_to_exp'],
            'credit': credit,
            'max_risk': max_risk,
            'roi_percent': roi,
            'probability_of_profit': prob_profit,
            'current_stock_price': current_price,
            'distance_from_money': distance_from_money,
            'short_iv': short_iv,
            'min_open_interest': min_oi,
            'short_symbol': short_symbol,
            'long_symbol': long_symbol,
            'strategy_explanation': self.get_strategy_explanation(spread_type, short_option['strike'], long_option['strike'])
        }
    
    def get_strategy_explanation(self, spread_type, short_strike, long_strike):
        """Explain the strategy"""
        if spread_type == 'BEAR_CALL':
            return f"Sell ${short_strike} call, buy ${long_strike} call. Profit if stock stays below ${short_strike}"
        else:
            return f"Sell ${short_strike} put, buy ${long_strike} put. Profit if stock stays above ${short_strike}"

def scan_all_credit_spreads():
    print("🏆 STEP 7: Complete Credit Spread Scanner")
    print("=" * 70)
    print("🎯 Scanning BOTH Call and Put Credit Spreads...")
    print("📈 Bear Call Spreads: Profit when stock doesn't go UP")
    print("📉 Bull Put Spreads: Profit when stock doesn't go DOWN")
    
    # Load all data
    with open('step1_stock_prices.json', 'r') as f:
        stock_data = json.load(f)
    
    with open('step2_options_contracts.json', 'r') as f:
        options_data = json.load(f)
    
    with open('step3_iv_data.json', 'r') as f:
        iv_data = json.load(f)
    
    with open('step4_market_prices.json', 'r') as f:
        price_data = json.load(f)
    
    with open('step6_advanced_iv_liquidity.json', 'r') as f:
        iv_liquidity_data = json.load(f)
    
    scanner = EliteCreditSpreadScanner()
    
    # Create price lookup
    price_lookup = {}
    for company, prices_list in price_data['prices_by_company'].items():
        for price in prices_list:
            price_lookup[price['contract_name']] = price
    
    all_spreads = []
    call_spreads_total = 0
    put_spreads_total = 0
    
    # Scan each company
    for company, company_options in options_data['options_by_company'].items():
        current_price = company_options['current_stock_price']
        company_iv_data = iv_liquidity_data['enhanced_options'].get(company, {})
        avg_iv = company_iv_data.get('avg_implied_volatility', 0.3)
        
        print(f"\n🏢 Scanning {company} (Price: ${current_price:.2f}, Avg IV: {avg_iv:.3f})...")
        
        # Skip if IV too low
        if avg_iv < 0.25:
            print(f"   ⚠️ IV too low ({avg_iv:.3f}), skipping...")
            continue
        
        liquid_contracts = company_iv_data.get('top_liquid_contracts', [])
        
        # Scan call credit spreads (bear call spreads)
        call_spreads = scanner.scan_call_spreads(
            liquid_contracts, current_price, company, price_lookup, avg_iv
        )
        call_spreads_total += len(call_spreads)
        
        # Scan put credit spreads (bull put spreads)  
        put_spreads = scanner.scan_put_spreads(
            liquid_contracts, current_price, company, price_lookup, avg_iv
        )
        put_spreads_total += len(put_spreads)
        
        all_spreads.extend(call_spreads)
        all_spreads.extend(put_spreads)
        
        print(f"   📈 Bear Call Spreads: {len(call_spreads)}")
        print(f"   📉 Bull Put Spreads: {len(put_spreads)}")
        print(f"   🎯 Total for {company}: {len(call_spreads) + len(put_spreads)}")
    
    # Sort by ROI * Probability score
    for spread in all_spreads:
        spread['combined_score'] = spread['roi_percent'] * (spread['probability_of_profit'] / 100)
    
    all_spreads.sort(key=lambda x: x['combined_score'], reverse=True)
    
    print(f"\n💎 TOTAL CREDIT SPREADS FOUND: {len(all_spreads)}")
    print(f"📈 Bear Call Spreads: {call_spreads_total}")
    print(f"📉 Bull Put Spreads: {put_spreads_total}")
    print("=" * 70)
    
    # Show top 15 - mixed calls and puts
    print(f"\n🏆 TOP 15 CREDIT SPREADS (Both Types):")
    print("-" * 120)
    
    for i, spread in enumerate(all_spreads[:15]):
        spread_icon = "📈" if spread['spread_type'] == 'BEAR_CALL' else "📉"
        spread_name = "Bear Call" if spread['spread_type'] == 'BEAR_CALL' else "Bull Put"
        
        print(f"{i+1:2}. {spread_icon} {spread['company']:4} {spread_name:9} | "
              f"${spread['short_strike']:.0f}/{spread['long_strike']:.0f} | "
              f"Score: {spread['combined_score']:.1f} | "
              f"PoP: {spread['probability_of_profit']:.1f}% | "
              f"ROI: {spread['roi_percent']:.1f}% | "
              f"Credit: ${spread['credit']:.2f} | "
              f"DTE: {spread['days_to_expiration']}")
        print(f"     📝 {spread['strategy_explanation']}")
    
    # Save results
    result = {
        'step': 7,
        'what_we_did': 'Complete Credit Spread Analysis - Both Calls and Puts',
        'timestamp': datetime.now().isoformat(),
        'total_spreads_found': len(all_spreads),
        'bear_call_spreads': call_spreads_total,
        'bull_put_spreads': put_spreads_total,
        'all_spreads': all_spreads[:100],  # Top 100
        'summary_stats': {
            'avg_roi': np.mean([s['roi_percent'] for s in all_spreads]) if all_spreads else 0,
            'avg_probability': np.mean([s['probability_of_profit'] for s in all_spreads]) if all_spreads else 0,
            'avg_combined_score': np.mean([s['combined_score'] for s in all_spreads]) if all_spreads else 0
        }
    }
    
    filename = 'step7_complete_credit_spreads.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved complete analysis to: {filename}")
    
    # Show strategy breakdown
    if all_spreads:
        best_call = next((s for s in all_spreads if s['spread_type'] == 'BEAR_CALL'), None)
        best_put = next((s for s in all_spreads if s['spread_type'] == 'BULL_PUT'), None)
        
        print(f"\n💎 STRATEGY COMPARISON:")
        if best_call:
            print(f"   📈 Best Bear Call: {best_call['company']} ${best_call['short_strike']:.0f}/{best_call['long_strike']:.0f}")
            print(f"      ROI: {best_call['roi_percent']:.1f}%, PoP: {best_call['probability_of_profit']:.1f}%")
        
        if best_put:
            print(f"   📉 Best Bull Put: {best_put['company']} ${best_put['short_strike']:.0f}/{best_put['long_strike']:.0f}")
            print(f"      ROI: {best_put['roi_percent']:.1f}%, PoP: {best_put['probability_of_profit']:.1f}%")
    
    return result

if __name__ == "__main__":
    scan_all_credit_spreads()
```

**Run:** `python3 find_tendies.py`
