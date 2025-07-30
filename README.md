# 📈 StonkYoloer Portfolio & Daily Trade Screener

I am now AI, start with $400, ChatGPT vs Grok, I will do whatever they say.  I am not responsible for my actions.  No DD.  No Brains.  JUST VIBES!  

---


# 1️⃣  Portfolio Construction

## 👨‍💻 Get Data

**Source**: Stocks are Nasdaq-100 constituents or related, aligned with [Nasdaq-100 Index](https://www.nasdaq.com/market-activity/quotes/nasdaq-ndx-index)

---
## ✍️ Prompt 
### Attachment
- us_tickers.csv
---
### Instructions 

**Goal**  
Construct a 9-ticker, sector-diversified options portfolio emphasizing:  
- **High Implied Volatility (IV)** (rich premiums & IV Rank ≥ 30%)  
- **Deep Liquidity** (OI ≥ 1,000 per leg; spreads ≤ $0.05 for top names, ≤ $0.10 for moderately liquid)  
- **Strong Short-Term Swings** (same-day to 30 days)  
- **Industry-Leading AI Exposure** in each sector  
- **Significant Market Attention** (institutional/retail hype)  

**Selection Criteria (ALL must be met)**  
1. **AI Leadership**: Core business or initiative is AI-driven.  
2. **Options Liquidity**: Weekly/monthly chains, ≥ 1,000 OI on each leg, tight spreads.  
3. **Elevated IV + IV Rank ≥ 30%**: Ensure options are richly priced relative to their history.  
4. **Public Buzz**: Recent catalysts, heavy newsflow, or social/institutional interest.  
5. **Robinhood-Available**: U.S.-listed and accessible to retail traders.  

**Technical & Risk Filters**  
- **Primary Signal (RSI(5))**: Confirm short-term momentum (oversold/overbought swings).  
- **Secondary Signal (MACD Crossover)**: Validate momentum for directional plays (debit spreads, straddles).  

**Rebalance Triggers**  
- **IV Rank < 30%** → remove/replace  
- **Stop-Loss Hit** → exit and free capital  
- **Profit Target Hit** → lock in gains  
- **Rebalance Cadence**: Event-driven only (no routine weekly unless a trigger fires)  

**Portfolio Construction**  
Select exactly one ticker per sector (no duplicates), drawn from the NASDAQ,  include any high-IV recent IPOs or AI spin-outs that meet all criteria.
---
### Prompt
**Goal**
1. Refer to the Goal, Selection Criteria, Filters, and Construction above.  
2. Use the attachments as your candidate universe.  
3. Be resourceful—pull live or most recent data (IV%, IV Rank, OI, spreads, RSI(5), MACD) from public APIs or data feeds.  
4. Exclude all tickers not traded on Robinhood.  

**Task**  
- Shortlist all holdings by sector.  
- Filter by AI exposure, liquidity, IV & IVR ≥ 30%, OI ≥ 1,000, spread ≤ $0.05/0.10, and RSI+MACD confirmation.  
- Select the single best ticker per sector.  
- Output a markdown table with columns:  
  `| Ticker | Sector | AI Leadership Summary | Avg IV % | IV Rank | RSI(5) | MACD Signal | Daily Volume | Liquidity Grade |`  
  - Liquidity Grade: A (ideal), B (acceptable), C (avoid).  
- Explain any sector where no perfect match exists by proposing the next best alternative and rationale.  
- Include rebalancing triggers and signal filters in your commentary block below the table.  
---

# 2️⃣ Setup & Install Tasty Trade API

## 🛠 Create a Project

**Create:** `mkdir tastytrade_data`

**Open:** `cd tastytrade_data`

**Install:** `pip install tastytrade websockets pandas httpx certifi`

  - `tastytrade`: Lets the project talk to the Tastytrade website to get data.
  - `websockets`: Helps get live updates on the Greeks.
  - `pandas`: Handles and calculates with the data.
  - `httpx` and `certifi`: Make secure connections to the internet.


## 🔐 Test Tastytrade Login


**Create:** `touch test_connection.py`

**Query:** `open -e test_connection.py`

```python
import requests
import json

# Test basic connection to TastyTrade
print("Testing TastyTrade API connection...")

url = "https://api.tastytrade.com/sessions"
print(f"API URL: {url}")
print("Ready for authentication test")
```
**Run:** `python3 test_connection.py`


## 🔑 Authenticate & Get Account Info

**Create:** touch auth_test.py
**Query:** open -e auth_test.py

```python
import requests
import json

# Your TastyTrade credentials
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

# Test authentication
url = "https://api.tastytrade.com/sessions"
data = {
    "login": USERNAME,
    "password": PASSWORD
}

print("Attempting to authenticate...")
response = requests.post(url, json=data)
print(f"Status code: {response.status_code}")

if response.status_code == 201:
    print("SUCCESS: Authentication worked!")
    result = response.json()
    print("Session token received")
else:
    print("FAILED: Authentication failed")
    print(f"Error: {response.text}")
```

**Run:** `python3 auth_test.py`


# 3️⃣ Build Data Tables


## 📁 Step 1: Get Stock Prices

**Create:** `touch stock_prices.py`

**Query:** `open -e stock_prices.py`

```bash
# Step 1: Get Stock Prices - Like checking price tags!
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

# Our 9 favorite companies to trade
COMPANIES = [
    'NVDA',  # NVIDIA (makes computer chips)
    'TSLA',  # Tesla (electric cars)
    'AMZN',  # Amazon (online shopping)
    'ISRG',  # Intuitive Surgical (robot surgery)
    'PLTR',  # Palantir (data analysis)
    'ENPH',  # Enphase Energy (solar power)
    'XOM',   # Exxon Mobil (oil company)
    'DE',    # John Deere (farm equipment)
    'CAT'    # Caterpillar (construction equipment)
]

async def get_stock_prices():
    print("🏪 STEP 1: Getting Stock Prices")
    print("=" * 50)
    print("📋 Checking prices for our 9 favorite companies...")
    
    session = Session(USERNAME, PASSWORD)
    stock_prices = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to the stock market...")
        await streamer.subscribe(Quote, COMPANIES)
        print("✅ Connected! Now listening for prices...")
        
        collected = set()
        start_time = asyncio.get_event_loop().time()
        
        while len(collected) < len(COMPANIES) and (asyncio.get_event_loop().time() - start_time) < 30:
            try:
                quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=5.0)
                
                if quote and quote.event_symbol in COMPANIES and quote.event_symbol not in collected:
                    company = quote.event_symbol
                    price = float((quote.bid_price + quote.ask_price) / 2)
                    
                    stock_prices[company] = {
                        'company_name': company,
                        'current_price': price,
                        'buy_price': float(quote.bid_price),
                        'sell_price': float(quote.ask_price),
                        'when_checked': datetime.now().isoformat()
                    }
                    
                    collected.add(company)
                    print(f"   💰 {company}: ${price:.2f}")
                    
            except asyncio.TimeoutError:
                continue
    
    # Save our results
    result = {
        'step': 1,
        'what_we_did': 'Got current stock prices',
        'timestamp': datetime.now().isoformat(),
        'companies_checked': len(stock_prices),
        'stock_prices': stock_prices
    }
    
    filename = 'step1_stock_prices.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved stock prices to: {filename}")
    print(f"📊 Found prices for {len(stock_prices)} companies!")
    return result

if __name__ == "__main__":
    asyncio.run(get_stock_prices())
```

**Run:** `python3 stock_prices.py`


---


## 📁 Step 2: Get All Options Contracts

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

---

## 📁 Step 3: Check How Risky Each Trade Is (Greeks)

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

---

## 📁 Step 4: Get Buy/Sell Prices (Bid/Ask)

**Create:** `touch market_prices.py`

**Query:** `open -e market_prices.py`

```bash
import asyncio
import json
from datetime import datetime
from decimal import Decimal
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def safe_float_convert(value):
    """Safely convert any numeric value to float"""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

async def get_market_prices():
    print("💰 STEP 4: Getting Market Prices")
    print("=" * 50)
    print("🏪 Finding out what people will actually pay vs. sell for...")
    
    # Load our contracts from Step 2
    with open('step2_options_contracts.json', 'r') as f:
        step2_data = json.load(f)
    
    # Collect all contract symbols
    all_contracts = []
    for company_data in step2_data['options_by_company'].values():
        for exp_data in company_data['expiration_dates'].values():
            for contract in exp_data['contracts']:
                all_contracts.append(contract['streamer_symbol'])
    
    print(f"🎯 Getting prices for {len(all_contracts)} contracts...")
    
    session = Session(USERNAME, PASSWORD)
    market_prices = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to get market prices...")
        await streamer.subscribe(Quote, all_contracts)
        print("✅ Connected! Getting buy/sell prices...")
        
        collected_quotes = []
        start_time = asyncio.get_event_loop().time()
        
        # Collect for 2 minutes
        while (asyncio.get_event_loop().time() - start_time) < 120:
            try:
                quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=3.0)
                
                if quote:
                    collected_quotes.append(quote)
                    
                    # Show progress every 100 quotes
                    if len(collected_quotes) % 100 == 0:
                        print(f"   💰 Prices collected: {len(collected_quotes)}")
                        
            except asyncio.TimeoutError:
                continue
        
        print(f"✅ Collected {len(collected_quotes)} market prices!")
        
        # Process quotes with proper decimal handling
        for quote in collected_quotes:
            # Safely convert all numeric values to float
            buy_price = safe_float_convert(quote.bid_price)
            sell_price = safe_float_convert(quote.ask_price)
            bid_size = safe_float_convert(getattr(quote, 'bid_size', 0))
            ask_size = safe_float_convert(getattr(quote, 'ask_size', 0))
            
            if buy_price > 0 and sell_price > 0:
                market_prices[quote.event_symbol] = {
                    'contract_name': quote.event_symbol,
                    'what_buyers_pay': buy_price,      # Bid price
                    'what_sellers_want': sell_price,   # Ask price
                    'fair_price': (buy_price + sell_price) / 2,  # Middle price
                    'price_difference': sell_price - buy_price,  # Spread
                    'buyers_willing': bid_size,
                    'sellers_available': ask_size
                }
    
    # Organize by company
    companies = ['NVDA', 'TSLA', 'AMZN', 'ISRG', 'PLTR', 'ENPH', 'XOM', 'DE', 'CAT']
    prices_by_company = {}
    
    for company in companies:
        prices_by_company[company] = []
        
    for symbol, price_data in market_prices.items():
        for company in companies:
            if company in symbol:
                prices_by_company[company].append(price_data)
                break
    
    # Save our results with decimal handling
    result = {
        'step': 4,
        'what_we_did': 'Got buy/sell prices for all options',
        'timestamp': datetime.now().isoformat(),
        'total_prices_collected': len(market_prices),
        'companies_with_prices': len([c for c in prices_by_company.values() if c]),
        'prices_by_company': prices_by_company,
        'price_explanations': {
            'what_buyers_pay': 'The highest price someone will pay (BID)',
            'what_sellers_want': 'The lowest price someone will sell for (ASK)',
            'fair_price': 'The middle price between buy and sell',
            'price_difference': 'The gap between buy and sell prices (SPREAD)'
        }
    }
    
    filename = 'step4_market_prices.json'
    
    # Use custom JSON encoder to handle any remaining Decimal objects
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super(DecimalEncoder, self).default(obj)
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2, cls=DecimalEncoder)
    
    print(f"\n✅ Saved market prices to: {filename}")
    print(f"💰 Got prices for {len(market_prices)} contracts!")
    
    # Show some examples
    print(f"\n💰 PRICE EXAMPLES:")
    sample_prices = list(market_prices.items())[:5]
    for symbol, price_data in sample_prices:
        buy = price_data['what_buyers_pay']
        sell = price_data['what_sellers_want']
        diff = price_data['price_difference']
        print(f"   {symbol[-10:]:10}: Buy=${buy:.2f}, Sell=${sell:.2f}, Gap=${diff:.3f}")
    
    return result

if __name__ == "__main__":
    asyncio.run(get_market_prices())
```

**Run:** `python3 market_prices.py`

---

# 

## 📁 Step 5: Find the Best Credit Spreads

**Create:** `touch find_tendies.py`

**Query:** `open -e find_tendies.py`

```bash
import json
import pandas as pd
import numpy as np
from datetime import datetime
import math
from scipy.stats import norm

class BlackScholesCalculator:
    """Black-Scholes option pricing and probability calculations"""
    
    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate
    
    def black_scholes_call(self, S, K, T, r, sigma):
        """Calculate Black-Scholes call option price"""
        if T <= 0:
            return max(S - K, 0)
        
        if sigma <= 0:
            return max(S - K, 0)
            
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return max(call_price, 0)
    
    def probability_otm(self, S, K, T, sigma, option_type='call'):
        """Calculate probability that option expires out-of-the-money"""
        if T <= 0:
            return 1.0 if (option_type == 'call' and S < K) or (option_type == 'put' and S > K) else 0.0
        
        if sigma <= 0:
            return 1.0 if (option_type == 'call' and S < K) or (option_type == 'put' and S > K) else 0.0
        
        d2 = (np.log(S / K) + (self.risk_free_rate - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        if option_type == 'call':
            prob_otm = norm.cdf(-d2)
        else:
            prob_otm = norm.cdf(d2)
        
        return prob_otm
    
    def calculate_greeks(self, S, K, T, r, sigma, option_type='call'):
        """Calculate option Greeks"""
        if T <= 0:
            return {'delta': 0, 'theta': 0, 'gamma': 0, 'vega': 0}
        
        if sigma <= 0:
            return {'delta': 0, 'theta': 0, 'gamma': 0, 'vega': 0}
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        else:
            delta = -norm.cdf(-d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        
        return {
            'delta': delta,
            'theta': theta,
            'gamma': gamma,
            'vega': vega
        }

def find_deals_with_delta_analysis():
    print("🔍 BLACK-SCHOLES WITH DELTA ANALYSIS")
    print("=" * 70)
    print("🎯 ROI > 10%, PoP > 66%, Delta Analysis...")
    
    # Load all data
    with open('step1_stock_prices.json', 'r') as f:
        stock_data = json.load(f)
    
    with open('step2_options_contracts.json', 'r') as f:
        options_data = json.load(f)
    
    with open('step3_risk_analysis.json', 'r') as f:
        risk_data = json.load(f)
    
    with open('step4_market_prices.json', 'r') as f:
        price_data = json.load(f)
    
    print("✅ Loaded all data!")
    
    bs_calc = BlackScholesCalculator()
    
    # Create lookups
    greek_lookup = {}
    for company, greeks_list in risk_data['risk_by_company'].items():
        for greek in greeks_list:
            greek_lookup[greek['contract_name']] = greek
    
    price_lookup = {}
    for company, prices_list in price_data['prices_by_company'].items():
        for price in prices_list:
            price_lookup[price['contract_name']] = price
    
    all_spreads_no_delta = []  # No delta filter
    all_spreads_loose_delta = []  # Loose delta filter
    all_spreads_strict_delta = []  # Strict delta filter
    
    delta_stats = {
        'deltas_seen': [],
        'negative_deltas': 0,
        'neutral_deltas': 0,  # -0.2 to +0.2
        'positive_deltas': 0
    }
    
    for company, company_options in options_data['options_by_company'].items():
        current_stock_price = company_options['current_stock_price']
        
        print(f"\n🏢 {company} (${current_stock_price:.2f})...")
        
        for exp_date, exp_data in company_options['expiration_dates'].items():
            contracts = exp_data['contracts']
            calls = [c for c in contracts if c['contract_type'] == 'CALL']
            calls_above_price = [c for c in calls if c['strike_price'] > current_stock_price]
            calls_above_price.sort(key=lambda x: x['strike_price'])
            
            for i in range(len(calls_above_price) - 1):
                short_call = calls_above_price[i]
                long_call = calls_above_price[i + 1]
                
                if long_call['strike_price'] - short_call['strike_price'] > 5:
                    continue
                
                short_symbol = short_call['streamer_symbol']
                long_symbol = long_call['streamer_symbol']
                
                if (short_symbol not in price_lookup or long_symbol not in price_lookup or
                    short_symbol not in greek_lookup or long_symbol not in greek_lookup):
                    continue
                
                short_price_data = price_lookup[short_symbol]
                long_price_data = price_lookup[long_symbol]
                short_greek_data = greek_lookup[short_symbol]
                long_greek_data = greek_lookup[long_symbol]
                
                # Get data
                short_iv = short_greek_data['implied_volatility']
                long_iv = long_greek_data['implied_volatility']
                avg_iv = (short_iv + long_iv) / 2
                
                days_to_exp = short_call['days_until_expires']
                time_to_exp = days_to_exp / 365.0
                
                if time_to_exp <= 0:
                    continue
                
                # Calculate market credit
                short_bid = short_price_data['what_buyers_pay']
                long_ask = long_price_data['what_sellers_want']
                
                if short_bid <= 0 or long_ask <= 0:
                    continue
                
                market_credit = short_bid - long_ask
                
                if market_credit <= 0:
                    continue
                
                # Black-Scholes probability
                prob_profit_bs = bs_calc.probability_otm(
                    current_stock_price, short_call['strike_price'], 
                    time_to_exp, avg_iv, 'call'
                ) * 100
                
                # Calculate metrics
                strike_width = long_call['strike_price'] - short_call['strike_price']
                max_risk = strike_width - market_credit
                roi_percent = (market_credit / max_risk) * 100 if max_risk > 0 else 0
                
                # Calculate Greeks
                short_greeks = bs_calc.calculate_greeks(
                    current_stock_price, short_call['strike_price'], 
                    time_to_exp, bs_calc.risk_free_rate, short_iv, 'call'
                )
                long_greeks = bs_calc.calculate_greeks(
                    current_stock_price, long_call['strike_price'], 
                    time_to_exp, bs_calc.risk_free_rate, long_iv, 'call'
                )
                
                spread_delta = short_greeks['delta'] - long_greeks['delta']
                spread_theta = short_greeks['theta'] - long_greeks['theta']
                
                # Track delta statistics
                delta_stats['deltas_seen'].append(spread_delta)
                if spread_delta < -0.1:
                    delta_stats['negative_deltas'] += 1
                elif -0.2 <= spread_delta <= 0.2:
                    delta_stats['neutral_deltas'] += 1
                else:
                    delta_stats['positive_deltas'] += 1
                
                # Basic filters first
                if roi_percent <= 10 or prob_profit_bs <= 66:
                    continue
                
                spread = {
                    'company': company,
                    'short_strike': short_call['strike_price'],
                    'long_strike': long_call['strike_price'],
                    'days_to_expiration': days_to_exp,
                    'credit_collected': market_credit,
                    'max_risk': max_risk,
                    'roi_percent': roi_percent,
                    'probability_of_profit': prob_profit_bs,
                    'current_stock_price': current_stock_price,
                    'avg_implied_volatility': avg_iv,
                    'spread_delta': spread_delta,
                    'spread_theta': spread_theta,
                    'explanation': f"Collect ${market_credit:.2f}, {prob_profit_bs:.1f}% PoP if {company} stays below ${short_call['strike_price']:.0f}",
                    'delta_interpretation': 'Neutral' if abs(spread_delta) <= 0.2 else ('Bullish' if spread_delta > 0.2 else 'Bearish')
                }
                
                # Add to no-delta list (already passed ROI/PoP filters)
                all_spreads_no_delta.append(spread)
                
                # Add to loose delta list (delta between -0.5 and +0.5)
                if -0.5 <= spread_delta <= 0.5:
                    all_spreads_loose_delta.append(spread)
                
                # Add to strict delta list (delta between -0.2 and +0.2)
                if -0.2 <= spread_delta <= 0.2:
                    all_spreads_strict_delta.append(spread)
    
    # Sort all lists by probability
    all_spreads_no_delta.sort(key=lambda x: x['probability_of_profit'], reverse=True)
    all_spreads_loose_delta.sort(key=lambda x: x['probability_of_profit'], reverse=True)
    all_spreads_strict_delta.sort(key=lambda x: x['probability_of_profit'], reverse=True)
    
    print(f"\n📊 DELTA ANALYSIS RESULTS:")
    print(f"   Deltas seen: min={min(delta_stats['deltas_seen']):.3f}, max={max(delta_stats['deltas_seen']):.3f}")
    print(f"   Negative deltas (<-0.1): {delta_stats['negative_deltas']}")
    print(f"   Neutral deltas (-0.2 to +0.2): {delta_stats['neutral_deltas']}")
    print(f"   Positive deltas (>+0.2): {delta_stats['positive_deltas']}")
    
    print(f"\n🎯 FILTER COMPARISON (ROI>10%, PoP>66%):")
    print(f"   ✅ NO Delta Filter: {len(all_spreads_no_delta)} opportunities")
    print(f"   📊 LOOSE Delta Filter (±0.5): {len(all_spreads_loose_delta)} opportunities")
    print(f"   🎯 STRICT Delta Filter (±0.2): {len(all_spreads_strict_delta)} opportunities")
    
    # Show top 10 from each category
    print(f"\n🏆 TOP 10 - NO DELTA FILTER:")
    print("-" * 100)
    for i, spread in enumerate(all_spreads_no_delta[:10]):
        delta_color = "🟢" if abs(spread['spread_delta']) <= 0.2 else ("🟡" if abs(spread['spread_delta']) <= 0.5 else "🔴")
        print(f"{i+1:2}. {spread['company']:4} | "
              f"PoP: {spread['probability_of_profit']:5.1f}% | "
              f"ROI: {spread['roi_percent']:5.1f}% | "
              f"Δ: {spread['spread_delta']:6.3f} {delta_color} | "
              f"Credit: ${spread['credit_collected']:.2f}")
    
    print(f"\n🎯 TOP 10 - WITH LOOSE DELTA FILTER (±0.5):")
    print("-" * 100)
    for i, spread in enumerate(all_spreads_loose_delta[:10]):
        print(f"{i+1:2}. {spread['company']:4} | "
              f"PoP: {spread['probability_of_profit']:5.1f}% | "
              f"ROI: {spread['roi_percent']:5.1f}% | "
              f"Δ: {spread['spread_delta']:6.3f} | "
              f"Credit: ${spread['credit_collected']:.2f}")
    
    if all_spreads_strict_delta:
        print(f"\n🎯 TOP 10 - WITH STRICT DELTA FILTER (±0.2):")
        print("-" * 100)
        for i, spread in enumerate(all_spreads_strict_delta[:10]):
            print(f"{i+1:2}. {spread['company']:4} | "
                  f"PoP: {spread['probability_of_profit']:5.1f}% | "
                  f"ROI: {spread['roi_percent']:5.1f}% | "
                  f"Δ: {spread['spread_delta']:6.3f} | "
                  f"Credit: ${spread['credit_collected']:.2f}")
    else:
        print(f"\n❌ NO TRADES passed strict delta filter (±0.2)")
    
    # Save the no-delta version as the main result
    result = {
        'step': 5,
        'filters_used': 'ROI > 10%, PoP > 66%, NO delta filter',
        'total_opportunities': len(all_spreads_no_delta),
        'delta_analysis': {
            'no_delta_filter': len(all_spreads_no_delta),
            'loose_delta_filter': len(all_spreads_loose_delta),
            'strict_delta_filter': len(all_spreads_strict_delta)
        },
        'best_deals': all_spreads_no_delta[:25],
        'timestamp': datetime.now().isoformat()
    }
    
    filename = 'step5_delta_analysis.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved analysis to: {filename}")
    
    return result

if __name__ == "__main__":
    find_deals_with_delta_analysis()
```

**Run:** `python3 find_tendies.py`

---

## 📁 Step 6: The Master Script

**Create:** `touch master.py`

**Query:** `open -e master.py`


```bash
import asyncio
import subprocess
import os
from datetime import datetime

async def run_complete_analysis():
    print("🤖 MASTER TRADING ROBOT")
    print("=" * 80)
    print("🚀 Running complete analysis in 5 steps...")
    print("⏰ This will take about 5-7 minutes total")
    print("=" * 80)
    
    steps = [
        ("stock_prices.py", "Getting stock prices"),
        ("options_chains.py", "Finding options contracts"), 
        ("risk_analysis.py", "Analyzing risk"),
        ("market_prices.py", "Getting market prices"),
        ("find_tendies.py", "Finding best deals")
    ]
    
    start_time = datetime.now()
    
    for i, (script, description) in enumerate(steps, 1):
        print(f"\n🎯 STEP {i}/5: {description}")
        print(f"🏃‍♂️ Running {script}...")
        
        try:
            # Run the script and wait for it to finish
            result = subprocess.run(['python3', script], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                print(f"   ✅ Step {i} completed successfully!")
                # Print some of the output so we can see progress
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-3:]:  # Show last 3 lines
                        print(f"      {line}")
            else:
                print(f"   ❌ Step {i} failed!")
                print(f"   Error: {result.stderr}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Step {i} took too long (over 5 minutes)")
            return False
        except Exception as e:
            print(f"   ❌ Error running step {i}: {e}")
            return False
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print(f"\n🎉 ALL STEPS COMPLETED!")
    print("=" * 80)
    print(f"⏰ Total time: {total_time/60:.1f} minutes")
    print(f"📁 Files created:")
    print(f"   📊 step1_stock_prices.json")
    print(f"   🎰 step2_options_contracts.json") 
    print(f"   🧮 step3_risk_analysis.json")
    print(f"   💰 step4_market_prices.json")
    print(f"   🏆 step5_best_deals.json")
    print(f"   📈 best_credit_spreads.csv")
    
    # Show final summary
    try:
        import json
        with open('step5_best_deals.json', 'r') as f:
            final_data = json.load(f)
        
        print(f"\n🏆 FINAL RESULTS:")
        print(f"   💡 Found {final_data['total_opportunities_found']} good trading opportunities!")
        
        if final_data['best_deals']:
            best_deal = final_data['best_deals'][0]
            print(f"   🥇 BEST DEAL: {best_deal['company']} - {best_deal['roi_percent']:.1f}% ROI")
            print(f"      {best_deal['explanation']}")
    
    except Exception as e:
        print(f"   ⚠️ Could not load final summary: {e}")

    return True

if __name__ == "__main__":
    # This is what was missing - actually run the async function!
    asyncio.run(run_complete_analysis())
```

**Run:** `python3 master.py`

---

## 🎯 Key Learning Points

### **Why Each Step Matters:**
1. **Stock Prices:** "You can't make smart bets without knowing the current score!"
2. **Options Contracts:** "We need to see ALL our choices before picking the best one!"
3. **Risk Analysis:** "Smart traders always check 'how dangerous is this?' first!"
4. **Market Prices:** "No point finding a great trade if nobody will buy/sell at good prices!"
5. **Best Deals:** "All the detective work pays off when we find the treasure!"

### **Real-World Analogies:**
- **Stock Market = Giant Mall** with different stores (companies)
- **Options = Carnival Games** where you bet on outcomes
- **Greeks = Report Cards** that grade each trade
- **Bid/Ask = Flea Market** haggling over prices
- **Credit Spreads = Smart Bets** where you collect money upfront

### **What Just Happened:**
- "We collected data on 5,560 different trades!"
- "Our robot can do in 6 minutes what takes humans hours!"
- "We found trades with 98% win rates!"
- "The computer is like having a super-smart friend who never gets tired!"

---

## 📁 File Structure Summary
📂 Trading Robot Project/
├── 📄 config.py (your login info)
├── 🤖 stock_prices.py
├── 📊 stock_prices.json
├── 🤖 options_chains.py
├── 📊 options_contracts.json
├── 🤖 risk_analysis.py
├── 📊 risk_analysis.json
├── 🤖 market_prices.py
├── 📊 market_prices.json
├── 🤖 find_tendies.py
├── 📊 best_deals.json
├── 📈 credit_spreads.csv
└── 🤖 master.py

**Total Runtime:** ~6 minutes for complete analysis
**Total Files Created:** 6 Python scripts + 6 data files
**Total Data Points:** 5,560+ options analyzed
**End Result:** Ranked list of best trading opportunities!

---

# 6️⃣ Prompt AI

## 🗂 Attachment
cs_picker.py

---

## 👨‍🏫 Instructions 
**Goal** Validate the **3 selected trades** from the AI‑optimized portfolio for execution readiness, including **macro/news risk checks, sector exposure sanity, and portfolio Greek balance**. Provide a final confidence check before trading.  

#### Data Inputs  
- **Trade Candidates:** 3 top‑scored option trades (from previous prompt)  
- **Market Data:** POP, Credit/Max‑Loss, DTE, Strategy, Thesis (from attached table)  
- **Macro Context:** Key upcoming earnings, Fed events, geopolitical risks, sector catalysts  

#### Validation Criteria  
1. **Confirm Trade Quality:** POP ≥ 0.66, Credit/Max‑Loss ≥ 0.33, DTE within strategy target bucket.  
2. **Portfolio Exposure:** No sector > 2 trades, Net Delta roughly balanced (∈ [–0.30,+0.30] × NAV/100k), Net Vega ≥ –0.05 × NAV/100k.  
3. **Catalyst Scan:** Flag upcoming earnings, Fed/geo headlines, or sector news that could affect volatility or invalidate thesis.  
4. **Sentiment & Flow Check:** Consider social sentiment, institutional flow, and analyst rating consensus.  
5. **Event Risk Tag:** Identify any ticker with a near‑term risk event (earnings, product launch, regulatory ruling).  

#### Output Table Schema  
| Ticker | Strategy | Legs | Thesis (≤ 30 words) | POP | Credit/Max‑Loss | DTE | Sector | Risk/Event Note | Confidence |  

---

## 🤖 Prompt  
Apply **the Instructions** to the attached data.  
1. **Output only** the clean, markdown‑wrapped table with columns:  
`Ticker, Strategy, Legs, Thesis (≤ 30 words), POP, Credit/Max‑Loss, DTE, Sector, Risk/Event Note, Confidence`  
   - **Risk/Event Note:** Short bullet (e.g. “Earnings in 5d”, “Fed risk”, “Sector upgrade momentum”).  
   - **Confidence:** High / Medium / Low based on combined signals.  
2. **Then add a brief commentary block** summarizing:  
   - Why these trades remain valid under current macro/news context  
   - Any portfolio risk adjustments needed (e.g., sector overweight, delta/vega imbalance)  
   - Key external catalysts to monitor before entry.  

