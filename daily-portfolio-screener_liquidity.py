**Create:** `touch liquidity.py`
**Query:** `open -e liquidity.py`

```bash
# sector_selection.py - Final Sector Selection
"""
NEW - replaces liquidity.py. 
Selects the best ticker per sector based on liquidity rankings.
Output: 18 tickers (9 GPT + 9 Grok) for credit spread analysis.
"""
import json
from datetime import datetime
from collections import defaultdict
from sectors import get_sectors, PerfTimer

def select_best_per_sector(mode):
    """Select best ticker per sector based on liquidity ranking"""
    print(f"🎯 Selecting Best {mode.upper()} Tickers per Sector")
    print("=" * 60)
    
    # Load ticker rankings
    try:
        with open(f"ticker_rankings_{mode}.json", "r") as f:
            rankings_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ ticker_rankings_{mode}.json not found")
        return None
    
    successful_tickers = rankings_data["ticker_rankings"]
    by_sector = rankings_data["by_sector"]
    
    print(f"📊 Input: {len(successful_tickers)} ranked tickers across {len(by_sector)} sectors")
    
    # Select best ticker per sector
    selected_basket = {}
    selection_stats = {
        "sectors_covered": 0,
        "sectors_missing": [],
        "avg_liquidity_score": 0,
        "score_range": [100, 0]  # min, max
    }
    
    sectors = get_sectors(mode)
    
    for sector_name in sectors.keys():
        sector_tickers = by_sector.get(sector_name, [])
        
        if sector_tickers:
            # Pick highest scoring ticker
            best_ticker = max(sector_tickers, key=lambda x: x["liquidity_score"])
            selected_basket[sector_name] = {
                "ticker": best_ticker["ticker"],
                "liquidity_score": best_ticker["liquidity_score"],
                "metrics": best_ticker["metrics"],
                "spot_price": best_ticker["spot_price"],
                "sector": sector_name,
                "rank_in_sector": 1,
                "total_in_sector": len(sector_tickers)
            }
            
            # Update stats
            selection_stats["sectors_covered"] += 1
            score = best_ticker["liquidity_score"]
            if score < selection_stats["score_range"][0]:
                selection_stats["score_range"][0] = score
            if score > selection_stats["score_range"][1]:
                selection_stats["score_range"][1] = score
                
        else:
            selection_stats["sectors_missing"].append(sector_name)
            print(f"  ⚠️ No valid tickers for {sector_name}")
    
    # Calculate average score
    if selected_basket:
        scores = [data["liquidity_score"] for data in selected_basket.values()]
        selection_stats["avg_liquidity_score"] = sum(scores) / len(scores)
    
    # Create output
    output = {
        "mode": mode,
        "selection_timestamp": datetime.now().isoformat(),
        "selection_stats": selection_stats,
        "selected_basket": selected_basket,
        "sector_analysis": {
            sector: {
                "selected_ticker": selected_basket.get(sector, {}).get("ticker"),
                "candidates_analyzed": len(by_sector.get(sector, [])),
                "top_3_scores": [t["liquidity_score"] for t in sorted(by_sector.get(sector, []), 
                                key=lambda x: x["liquidity_score"], reverse=True)[:3]]
            }
            for sector in sectors.keys()
        }
    }
    
    # Save results
    filename = f"sector_selection_{mode}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"📊 {mode.upper()} Sector Selection Results:")
    print(f"  ✅ Sectors covered: {selection_stats['sectors_covered']}/9")
    print(f"  🏆 Avg liquidity score: {selection_stats['avg_liquidity_score']:.1f}")
    print(f"  📈 Score range: {selection_stats['score_range'][0]:.1f} - {selection_stats['score_range'][1]:.1f}")
    print(f"  📁 Saved: {filename}")
    
    if selection_stats["sectors_missing"]:
        print(f"  ❌ Missing sectors: {selection_stats['sectors_missing']}")
    
    # Show selected basket
    print(f"\n🏆 {mode.upper()} SELECTED BASKET:")
    print("  Sector | Ticker | Score | Spread% | OI")
    print("  " + "-" * 45)
    
    sorted_basket = sorted(selected_basket.items(), 
                          key=lambda x: x[1]["liquidity_score"], reverse=True)
    
    for sector, data in sorted_basket:
        ticker = data["ticker"]
        score = data["liquidity_score"]
        spread = data["metrics"]["atm_spread_pct"]
        oi = data["metrics"]["avg_open_interest"]
        sector_short = sector[:20] + "..." if len(sector) > 20 else sector
        print(f"  {sector_short:20} | {ticker:6} | {score:5.1f} | {spread:6.1f} | {oi:8.0f}")
    
    return output

def create_final_universe():
    """Create final combined universe of 18 tickers"""
    print("\n🎯 Creating Final Combined Universe")
    print("=" * 60)
    
    combined_basket = {}
    total_tickers = 0
    
    with PerfTimer("Final universe creation"):
        for mode in ["gpt", "grok"]:
            try:
                with open(f"sector_selection_{mode}.json", "r") as f:
                    selection_data = json.load(f)
                
                selected_basket = selection_data["selected_basket"]
                mode_tickers = []
                
                for sector, data in selected_basket.items():
                    ticker_info = {
                        "ticker": data["ticker"],
                        "sector": sector,
                        "mode": mode,
                        "liquidity_score": data["liquidity_score"],
                        "spot_price": data["spot_price"]
                    }
                    mode_tickers.append(ticker_info)
                    total_tickers += 1
                
                combined_basket[mode] = {
                    "tickers": mode_tickers,
                    "count": len(mode_tickers),
                    "avg_score": sum(t["liquidity_score"] for t in mode_tickers) / len(mode_tickers) if mode_tickers else 0
                }
                
                print(f"  📊 {mode.upper()}: {len(mode_tickers)} tickers, avg score {combined_basket[mode]['avg_score']:.1f}")
                
            except FileNotFoundError:
                print(f"  ❌ Missing {mode} selection data")
                combined_basket[mode] = {"tickers": [], "count": 0, "avg_score": 0}
    
    # Create flat list for credit spread analysis
    final_ticker_list = []
    for mode_data in combined_basket.values():
        final_ticker_list.extend(mode_data["tickers"])
    
    # Create final output
    final_universe = {
        "creation_timestamp": datetime.now().isoformat(),
        "total_tickers": total_tickers,
        "target_tickers": 18,  # 9 per mode
        "breakdown_by_mode": combined_basket,
        "ticker_list": final_ticker_list,
        "tickers_for_credit_analysis": [t["ticker"] for t in final_ticker_list]
    }
    
    # Save final universe
    with open("final_universe.json", "w") as f:
        json.dump(final_universe, f, indent=2)
    
    print(f"\n🎉 Final Universe Created:")
    print(f"  📊 Total tickers: {total_tickers}/18 target")
    print(f"  📁 Saved: final_universe.json")
    print(f"  🎯 Ready for credit spread analysis")
    
    # Show final list
    print(f"\n📋 FINAL TICKER LIST ({total_tickers} tickers):")
    gpt_tickers = [t["ticker"] for t in combined_basket["gpt"]["tickers"]]
    grok_tickers = [t["ticker"] for t in combined_basket["grok"]["tickers"]]
    print(f"  GPT ({len(gpt_tickers)}): {', '.join(gpt_tickers)}")
    print(f"  GROK ({len(grok_tickers)}): {', '.join(grok_tickers)}")
    
    return final_universe

def main():
    """Main sector selection"""
    print("🚀 Sector Selection & Final Universe Creation")
    print("=" * 50)
    
    # Select best per sector for each mode
    for mode in ["gpt", "grok"]:
        select_best_per_sector(mode)
        print()
    
    # Create final combined universe
    create_final_universe()

if __name__ == "__main__":
    main()
```
**Run:** `python3 liquidity.py`
