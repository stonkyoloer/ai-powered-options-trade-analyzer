# spread_analyzer.py - Credit Spread Analysis & Final Rankings
"""
FINAL STEP - Constructs and analyzes credit spreads using real market data.
Calculates actual PoP and ROI, then selects top 3 spreads per sector per AI model.
Output: AI bot name | Sector | Ticker | Bull Put or Bear Call | $/$ leg cost | DTE | PoP | ROI
"""
import json
import math
from datetime import datetime
from collections import defaultdict
from scipy.stats import norm
import itertools
from sectors import get_sectors

def calculate_black_scholes_pop(spot, strike, dte, iv, option_type, risk_free_rate=0.05):
    """Calculate probability of profit using Black-Scholes"""
    if dte <= 0 or iv <= 0 or spot <= 0:
        return 0
    
    try:
        T = dte / 365.0
        d1 = (math.log(spot / strike) + (risk_free_rate + 0.5 * iv**2) * T) / (iv * math.sqrt(T))
        d2 = d1 - iv * math.sqrt(T)
        
        if option_type == "C":
            # For calls, PoP = probability of finishing below strike (N(-d2))
            return norm.cdf(-d2) * 100
        else:
            # For puts, PoP = probability of finishing above strike (N(d2))
            return norm.cdf(d2) * 100
    except:
        return 0

def construct_credit_spreads(ticker_data, max_spreads_per_expiry=10):
    """Construct all viable credit spreads for a ticker"""
    ticker = ticker_data["ticker_info"]["ticker"]
    current_price = ticker_data["ticker_info"]["current_price"]
    contracts = ticker_data["contracts"]
    
    # Group contracts by expiration and type
    by_expiry = defaultdict(lambda: {"calls": [], "puts": []})
    
    for contract in contracts:
        if contract["credit_spread_metrics"]["suitable_for_selling"]:
            exp_date = contract["expiration_date"]
            option_type = contract["option_type"]
            
            if option_type == "C":
                by_expiry[exp_date]["calls"].append(contract)
            else:
                by_expiry[exp_date]["puts"].append(contract)
    
    credit_spreads = []
    
    for exp_date, exp_contracts in by_expiry.items():
        calls = sorted(exp_contracts["calls"], key=lambda x: x["strike"])
        puts = sorted(exp_contracts["puts"], key=lambda x: x["strike"], reverse=True)
        
        if not calls or not puts:
            continue
        
        dte = calls[0]["dte"] if calls else puts[0]["dte"]
        
        # Construct Bear Call Spreads (sell lower strike call, buy higher strike call)
        bear_calls_created = 0
        for i, short_call in enumerate(calls):
            if bear_calls_created >= max_spreads_per_expiry:
                break
                
            # Look for long calls with higher strikes
            for long_call in calls[i+1:]:
                if long_call["strike"] - short_call["strike"] >= 2.5:  # Minimum $2.50 width
                    spread_width = long_call["strike"] - short_call["strike"]
                    
                    # Calculate spread pricing
                    short_premium = short_call["market_data"]["mid"]
                    long_premium = long_call["market_data"]["mid"]
                    net_credit = short_premium - long_premium
                    
                    if net_credit > 0.25:  # Minimum $0.25 credit
                        # Calculate metrics
                        max_profit = net_credit
                        max_loss = spread_width - net_credit
                        roi = (max_profit / max_loss * 100) if max_loss > 0 else 0
                        
                        # PoP based on short strike (needs to stay below)
                        short_iv = short_call["market_data"]["iv"]
                        pop = calculate_black_scholes_pop(
                            current_price, short_call["strike"], dte, short_iv, "C"
                        )
                        
                        # Quality filters
                        if roi >= 10 and pop >= 50 and net_credit >= 0.30:
                            credit_spreads.append({
                                "spread_type": "Bear Call",
                                "ticker": ticker,
                                "sector": short_call["sector"],
                                "current_price": current_price,
                                "dte": dte,
                                "expiration": exp_date,
                                "short_leg": {
                                    "strike": short_call["strike"],
                                    "premium": short_premium,
                                    "iv": short_iv,
                                    "delta": short_call["market_data"]["delta"]
                                },
                                "long_leg": {
                                    "strike": long_call["strike"],
                                    "premium": long_premium,
                                    "iv": long_call["market_data"]["iv"],
                                    "delta": long_call["market_data"]["delta"]
                                },
                                "spread_width": spread_width,
                                "net_credit": round(net_credit, 2),
                                "max_profit": round(max_profit, 2),
                                "max_loss": round(max_loss, 2),
                                "roi": round(roi, 1),
                                "pop": round(pop, 1),
                                "legs": f"${short_call['strike']:.0f}/${long_call['strike']:.0f}",
                                "distance_from_current": round((short_call["strike"] - current_price) / current_price * 100, 1)
                            })
                            bear_calls_created += 1
                            break
        
        # Construct Bull Put Spreads (sell higher strike put, buy lower strike put)
        bull_puts_created = 0
        for i, short_put in enumerate(puts):
            if bull_puts_created >= max_spreads_per_expiry:
                break
                
            # Look for long puts with lower strikes
            for long_put in puts[i+1:]:
                if short_put["strike"] - long_put["strike"] >= 2.5:  # Minimum $2.50 width
                    spread_width = short_put["strike"] - long_put["strike"]
                    
                    # Calculate spread pricing
                    short_premium = short_put["market_data"]["mid"]
                    long_premium = long_put["market_data"]["mid"]
                    net_credit = short_premium - long_premium
                    
                    if net_credit > 0.25:  # Minimum $0.25 credit
                        # Calculate metrics
                        max_profit = net_credit
                        max_loss = spread_width - net_credit
                        roi = (max_profit / max_loss * 100) if max_loss > 0 else 0
                        
                        # PoP based on short strike (needs to stay above)
                        short_iv = short_put["market_data"]["iv"]
                        pop = calculate_black_scholes_pop(
                            current_price, short_put["strike"], dte, short_iv, "P"
                        )
                        
                        # Quality filters
                        if roi >= 10 and pop >= 50 and net_credit >= 0.30:
                            credit_spreads.append({
                                "spread_type": "Bull Put",
                                "ticker": ticker,
                                "sector": short_put["sector"],
                                "current_price": current_price,
                                "dte": dte,
                                "expiration": exp_date,
                                "short_leg": {
                                    "strike": short_put["strike"],
                                    "premium": short_premium,
                                    "iv": short_iv,
                                    "delta": short_put["market_data"]["delta"]
                                },
                                "long_leg": {
                                    "strike": long_put["strike"],
                                    "premium": long_premium,
                                    "iv": long_put["market_data"]["iv"],
                                    "delta": long_put["market_data"]["delta"]
                                },
                                "spread_width": spread_width,
                                "net_credit": round(net_credit, 2),
                                "max_profit": round(max_profit, 2),
                                "max_loss": round(max_loss, 2),
                                "roi": round(roi, 1),
                                "pop": round(pop, 1),
                                "legs": f"${short_put['strike']:.0f}/${long_put['strike']:.0f}",
                                "distance_from_current": round((current_price - short_put["strike"]) / current_price * 100, 1)
                            })
                            bull_puts_created += 1
                            break
    
    return credit_spreads

