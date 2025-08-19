**Create:** `touch find_tendies.py`

**Query:** `open -e find_tendies.py`

```bash
# find_tendies.py - Elite Credit Spread Scanner
"""
Advanced credit spread scanner using Black-Scholes probability modeling.
Finds both bear call and bull put credit spreads with optimal risk/reward.
"""
import json
import numpy as np
from datetime import datetime
from scipy.stats import norm
from collections import defaultdict

class CreditSpreadScanner:
    """Elite credit spread scanner with probability modeling"""
    
    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate
        
    def black_scholes_probability_otm(self, S, K, T, sigma, option_type='call'):
        """Calculate probability of staying OTM using Black-Scholes"""
        if T <= 0 or sigma <= 0:
            return 0
        
        d2 = (np.log(S / K) + (self.risk_free_rate - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        if option_type == 'call':
            # Probability call stays OTM (stock stays below strike)
            return norm.cdf(-d2) * 100
        else:
            # Probability put stays OTM (stock stays above strike)
            return norm.cdf(d2) * 100
    
    def calculate_master_score(self, roi, probability, iv_rank, liquidity_score, dte):
        """Calculate composite score for spread quality"""
        # Weight factors
        roi_weight = 0.25
        prob_weight = 0.35
        iv_weight = 0.20
        liquidity_weight = 0.15
        dte_weight = 0.05
        
        # Normalize components
        roi_score = min(100, roi * 2)  # 50% ROI = 100 score
        prob_score = probability
        iv_score = min(100, iv_rank * 100)  # IV rank already 0-1
        liq_score = liquidity_score
        dte_score = 100 if 30 <= dte <= 45 else 50  # Prefer sweet spot
        
        master_score = (
            roi_score * roi_weight +
            prob_score * prob_weight +
            iv_score * iv_weight +
            liq_score * liquidity_weight +
            dte_score * dte_weight
        )
        
        return round(master_score, 1)
    
    def find_bear_call_spreads(self, contracts, current_price, ticker):
        """Find bear call credit spreads"""
        spreads = []
        
        # Get calls above current price
        otm_calls = [c for c in contracts 
                     if c["type"] == "C" and 
                     c["strike"] > current_price * 1.02 and  # At least 2% OTM
                     c["is_liquid"]]
        
        # Sort by strike
        otm_calls.sort(key=lambda x: x["strike"])
        
        # Create spreads
        for i in range(len(otm_calls) - 1):
            for j in range(i + 1, min(i + 4, len(otm_calls))):  # Look at next 3 strikes
                short_call = otm_calls[i]
                long_call = otm_calls[j]
                
                spread = self.analyze_vertical_spread(
                    short_call, long_call, current_price, ticker, "BEAR_CALL"
                )
                
                if spread:
                    spreads.append(spread)
        
        return spreads
    
    def find_bull_put_spreads(self, contracts, current_price, ticker):
        """Find bull put credit spreads"""
        spreads = []
        
        # Get puts below current price
        otm_puts = [c for c in contracts 
                    if c["type"] == "P" and 
                    c["strike"] < current_price * 0.98 and  # At least 2% OTM
                    c["is_liquid"]]
        
        # Sort by strike (descending for puts)
        otm_puts.sort(key=lambda x: x["strike"], reverse=True)
        
        # Create spreads
        for i in range(len(otm_puts) - 1):
            for j in range(i + 1, min(i + 4, len(otm_puts))):  # Look at next 3 strikes
                short_put = otm_puts[i]  # Higher strike (short)
                long_put = otm_puts[j]   # Lower strike (long)
                
                spread = self.analyze_vertical_spread(
                    short_put, long_put, current_price, ticker, "BULL_PUT"
                )
                
                if spread:
                    spreads.append(spread)
        
        return spreads
    
    def analyze_vertical_spread(self, short_option, long_option, current_price, ticker, spread_type):
        """Analyze a vertical credit spread"""
        # Calculate strike width
        strike_width = abs(long_option["strike"] - short_option["strike"])
        
        # Skip if strikes too wide
        if strike_width > 10 or strike_width < 1:
            return None
        
        # Calculate credit received
        credit = short_option["bid"] - long_option["ask"]
        
        # Skip if credit too small or negative
        if credit <= 0.05:
            return None
        
        # Calculate max risk and ROI
        max_risk = strike_width - credit
        if max_risk <= 0:
            return None
        
        roi = (credit / max_risk) * 100
        
        # Skip low ROI spreads
        if roi < 10:
            return None
        
        # Calculate probability of profit
        time_to_exp = short_option["dte"] / 365
        iv = short_option["iv"]
        
        if spread_type == "BEAR_CALL":
            prob_otm = self.black_scholes_probability_otm(
                current_price, short_option["strike"], time_to_exp, iv, "call"
            )
            distance = ((short_option["strike"] - current_price) / current_price) * 100
        else:  # BULL_PUT
            prob_otm = self.black_scholes_probability_otm(
                current_price, short_option["strike"], time_to_exp, iv, "put"
            )
            distance = ((current_price - short_option["strike"]) / current_price) * 100
        
        # Skip low probability spreads
        if prob_otm < 65:
            return None
        
        # Calculate IV rank (simplified)
        iv_rank = min(1.0, iv / 0.50)  # Normalize to 0.50 as high IV
        
        # Get average liquidity score
        avg_liquidity = (short_option["liquidity_score"] + long_option["liquidity_score"]) / 2
        
        # Calculate master score
        master_score = self.calculate_master_score(
            roi, prob_otm, iv_rank, avg_liquidity, short_option["dte"]
        )
        
        # Skip low scoring spreads
        if master_score < 50:
            return None
        
        return {
            "ticker": ticker,
            "spread_type": spread_type,
            "short_strike": short_option["strike"],
            "long_strike": long_option["strike"],
            "strike_width": round(strike_width, 2),
            "dte": short_option["dte"],
            "credit": round(credit, 2),
            "max_risk": round(max_risk, 2),
            "max_profit": round(credit, 2),
            "roi_percent": round(roi, 1),
            "probability_otm": round(prob_otm, 1),
            "current_price": round(current_price, 2),
            "distance_otm": round(distance, 1),
            "iv": round(iv, 3),
            "iv_rank": round(iv_rank, 2),
            "liquidity_score": round(avg_liquidity, 1),
            "master_score": master_score,
            "short_symbol": short_option["symbol"],
            "long_symbol": long_option["symbol"],
            "breakeven": self.calculate_breakeven(spread_type, short_option["strike"], credit),
            "risk_reward_ratio": round(max_risk / credit, 2) if credit > 0 else 0
        }
    
    def calculate_breakeven(self, spread_type, short_strike, credit):
        """Calculate breakeven price"""
        if spread_type == "BEAR_CALL":
            return round(short_strike + credit, 2)
        else:  # BULL_PUT
            return round(short_strike - credit, 2)

def scan_credit_spreads(mode, verbose=True):
    """Main function to scan for credit spreads"""
    if verbose:
        print(f"🏆 Elite Credit Spread Scanner - {mode.upper()}")
        print("=" * 60)
    
    # Load required data
    try:
        with open(f"stock_prices_{mode}.json", "r") as f:
            stock_data = json.load(f)
        
        with open(f"iv_liquidity_{mode}.json", "r") as f:
            liquidity_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Missing required file: {e}")
        return None
    
    scanner = CreditSpreadScanner()
    all_spreads = []
    spreads_by_ticker = defaultdict(list)
    
    # Get enhanced contracts and organize by ticker
    contracts_by_ticker = defaultdict(list)
    for contract in liquidity_data["enhanced_contracts"].values():
        contracts_by_ticker[contract["ticker"]].append(contract)
    
    if verbose:
        print(f"🎯 Scanning {len(contracts_by_ticker)} tickers for credit spreads...")
    
    # Scan each ticker
    for ticker in contracts_by_ticker:
        if ticker not in stock_data["stock_prices"]:
            continue
        
        current_price = stock_data["stock_prices"][ticker]["current_price"]
        contracts = contracts_by_ticker[ticker]
        
        # Find bear call spreads
        bear_calls = scanner.find_bear_call_spreads(contracts, current_price, ticker)
        
        # Find bull put spreads
        bull_puts = scanner.find_bull_put_spreads(contracts, current_price, ticker)
        
        # Combine and track
        ticker_spreads = bear_calls + bull_puts
        all_spreads.extend(ticker_spreads)
        spreads_by_ticker[ticker] = ticker_spreads
        
        if verbose and ticker_spreads:
            print(f"  📊 {ticker}: Found {len(bear_calls)} bear calls, {len(bull_puts)} bull puts")
    
    # Sort by master score
    all_spreads.sort(key=lambda x: x["master_score"], reverse=True)
    
    # Get top spreads
    elite_spreads = [s for s in all_spreads if s["master_score"] >= 70]
    good_spreads = [s for s in all_spreads if 60 <= s["master_score"] < 70]
    
    # Calculate statistics
    if all_spreads:
        avg_roi = np.mean([s["roi_percent"] for s in all_spreads])
        avg_prob = np.mean([s["probability_otm"] for s in all_spreads])
        avg_score = np.mean([s["master_score"] for s in all_spreads])
        
        bear_calls = [s for s in all_spreads if s["spread_type"] == "BEAR_CALL"]
        bull_puts = [s for s in all_spreads if s["spread_type"] == "BULL_PUT"]
    else:
        avg_roi = avg_prob = avg_score = 0
        bear_calls = bull_puts = []
    
    # Create output
    result = {
        "mode": mode,
        "scan_stats": {
            "tickers_scanned": len(contracts_by_ticker),
            "total_spreads_found": len(all_spreads),
            "elite_spreads": len(elite_spreads),
            "good_spreads": len(good_spreads),
            "bear_call_spreads": len(bear_calls),
            "bull_put_spreads": len(bull_puts),
            "avg_roi": round(avg_roi, 1),
            "avg_probability": round(avg_prob, 1),
            "avg_master_score": round(avg_score, 1)
        },
        "elite_spreads": elite_spreads[:50],  # Top 50 elite
        "good_spreads": good_spreads[:50],    # Top 50 good
        "all_spreads": all_spreads[:200],     # Top 200 overall
        "spreads_by_ticker": dict(spreads_by_ticker),
        "scoring_criteria": {
            "elite_threshold": 70,
            "good_threshold": 60,
            "min_probability": 65,
            "min_roi": 10,
            "min_liquidity": 70
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Save results
    filename = f"credit_spreads_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Credit Spread Results:")
        print(f"  🎯 Total spreads found: {len(all_spreads)}")
        print(f"  🏆 Elite spreads (70+): {len(elite_spreads)}")
        print(f"  ✅ Good spreads (60-70): {len(good_spreads)}")
        print(f"  📈 Bear call spreads: {len(bear_calls)}")
        print(f"  📉 Bull put spreads: {len(bull_puts)}")
        print(f"  📁 Saved: {filename}")
        
        # Show top 5 elite spreads
        if elite_spreads:
            print(f"\n🏆 TOP 5 ELITE SPREADS:")
            for i, spread in enumerate(elite_spreads[:5], 1):
                icon = "📈" if spread["spread_type"] == "BEAR_CALL" else "📉"
                print(f"  {i}. {icon} {spread['ticker']} ${spread['short_strike']:.0f}/{spread['long_strike']:.0f}")
                print(f"     Score: {spread['master_score']:.1f} | PoP: {spread['probability_otm']:.1f}% | ROI: {spread['roi_percent']:.1f}%")
                print(f"     Credit: ${spread['credit']:.2f} | Risk: ${spread['max_risk']:.2f} | DTE: {spread['dte']}")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Elite Credit Spread Scanner")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        scan_credit_spreads(mode)
        print()

if __name__ == "__main__":
    main()
```

**Run:** `python3 find_tendies.py`
