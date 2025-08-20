# greeks.py - Greeks Analysis for Credit Spreads
"""
FIXED - Collects real Greeks data for all option contracts.
Focuses on data needed for credit spread PoP and ROI calculations.
"""
import asyncio
import json
from datetime import datetime, timezone
from collections import defaultdict
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote, Greeks
from config import USERNAME, PASSWORD
from sectors import PerfTimer

async def collect_greeks_for_credit_spreads(mode, verbose=True):
    """Collect Greeks and pricing for all option contracts"""
    if verbose:
        print(f"🧮 Collecting Greeks for Credit Spreads - {mode.upper()}")
        print("=" * 70)
    
    # Load options contracts from previous step
    try:
        with open(f"options_contracts_{mode}.json", "r") as f:
            contracts_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ options_contracts_{mode}.json not found. Run options_chains.py first.")
        return None
    
    contracts_by_ticker = contracts_data["contracts_by_ticker"]
    
    if not contracts_by_ticker:
        print(f"❌ No contracts found in options_contracts_{mode}.json")
        return None
    
    # Collect all option symbols for batch processing
    all_symbols = []
    symbol_to_ticker = {}
    symbol_to_contract_info = {}
    
    for ticker, ticker_data in contracts_by_ticker.items():
        for exp_date, exp_data in ticker_data["expiration_dates"].items():
            for contract in exp_data["contracts"]:
                symbol = contract["streamer_symbol"]
                all_symbols.append(symbol)
                symbol_to_ticker[symbol] = ticker
                symbol_to_contract_info[symbol] = {
                    "ticker": ticker,
                    "sector": ticker_data["sector"],
                    "current_price": ticker_data["current_price"],
                    "liquidity_score": ticker_data["liquidity_score"],
                    "strike": contract["strike"],
                    "option_type": contract["option_type"],
                    "dte": contract["dte"],
                    "expiration_date": exp_date,
                    "moneyness": contract["moneyness"],
                    "distance_from_current": contract["distance_from_current"]
                }
    
    if verbose:
        print(f"📊 Collecting data for {len(all_symbols):,} option contracts")
        print(f"🏢 Across {len(contracts_by_ticker)} tickers")
    
    sess = Session(USERNAME, PASSWORD)
    
    # Collect market data in batches
    quotes_data = {}
    greeks_data = {}
    batch_size = 800  # Process in manageable batches
    total_batches = (len(all_symbols) + batch_size - 1) // batch_size
    
    with PerfTimer(f"{mode.upper()} Greeks collection"):
        async with DXLinkStreamer(sess) as streamer:
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(all_symbols))
                batch_symbols = all_symbols[start_idx:end_idx]
                
                if verbose:
                    print(f"\n📦 Batch {batch_num + 1}/{total_batches}: {len(batch_symbols)} symbols")
                
                # Subscribe to both quotes and Greeks
                await streamer.subscribe(Quote, batch_symbols)
                await streamer.subscribe(Greeks, batch_symbols)
                
                batch_quotes = {}
                batch_greeks = {}
                start_time = asyncio.get_event_loop().time()
                no_data_timeout = 0
                
                # Collect data for this batch
                while (asyncio.get_event_loop().time() - start_time) < 25 and no_data_timeout < 15:
                    try:
                        # Collect quotes (bid/ask/mid pricing)
                        quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=0.4)
                        if quote and quote.event_symbol in batch_symbols:
                            bid, ask = float(quote.bid_price or 0), float(quote.ask_price or 0)
                            if bid > 0 and ask > 0 and ask >= bid:
                                mid = (bid + ask) / 2
                                batch_quotes[quote.event_symbol] = {
                                    "bid": round(bid, 4),
                                    "ask": round(ask, 4),
                                    "mid": round(mid, 4),
                                    "spread": round(ask - bid, 4),
                                    "spread_pct": round(100 * (ask - bid) / mid, 2) if mid > 0 else 0
                                }
                                no_data_timeout = 0
                    except asyncio.TimeoutError:
                        pass
                    
                    try:
                        # Collect Greeks (delta, theta, gamma, vega, IV)
                        greek = await asyncio.wait_for(streamer.get_event(Greeks), timeout=0.4)
                        if greek and greek.event_symbol in batch_symbols:
                            batch_greeks[greek.event_symbol] = {
                                "delta": round(float(greek.delta or 0), 4),
                                "theta": round(float(greek.theta or 0), 4),
                                "gamma": round(float(greek.gamma or 0), 6),
                                "vega": round(float(greek.vega or 0), 4),
                                "rho": round(float(greek.rho or 0), 4),
                                "iv": round(float(greek.volatility or 0), 4),
                                "price": round(float(greek.price or 0), 4) if greek.price else 0
                            }
                            no_data_timeout = 0
                    except asyncio.TimeoutError:
                        no_data_timeout += 1
                        continue
                    
                    # Progress check
                    quote_progress = len(batch_quotes) / len(batch_symbols) * 100
                    greek_progress = len(batch_greeks) / len(batch_symbols) * 100
                    
                    # Early exit if good coverage
                    if quote_progress >= 70 and greek_progress >= 60:
                        if verbose:
                            print(f"    ✅ Good coverage: {quote_progress:.0f}% quotes, {greek_progress:.0f}% Greeks")
                        break
                
                # Unsubscribe from batch
                await streamer.unsubscribe(Quote, batch_symbols)
                await streamer.unsubscribe(Greeks, batch_symbols)
                
                # Merge batch results
                quotes_data.update(batch_quotes)
                greeks_data.update(batch_greeks)
                
                if verbose:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    print(f"    📊 Collected {len(batch_quotes)} quotes, {len(batch_greeks)} Greeks in {elapsed:.1f}s")
                
                # Brief pause between batches
                await asyncio.sleep(0.3)
    
    # Combine quotes and Greeks data with contract info
    complete_data = {}
    
    for symbol in all_symbols:
        if symbol in quotes_data or symbol in greeks_data:
            contract_info = symbol_to_contract_info[symbol]
            quote_data = quotes_data.get(symbol, {})
            greek_data = greeks_data.get(symbol, {})
            
            # Calculate additional metrics for credit spreads
            delta = greek_data.get("delta", 0)
            iv = greek_data.get("iv", 0)
            mid_price = quote_data.get("mid", 0)
            
            complete_data[symbol] = {
                **contract_info,
                "market_data": {
                    **quote_data,
                    **greek_data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "credit_spread_metrics": {
                    "pop_estimate": round(abs(delta) * 100, 1) if delta else 0,  # Rough PoP estimate
                    "premium_quality": "high" if mid_price >= 1.0 else "medium" if mid_price >= 0.5 else "low",
                    "iv_rank": "high" if iv >= 0.4 else "medium" if iv >= 0.25 else "low",
                    "theta_decay": abs(greek_data.get("theta", 0)),
                    "suitable_for_selling": (
                        mid_price >= 0.30 and  # Minimum premium
                        quote_data.get("spread_pct", 100) <= 15 and  # Reasonable spread
                        iv >= 0.15  # Minimum IV
                    ) if quote_data and greek_data else False
                }
            }
    
    # Organize data by ticker and calculate statistics
    data_by_ticker = defaultdict(lambda: {
        "ticker_info": {},
        "contracts": [],
        "statistics": {}
    })
    
    for symbol, data in complete_data.items():
        ticker = data["ticker"]
        data_by_ticker[ticker]["ticker_info"] = {
            "ticker": ticker,
            "sector": data["sector"],
            "current_price": data["current_price"],
            "liquidity_score": data["liquidity_score"]
        }
        data_by_ticker[ticker]["contracts"].append(data)
    
    # Calculate statistics for each ticker
    for ticker, ticker_data in data_by_ticker.items():
        contracts = ticker_data["contracts"]
        if contracts:
            # Overall statistics
            total_contracts = len(contracts)
            suitable_for_selling = len([c for c in contracts if c["credit_spread_metrics"]["suitable_for_selling"]])
            
            # IV statistics
            ivs = [c["market_data"]["iv"] for c in contracts if c["market_data"].get("iv", 0) > 0]
            avg_iv = sum(ivs) / len(ivs) if ivs else 0
            
            # Premium statistics
            premiums = [c["market_data"]["mid"] for c in contracts if c["market_data"].get("mid", 0) > 0]
            avg_premium = sum(premiums) / len(premiums) if premiums else 0
            
            # Spread statistics
            spreads = [c["market_data"]["spread_pct"] for c in contracts if c["market_data"].get("spread_pct", 0) > 0]
            avg_spread = sum(spreads) / len(spreads) if spreads else 0
            
            ticker_data["statistics"] = {
                "total_contracts": total_contracts,
                "suitable_for_selling": suitable_for_selling,
                "sellable_percentage": round(suitable_for_selling / total_contracts * 100, 1) if total_contracts else 0,
                "avg_iv": round(avg_iv, 3),
                "avg_premium": round(avg_premium, 2),
                "avg_spread_pct": round(avg_spread, 1),
                "high_iv_contracts": len([c for c in contracts if c["credit_spread_metrics"]["iv_rank"] == "high"]),
                "otm_contracts": len([c for c in contracts if c["moneyness"] == "OTM"])
            }
    
    # Create comprehensive output
    result = {
        "mode": mode,
        "collection_timestamp": datetime.now(timezone.utc).isoformat(),
        "collection_stats": {
            "total_symbols_requested": len(all_symbols),
            "quotes_collected": len(quotes_data),
            "greeks_collected": len(greeks_data),
            "complete_data_points": len(complete_data),
            "quote_success_rate": round(len(quotes_data) / len(all_symbols) * 100, 1),
            "greeks_success_rate": round(len(greeks_data) / len(all_symbols) * 100, 1),
            "overall_success_rate": round(len(complete_data) / len(all_symbols) * 100, 1)
        },
        "market_data": complete_data,
        "by_ticker": dict(data_by_ticker),
        "credit_spread_summary": {
            "tickers_analyzed": len(data_by_ticker),
            "total_sellable_contracts": sum(
                ticker_data["statistics"]["suitable_for_selling"] 
                for ticker_data in data_by_ticker.values()
            ),
            "avg_iv_across_all": round(
                sum(
                    ticker_data["statistics"]["avg_iv"] * ticker_data["statistics"]["total_contracts"]
                    for ticker_data in data_by_ticker.values()
                ) / sum(
                    ticker_data["statistics"]["total_contracts"]
                    for ticker_data in data_by_ticker.values()
                ), 3
            ) if data_by_ticker else 0
        }
    }
    
    # Save results
    filename = f"greeks_data_{mode}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    if verbose:
        print(f"\n📊 {mode.upper()} Greeks Collection Results:")
        print(f"  ✅ Complete data: {len(complete_data):,}/{len(all_symbols):,} ({result['collection_stats']['overall_success_rate']:.1f}%)")
        print(f"  📈 Quote success: {result['collection_stats']['quote_success_rate']:.1f}%")
        print(f"  🧮 Greeks success: {result['collection_stats']['greeks_success_rate']:.1f}%")
        print(f"  💰 Sellable contracts: {result['credit_spread_summary']['total_sellable_contracts']:,}")
        print(f"  📊 Avg IV: {result['credit_spread_summary']['avg_iv_across_all']:.3f}")
        print(f"  📁 Saved: {filename}")
        
        # Show top tickers by sellable contracts
        if data_by_ticker:
            top_tickers = sorted(
                data_by_ticker.items(),
                key=lambda x: x[1]["statistics"]["suitable_for_selling"],
                reverse=True
            )[:5]
            print(f"\n🏆 Top Credit Spread Candidates:")
            for ticker, data in top_tickers:
                stats = data["statistics"]
                sellable = stats["suitable_for_selling"]
                total = stats["total_contracts"]
                pct = stats["sellable_percentage"]
                iv = stats["avg_iv"]
                print(f"    {ticker}: {sellable}/{total} sellable ({pct:.1f}%) | IV: {iv:.3f}")
    
    return result

def main():
    """Main function for standalone execution"""
    print("🚀 Greeks Analysis for Credit Spreads")
    print("=" * 50)
    
    for mode in ["gpt", "grok"]:
        result = asyncio.run(collect_greeks_for_credit_spreads(mode))
        if result:
            sellable = result["credit_spread_summary"]["total_sellable_contracts"]
            print(f"🎯 {mode.upper()}: {sellable:,} contracts ready for credit spreads")
        print()

if __name__ == "__main__":
    main()