def analyze_credit_spreads_for_mode(mode, verbose=True):
    """Analyze and rank credit spreads for a mode"""
    if verbose:
        print(f"🎯 Analyzing Credit Spreads - {mode.upper()}")
        print("=" * 70)
    
    # Load Greeks data
    try:
        with open(f"greeks_data_{mode}.json", "r") as f:
            greeks_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ greeks_data_{mode}.json not found. Run greeks.py first.")
        return None
    
    tickers_data = greeks_data["by_ticker"]
    
    if verbose:
        print(f"📊 Analyzing {len(tickers_data)} tickers for credit spreads...")
    
    # Construct spreads for each ticker
    all_spreads = []
    spreads_by_ticker = {}
    
    for ticker, ticker_data in tickers_data.items():
        if verbose:
            print(f"  🔍 {ticker}: Constructing spreads...")
        
        ticker_spreads = construct_credit_spreads(ticker_data)
        spreads_by_ticker[ticker] = ticker_spreads
        all_spreads.extend(ticker_spreads)
        
        if verbose:
            bear_calls = len([s for s in ticker_spreads if s["spread_type"] == "Bear Call"])
            bull_puts = len([s for s in ticker_spreads if s["spread_type"] == "Bull Put"])
            print(f"    ✅ Found {len(ticker_spreads)} spreads ({bear_calls} Bear Call, {bull_puts} Bull Put)")
    
    if verbose:
        print(f"\n📊 Total spreads constructed: {len(all_spreads)}")
    
    # Group spreads by sector
    sectors = get_sectors(mode)
    spreads_by_sector = defaultdict(list)
    
    for spread in all_spreads:
        sector = spread["sector"]
        spreads_by_sector[sector].append(spread)
    
    # Rank spreads within each sector and select top 3
    sector_rankings = {}
    final_selections = []
    
    for sector in sectors.keys():
        sector_spreads = spreads_by_sector[sector]
        
        if not sector_spreads:
            if verbose:
                print(f"  ⚠️ {sector}: No spreads found")
            continue
        
        # Sort by composite score (ROI * PoP / 100 for risk-adjusted return)
        sector_spreads.sort(key=lambda x: (x["roi"] * x["pop"] / 100, x["roi"], x["pop"]), reverse=True)
        
        # Select top 3
        top_3 = sector_spreads[:3]
        sector_rankings[sector] = {
            "total_spreads": len(sector_spreads),
            "top_3": top_3,
            "avg_roi": round(sum(s["roi"] for s in sector_spreads) / len(sector_spreads), 1),
            "avg_pop": round(sum(s["pop"] for s in sector_spreads) / len(sector_spreads), 1)
        }
        
        final_selections.extend(top_3)
        
        if verbose:
            print(f"  🏆 {sector}: {len(sector_spreads)} spreads → Top 3 selected")
            for i, spread in enumerate(top_3, 1):
                print(f"    {i}. {spread['ticker']} {spread['spread_type']} {spread['legs']} | ROI: {spread['roi']:.1f}% | PoP: {spread['pop']:.1f}%")
    
    # Create final output
    result = {
        "mode": mode,
        "analysis_timestamp": datetime.now().isoformat(),
        "summary": {
            "total_spreads_analyzed": len(all_spreads),
            "sectors_with_spreads": len(sector_rankings),
            "final_selections": len(final_selections),
            "target_selections": len(sectors) * 3,  # 3 per sector
            "avg_roi_all": round(sum(s["roi"] for s in all_spreads) / len(all_spreads), 1) if all_spreads else 0,
            "avg_pop_all": round(sum(s["pop"] for s in all_spreads) / len(all_spreads), 1) if all_spreads else 0
        },
        "by_sector": sector_rankings,
        "final_selections": final_selections,
        "all_spreads": all_spreads
    }
    
    # Save results
    filename = f"credit_spreads_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Credit Spread Analysis Complete:")
        print(f"  🎯 Final selections: {len(final_selections)}/{len(sectors) * 3}")
        print(f"  📈 Avg ROI: {result['summary']['avg_roi_all']:.1f}%")
        print(f"  🎲 Avg PoP: {result['summary']['avg_pop_all']:.1f}%")
        print(f"  📁 Saved: {filename}")
    
    return result

