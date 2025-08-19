**Create:** `touch risk_analysis.py`

**Query:** `open -e risk_analysis.py`

```bash
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from config import USERNAME, PASSWORD

async def analyze_risk():
    print("🧮 STEP 3: Risk Analysis (Greeks)")
    print("=" * 50)
    print("🔬 Using special math to check how risky each bet is...")
    
    # Load our options from Step 2
    with open('step2_options_contracts.json', 'r') as f:
        step2_data = json.load(f)
    
    # Collect all contract symbols we need to analyze
    all_contracts = []
    for company_data in step2_data['options_by_company'].values():
        for exp_data in company_data['expiration_dates'].values():
            for contract in exp_data['contracts']:
                all_contracts.append(contract['streamer_symbol'])
    
    print(f"🎯 Analyzing risk for {len(all_contracts)} contracts...")
    
    session = Session(USERNAME, PASSWORD)
    risk_data = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to get risk calculations...")
        await streamer.subscribe(Greeks, all_contracts)
        print("✅ Connected! Getting risk data...")
        
        collected_greeks = []
        start_time = asyncio.get_event_loop().time()
        
        # Collect for 2 minutes to get all data
        while (asyncio.get_event_loop().time() - start_time) < 120:
            try:
                greek_data = await asyncio.wait_for(streamer.get_event(Greeks), timeout=3.0)
                
                if greek_data:
                    collected_greeks.append(greek_data)
                    
                    # Show progress every 100 items
                    if len(collected_greeks) % 100 == 0:
                        print(f"   📊 Risk calculations done: {len(collected_greeks)}")
                        
            except asyncio.TimeoutError:
                continue
        
        print(f"✅ Completed {len(collected_greeks)} risk calculations!")
        
        # Organize risk data by company
        companies = ['NVDA', 'TSLA', 'AMZN', 'ISRG', 'PLTR', 'ENPH', 'XOM', 'DE', 'CAT']
        
        for greek in collected_greeks:
            # Figure out which company this belongs to
            company = None
            for comp in companies:
                if comp in greek.event_symbol:
                    company = comp
                    break
            
            if company:
                if company not in risk_data:
                    risk_data[company] = []
                
                # Save the risk information in simple terms
                risk_info = {
                    'contract_name': greek.event_symbol,
                    'current_option_price': float(greek.price),
                    'delta': float(greek.delta),  # How much price changes when stock moves $1
                    'theta': float(greek.theta),  # How much we lose each day (time decay)
                    'gamma': float(greek.gamma),  # How much delta changes
                    'vega': float(greek.vega),   # How much price changes with volatility
                    'implied_volatility': float(greek.volatility)  # How "jumpy" people think stock will be
                }
                
                risk_data[company].append(risk_info)
    
    # Save our results
    result = {
        'step': 3,
        'what_we_did': 'Calculated risk for all options using Greeks',
        'timestamp': datetime.now().isoformat(),
        'total_risk_calculations': len(collected_greeks),
        'companies_analyzed': len(risk_data),
        'risk_by_company': risk_data,
        'greek_explanations': {
            'delta': 'How much option price changes when stock moves $1',
            'theta': 'How much money we lose each day (time decay)',
            'gamma': 'How much delta speeds up or slows down',
            'vega': 'How much price changes if volatility changes',
            'implied_volatility': 'How jumpy people think the stock will be'
        }
    }
    
    filename = 'step3_risk_analysis.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved risk analysis to: {filename}")
    print(f"🧮 Calculated risk for {len(collected_greeks)} contracts!")
    
    # Show some examples
    print(f"\n📊 RISK EXAMPLES:")
    for company, risks in list(risk_data.items())[:3]:
        if risks:
            example = risks[0]
            print(f"   {company}: Delta={example['delta']:.3f}, Theta={example['theta']:.3f}")
    
    return result

if __name__ == "__main__":
    asyncio.run(analyze_risk())
```

**Run:** `python3 risk_analysis.py`
