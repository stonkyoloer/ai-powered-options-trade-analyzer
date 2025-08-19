**Create:** `touch options_chains.py`

**Query:** `open -e options_chains.py`

```bash
import json
from datetime import datetime
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

def get_options_contracts():
    print("🎰 STEP 2: Finding Options Contracts")
    print("=" * 50)
    print("🔍 Looking for all the different bets we can make...")
    
    # Load our stock prices from Step 1
    with open('step1_stock_prices.json', 'r') as f:
        step1_data = json.load(f)
    
    companies = list(step1_data['stock_prices'].keys())
    session = Session(USERNAME, PASSWORD)
    
    all_options = {}
    total_contracts = 0
    
    for company in companies:
        print(f"\n🏢 Looking at {company} options...")
        
        try:
            # Get all the different expiration dates for this company
            option_chain = get_option_chain(session, company)
            
            if not option_chain:
                print(f"   ❌ No options found for {company}")
                continue
            
            print(f"   📅 Found {len(option_chain)} different expiration dates!")
            
            company_options = {
                'company': company,
                'current_stock_price': step1_data['stock_prices'][company]['current_price'],
                'expiration_dates': {},
                'total_contracts': 0
            }
            
            # Look at the first 4 expiration dates (nearest ones)
            exp_dates = sorted(option_chain.keys())[:4]
            
            for exp_date in exp_dates:
                options_list = option_chain[exp_date]
                exp_date_str = str(exp_date)
                
                print(f"   📋 {exp_date_str}: Found {len(options_list)} contracts")
                
                contracts = []
                calls = 0
                puts = 0
                
                for option in options_list:
                    if option.days_to_expiration <= 45:  # Only contracts expiring soon
                        contract_info = {
                            'contract_name': option.symbol,
                            'strike_price': float(option.strike_price),
                            'days_until_expires': option.days_to_expiration,
                            'contract_type': 'CALL' if option.option_type.value == 'C' else 'PUT',
                            'streamer_symbol': option.streamer_symbol
                        }
                        contracts.append(contract_info)
                        
                        if option.option_type.value == 'C':
                            calls += 1
                        else:
                            puts += 1
                
                company_options['expiration_dates'][exp_date_str] = {
                    'date': exp_date_str,
                    'total_contracts': len(contracts),
                    'calls': calls,
                    'puts': puts,
                    'contracts': contracts
                }
                
                company_options['total_contracts'] += len(contracts)
                total_contracts += len(contracts)
                
                print(f"      ✅ {calls} CALLS (bet stock goes UP)")
                print(f"      ✅ {puts} PUTS (bet stock goes DOWN)")
            
            all_options[company] = company_options
            print(f"   🎯 Total for {company}: {company_options['total_contracts']} contracts")
            
        except Exception as e:
            print(f"   ❌ Error with {company}: {e}")
    
    # Save our results
    result = {
        'step': 2,
        'what_we_did': 'Found all options contracts for each company',
        'timestamp': datetime.now().isoformat(),
        'companies_analyzed': len(all_options),
        'total_contracts_found': total_contracts,
        'options_by_company': all_options
    }
    
    filename = 'step2_options_contracts.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved options data to: {filename}")
    print(f"🎰 Found {total_contracts} total contracts to analyze!")
    return result

if __name__ == "__main__":
    get_options_contracts()
```

**Run:** `python3 options_chains.py`