def create_final_comparison_table():
    """Create the final comparison table between GPT, Grok, and Claude"""
    print("🏆 Creating Final Comparison Table")
    print("=" * 70)
    
    # Load results from modes
    gpt_data = None
    grok_data = None
    claude_data = None
    
    try:
        with open("credit_spreads_gpt.json", "r") as f:
            gpt_data = json.load(f)
    except FileNotFoundError:
        print("❌ credit_spreads_gpt.json not found")
    
    try:
        with open("credit_spreads_grok.json", "r") as f:
            grok_data = json.load(f)
    except FileNotFoundError:
        print("❌ credit_spreads_grok.json not found")
    
    try:
        with open("credit_spreads_claude.json", "r") as f:
            claude_data = json.load(f)
    except FileNotFoundError:
        print("❌ credit_spreads_claude.json not found")
    
    if not gpt_data or not grok_data:
        print("❌ Missing data files - run analysis for GPT and Grok first")
        return None
    
    final_table = []
    
    # Add GPT selections
    for spread in gpt_data["final_selections"]:
        final_table.append({
            "AI_bot_name": "GPT",
            "Sector": spread["sector"],
            "Ticker": spread["ticker"],
            "Spread_Type": spread["spread_type"],
            "Legs": spread["legs"],
            "DTE": spread["dte"],
            "PoP": f"{spread['pop']:.1f}%",
            "ROI": f"{spread['roi']:.1f}%",
            "Net_Credit": f"${spread['net_credit']:.2f}",
            "Distance_From_Current": f"{spread['distance_from_current']:.1f}%"
        })
    
    # Add Grok selections
    for spread in grok_data["final_selections"]:
        final_table.append({
            "AI_bot_name": "Grok",
            "Sector": spread["sector"],
            "Ticker": spread["ticker"],
            "Spread_Type": spread["spread_type"],
            "Legs": spread["legs"],
            "DTE": spread["dte"],
            "PoP": f"{spread['pop']:.1f}%",
            "ROI": f"{spread['roi']:.1f}%",
            "Net_Credit": f"${spread['net_credit']:.2f}",
            "Distance_From_Current": f"{spread['distance_from_current']:.1f}%"
        })
    
    # Add Claude selections if available
    if claude_data:
        for spread in claude_data["final_selections"]:
            final_table.append({
                "AI_bot_name": "Claude",
                "Sector": spread["sector"],
                "Ticker": spread["ticker"],
                "Spread_Type": spread["spread_type"],
                "Legs": spread["legs"],
                "DTE": spread["dte"],
                "PoP": f"{spread['pop']:.1f}%",
                "ROI": f"{spread['roi']:.1f}%",
                "Net_Credit": f"${spread['net_credit']:.2f}",
                "Distance_From_Current": f"{spread['distance_from_current']:.1f}%"
            })
    
    # Sort by AI bot name, then by sector
    final_table.sort(key=lambda x: (x["AI_bot_name"], x["Sector"]))
    
    # Save final table
    final_output = {
        "creation_timestamp": datetime.now().isoformat(),
        "total_spreads": len(final_table),
        "gpt_spreads": len([s for s in final_table if s["AI_bot_name"] == "GPT"]),
        "grok_spreads": len([s for s in final_table if s["AI_bot_name"] == "Grok"]),
        "claude_spreads": len([s for s in final_table if s["AI_bot_name"] == "Claude"]),
        "final_comparison_table": final_table,
        "summary_stats": {
            "gpt_avg_roi": sum(float(s["ROI"].rstrip('%')) for s in final_table if s["AI_bot_name"] == "GPT") / len([s for s in final_table if s["AI_bot_name"] == "GPT"]) if [s for s in final_table if s["AI_bot_name"] == "GPT"] else 0,
            "grok_avg_roi": sum(float(s["ROI"].rstrip('%')) for s in final_table if s["AI_bot_name"] == "Grok") / len([s for s in final_table if s["AI_bot_name"] == "Grok"]) if [s for s in final_table if s["AI_bot_name"] == "Grok"] else 0,
            "claude_avg_roi": sum(float(s["ROI"].rstrip('%')) for s in final_table if s["AI_bot_name"] == "Claude") / len([s for s in final_table if s["AI_bot_name"] == "Claude"]) if [s for s in final_table if s["AI_bot_name"] == "Claude"] else 0,
            "gpt_avg_pop": sum(float(s["PoP"].rstrip('%')) for s in final_table if s["AI_bot_name"] == "GPT") / len([s for s in final_table if s["AI_bot_name"] == "GPT"]) if [s for s in final_table if s["AI_bot_name"] == "GPT"] else 0,
            "grok_avg_pop": sum(float(s["PoP"].rstrip('%')) for s in final_table if s["AI_bot_name"] == "Grok") / len([s for s in final_table if s["AI_bot_name"] == "Grok"]) if [s for s in final_table if s["AI_bot_name"] == "Grok"] else 0,
            "claude_avg_pop": sum(float(s["PoP"].rstrip('%')) for s in final_table if s["AI_bot_name"] == "Claude") / len([s for s in final_table if s["AI_bot_name"] == "Claude"]) if [s for s in final_table if s["AI_bot_name"] == "Claude"] else 0
        }
    }
    
    with open("final_credit_spread_comparison.json", "w") as f:
        json.dump(final_output, f, indent=2)
    
    # Display the table
    print("\n🎯 FINAL CREDIT SPREAD COMPARISON TABLE")
    print("=" * 120)
    print(f"{'AI Bot':<6} | {'Sector':<20} | {'Ticker':<6} | {'Type':<10} | {'Legs':<12} | {'DTE':<3} | {'PoP':<6} | {'ROI':<6}")
    print("-" * 120)
    
    for spread in final_table:
        print(f"{spread['AI_bot_name']:<6} | {spread['Sector'][:20]:<20} | {spread['Ticker']:<6} | {spread['Spread_Type']:<10} | {spread['Legs']:<12} | {spread['DTE']:<3} | {spread['PoP']:<6} | {spread['ROI']:<6}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  GPT: {final_output['gpt_spreads']} spreads | Avg ROI: {final_output['summary_stats']['gpt_avg_roi']:.1f}% | Avg PoP: {final_output['summary_stats']['gpt_avg_pop']:.1f}%")
    print(f"  Grok: {final_output['grok_spreads']} spreads | Avg ROI: {final_output['summary_stats']['grok_avg_roi']:.1f}% | Avg PoP: {final_output['summary_stats']['grok_avg_pop']:.1f}%")
    if final_output['claude_spreads']:
        print(f"  Claude: {final_output['claude_spreads']} spreads | Avg ROI: {final_output['summary_stats']['claude_avg_roi']:.1f}% | Avg PoP: {final_output['summary_stats']['claude_avg_pop']:.1f}%")
    print(f"  📁 Saved: final_credit_spread_comparison.json")
    
    return final_output

def main():
    """Main function - analyze both modes and create comparison"""
    print("🚀 Final Credit Spread Analysis")
    print("=" * 50)
    
    # Analyze modes
    for mode in ["gpt", "grok", "claude"]:
        result = analyze_credit_spreads_for_mode(mode)
        if result:
            selections = len(result["final_selections"])
            avg_roi = result["summary"]["avg_roi_all"]
            avg_pop = result["summary"]["avg_pop_all"]
            print(f"✅ {mode.upper()}: {selections} spreads selected | ROI: {avg_roi:.1f}% | PoP: {avg_pop:.1f}%")
        print()
    
    # Create final comparison
    create_final_comparison_table()

if __name__ == "__main__":
    main()
