**Create:** `touch iv_liquidity.py`

**Query:** `touch iv_liquidity.py`

```bash
# advanced_iv_liquidity.py - STEP 6: Fixed version with better data collection
import json
import numpy as np
from datetime import datetime
import asyncio
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Summary
from config import USERNAME, PASSWORD

async def analyze_iv_and_liquidity():
    print("📊 STEP 6: Advanced IV & Liquidity Analysis")
    print("=" * 70)
    print("🎯 Collecting comprehensive market data...")
    
    # Load previous data
    with open('step1_stock_prices.json', 'r') as f:
        stock_data = json.load(f)
    
    with open('step2_options_contracts.json', 'r') as f:
        options_data = json.load(f)
    
    with open('step3_iv_data.json', 'r') as f:
        iv_data = json.load(f)
    
    with open('step4_market_prices.json', 'r') as f:
        price_data = json.load(f)
    
    print(f"✅ Loaded data: {options_data['total_contracts_found']} contracts to analyze")
    
    session = Session(USERNAME, PASSWORD)
    
    # Create lookups
    price_lookup = {}
    for company, prices_list in price_data['prices_by_company'].items():
        for price in prices_list:
            price_lookup[price['contract_name']] = price
    
    companies = list(stock_data['stock_prices'].keys())
    enhanced_options = {}
    
    # Collect ALL contract symbols
    all_symbols = []
    symbol_to_company = {}
    
    for company, company_data in options_data['options_by_company'].items():
        for exp_data in company_data['expiration_dates'].values():
            for contract in exp_data['contracts']:
                symbol = contract['streamer_symbol']
                all_symbols.append(symbol)
                symbol_to_company[symbol] = company
    
    print(f"📡 Need to get Summary data for {len(all_symbols)} contracts...")
    
    # Process in batches to avoid overwhelming the connection
    batch_size = 500
    summary_data = {}
    
    async with DXLinkStreamer(session) as streamer:
        for batch_start in range(0, len(all_symbols), batch_size):
            batch_end = min(batch_start + batch_size, len(all_symbols))
            batch_symbols = all_symbols[batch_start:batch_end]
            
            print(f"\n   📊 Processing batch {batch_start//batch_size + 1}/{(len(all_symbols) + batch_size - 1)//batch_size}")
            print(f"      Symbols {batch_start + 1} to {batch_end} of {len(all_symbols)}")
            
            # Subscribe to this batch
            await streamer.subscribe(Summary, batch_symbols)
            
            # Collect data for this batch
            batch_collected = 0
            start_time = asyncio.get_event_loop().time()
            no_data_timeout = 0
            
            # Collect for up to 30 seconds per batch or until we stop getting new data
            while (asyncio.get_event_loop().time() - start_time) < 30 and no_data_timeout < 5:
                try:
                    summary = await asyncio.wait_for(streamer.get_event(Summary), timeout=1.0)
                    if summary and summary.event_symbol in batch_symbols:
                        summary_data[summary.event_symbol] = {
                            'open_interest': int(summary.open_interest) if summary.open_interest else 0,
                            'volume': int(summary.prev_day_volume) if summary.prev_day_volume else 0,
                            'day_high': float(summary.day_high_price) if summary.day_high_price else 0,
                            'day_low': float(summary.day_low_price) if summary.day_low_price else 0
                        }
                        batch_collected += 1
                        no_data_timeout = 0  # Reset timeout counter
                        
                        if batch_collected % 50 == 0:
                            print(f"      Collected: {batch_collected} summaries")
                        
                except asyncio.TimeoutError:
                    no_data_timeout += 1
                    continue
                except Exception as e:
                    continue
            
            print(f"      ✅ Batch complete: {batch_collected} summaries collected")
            
            # Unsubscribe from this batch before moving to next
            await streamer.unsubscribe(Summary, batch_symbols)
            
            # Small delay between batches
            await asyncio.sleep(0.5)
    
    print(f"\n✅ Total Summary data collected: {len(summary_data)} contracts")
    
    # Now analyze each company with all the data
    for company in companies:
        print(f"\n🏢 Analyzing {company}...")
        
        company_options = options_data['options_by_company'].get(company, {})
        if not company_options:
            continue
        
        current_price = company_options['current_stock_price']
        company_contracts = []
        
        # Stats tracking
        stats = {
            'total_analyzed': 0,
            'has_iv': 0,
            'has_price': 0,
            'has_summary': 0,
            'has_all_data': 0
        }
        
        for exp_data in company_options['expiration_dates'].values():
            for contract in exp_data['contracts']:
                symbol = contract['streamer_symbol']
                stats['total_analyzed'] += 1
                
                # Check data availability
                has_iv = symbol in iv_data['iv_by_contract']
                has_price = symbol in price_lookup
                has_summary = symbol in summary_data
                
                if has_iv:
                    stats['has_iv'] += 1
                if has_price:
                    stats['has_price'] += 1
                if has_summary:
                    stats['has_summary'] += 1
                
                # Only analyze if we have at least IV and price data
                if not (has_iv and has_price):
                    continue
                
                stats['has_all_data'] += 1
                
                # Get all data
                current_iv = iv_data['iv_by_contract'][symbol]
                price_info = price_lookup[symbol]
                
                # Get summary data or use defaults
                if has_summary:
                    liquidity = summary_data[symbol]
                else:
                    liquidity = {'open_interest': 0, 'volume': 0}
                
                # Calculate metrics
                bid = price_info['what_buyers_pay']
                ask = price_info['what_sellers_want']
                spread = ask - bid
                
                # Calculate liquidity score
                liquidity_score = calculate_liquidity_score(
                    liquidity['open_interest'],
                    liquidity['volume'],
                    spread,
                    company
                )
                
                contract_analysis = {
                    'symbol': symbol,
                    'strike': contract['strike_price'],
                    'type': contract['contract_type'],
                    'days_to_exp': contract['days_until_expires'],
                    'current_iv': current_iv,
                    'open_interest': liquidity['open_interest'],
                    'volume': liquidity['volume'],
                    'bid': bid,
                    'ask': ask,
                    'bid_ask_spread': spread,
                    'liquidity_score': liquidity_score,
                    'liquid': liquidity_score >= 70,
                    'has_summary_data': has_summary
                }
                
                company_contracts.append(contract_analysis)
        
        # Calculate company metrics
        if company_contracts:
            liquid_contracts = [c for c in company_contracts if c['liquid']]
            high_volume = [c for c in company_contracts if c['volume'] >= 100]
            high_oi = [c for c in company_contracts if c['open_interest'] >= 1000]
            tight_spreads = [c for c in company_contracts if c['bid_ask_spread'] <= 0.10]
            
            avg_iv = np.mean([c['current_iv'] for c in company_contracts])
            
            enhanced_options[company] = {
                'current_stock_price': current_price,
                'avg_implied_volatility': avg_iv,
                'data_coverage': stats,
                'metrics': {
                    'total_contracts_analyzed': len(company_contracts),
                    'liquid_contracts': len(liquid_contracts),
                    'high_volume_contracts': len(high_volume),
                    'high_oi_contracts': len(high_oi),
                    'tight_spread_contracts': len(tight_spreads),
                    'contracts_with_summary': sum(1 for c in company_contracts if c['has_summary_data'])
                },
                'top_liquid_contracts': sorted(
                    company_contracts, 
                    key=lambda x: (x['liquidity_score'], x['open_interest']), 
                    reverse=True
                )[:20]
            }
            
            print(f"   📊 Avg IV: {avg_iv:.3f}")
            print(f"   📈 Contracts analyzed: {len(company_contracts)}")
            print(f"   💧 Liquid contracts: {len(liquid_contracts)}")
            print(f"   📊 High OI (≥1000): {len(high_oi)}")
            print(f"   📊 Summary data coverage: {stats['has_summary']}/{stats['total_analyzed']} ({stats['has_summary']/stats['total_analyzed']*100:.1f}%)")
    
    # Find best opportunities
    all_liquid_contracts = []
    for company, data in enhanced_options.items():
        for contract in data['top_liquid_contracts']:
            if contract['liquid']:
                contract['company'] = company
                all_liquid_contracts.append(contract)
    
    # Sort by liquidity score
    all_liquid_contracts.sort(key=lambda x: (x['liquidity_score'], x['open_interest']), reverse=True)
    
    # Save results
    result = {
        'step': 6,
        'what_we_did': 'Comprehensive IV & Liquidity Analysis',
        'timestamp': datetime.now().isoformat(),
        'data_summary': {
            'total_contracts': options_data['total_contracts_found'],
            'contracts_with_iv': len(iv_data['iv_by_contract']),
            'contracts_with_prices': price_data['total_prices_collected'],
            'contracts_with_summary': len(summary_data)
        },
        'companies_analyzed': len(enhanced_options),
        'enhanced_options': enhanced_options,
        'top_liquid_contracts': all_liquid_contracts[:50],
        'liquidity_criteria': {
            'score_threshold': 70,
            'oi_threshold': 1000,
            'volume_threshold': 100,
            'spread_thresholds': {
                'top_names': 0.05,
                'others': 0.10
            }
        }
    }
    
    filename = 'step6_advanced_iv_liquidity.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Summary data coverage: {len(summary_data)}/{len(all_symbols)} contracts ({len(summary_data)/len(all_symbols)*100:.1f}%)")
    print(f"💧 Total liquid contracts found: {len(all_liquid_contracts)}")
    print(f"📁 Results saved to: {filename}")
    
    return result

def calculate_liquidity_score(open_interest, volume, spread, company):
    """Calculate 0-100 liquidity score"""
    score = 0
    
    # Open interest component (40 points)
    if open_interest >= 1000:
        score += 40
    elif open_interest >= 500:
        score += 30
    elif open_interest >= 100:
        score += 20
    elif open_interest > 0:
        score += min(20, (open_interest / 100) * 20)
    
    # Volume component (30 points)
    if volume >= 1000:
        score += 30
    elif volume >= 500:
        score += 20
    elif volume >= 100:
        score += 10
    elif volume > 0:
        score += min(10, (volume / 100) * 10)
    
    # Spread component (30 points)
    if spread >= 0:
        if company in ['NVDA', 'TSLA', 'AMZN']:
            if spread <= 0.05:
                score += 30
            elif spread <= 0.10:
                score += 20
            elif spread <= 0.20:
                score += 10
        else:
            if spread <= 0.10:
                score += 30
            elif spread <= 0.20:
                score += 20
            elif spread <= 0.50:
                score += 10
    
    return min(100, score)

if __name__ == "__main__":
    asyncio.run(analyze_iv_and_liquidity())
```
**Run:** `python3 iv_liquidity.py`
