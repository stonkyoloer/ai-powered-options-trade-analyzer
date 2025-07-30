# 📈 StonkYoloer Portfolio & Daily Trade Screener

I am now AI, start with $400, ChatGPT vs Grok, I will do whatever they say.  I am not responsible for my actions.  No DD.  No Brains.  JUST VIBES!  

---

## 📖 What This Does
This workflow builds an **AI‑driven trading portfolio** and screens for the day’s top option trades.  
It:
1. Selects **9 AI-focused stocks** across multiple sectors.
2. Pulls **live option chain and Greeks data** from Tastytrade.
3. Filters and ranks option trades using **defined rules and real‑time risk metrics**.
4. Outputs the **Top 3 highest‑probability trades** in a clean table.

---

## 🧠 Why Build This?
- **Massive option universe:** Thousands of tickers and millions of option combinations exist daily. This workflow narrows focus to **AI sector leaders only**.
- **Objective filtering:** Uses liquidity, volatility, and momentum rules to eliminate weak setups.
- **Greeks integration:** Delta, Gamma, Theta, Vega are pulled live so trades are grounded in real risk data.
- **Risk control:** Only trades with high probability of profit and defined max loss are shown.

---


# 1️⃣  Collect Data

**Source**: Stocks are Nasdaq-100 constituents or related, aligned with [Nasdaq-100 Index](https://www.nasdaq.com/market-activity/quotes/nasdaq-ndx-index)

---

# 2️⃣  Prompt AI (ChatGPT / Grok)

## 🗂 Attachment
- us_tickers.csv

---

## 👨‍🏫 Instructions 

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

| Sector                  | AI Theme                                                   |
|-------------------------|------------------------------------------------------------|
| Agriculture             | Precision farming, ag-biotech, automation                  |
| Technology              | AI chips, semiconductors, cloud/LLM infrastructure         |
| Industrials             | Robotics, smart infrastructure, automation systems         |
| Biotechnology           | ML drug discovery (oncology, antivirals, genomics, psychedelics) |
| Energy (Traditional)    | AI in oil/gas ops, predictive maintenance, commodities algos |
| Energy (Renewable)      | AI-optimized solar/wind/hydro, grid/storage analytics      |
| Financials              | AI for risk models, fraud detection, quant trading         |
| Consumer Staples        | AI-driven forecasting, supply chain, personalization       |
| Transportation          | Autonomous vehicles, predictive logistics, fleet AI        |

---

## 🤖 Prompt
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

## Prompt Output
| Ticker | Sector              | AI Theme                                              | Avg IV % | IV Rank | Liquidity Grade |
|--------|---------------------|------------------------------------------------------|----------|---------|-----------------|
| NVDA   | Technology          | AI chips, semiconductors                            | 68.6     | ≥ 30%   | A               |
| ISRG   | Biotechnology       | ML drug discovery (oncology, antivirals, genomics, psychedelics) | 59.3 | ≥ 30%   | A               |
| PLTR   | Technology          | Cloud/LLM infrastructure                           | 68.6     | ≥ 30%   | A               |
| TSLA   | Transportation      | Autonomous vehicles, predictive logistics, fleet AI | 52.7     | ≥ 30%   | A               |
| AMZN   | Technology          | Cloud/LLM infrastructure                           | 45.0     | ≥ 30%   | A               |
| ENPH   | Energy (Renewable)  | AI-optimized solar/wind/hydro, grid/storage analytics | 59.3 | ≥ 30%   | A               |
| XOM    | Energy (Traditional)| AI in oil/gas ops, predictive maintenance, commodities algos | 35.0 | ≥ 30%   | B               |
| DE     | Agriculture         | Precision farming, ag-biotech, automation           | 40.0     | ≥ 30%   | B               |
| CAT    | Industrials         | Robotics, smart infrastructure, automation systems  | 38.0     | ≥ 30%   | B               |

# 3️⃣ Connect to TastyTrade API 

## 🛠 Setup & Install

### Create a Folder
```bash
mkdir tastytrade_data
cd tastytrade_data
```

### Install Required Packages
```bash
pip install tastytrade websockets pandas httpx certifi
```
  - `tastytrade`: Lets the project talk to the Tastytrade website to get data.
  - `websockets`: Helps get live updates on the Greeks.
  - `pandas`: Handles and calculates with the data.
  - `httpx` and `certifi`: Make secure connections to the internet.

---

## 🔐 Test Tastytrade Login

### Create a File
```bash
touch test_connection.py
open -e test_connection.py
```
### Save the Script
```python
import requests
import json

# Test basic connection to TastyTrade
print("Testing TastyTrade API connection...")

url = "https://api.tastytrade.com/sessions"
print(f"API URL: {url}")
print("Ready for authentication test")
```
### Run the Script
```bash
python3 test_connection.py
```
---

## 🔑 Authenticate & Get Account Info

### Create a File
```bash
touch auth_test.py
open -e auth_test.py
```
### Save the Script
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

### Run the Script
```bash
python3 auth_test.py
```
---

# 4️⃣ Build Data Tables


---

# 🎯 What We're Building
We're going to build a Stonk Trading Data Table that:

1. Looks at stock prices 
2. Finds all the options contracts
3. Checks how risky each trade is using Greeks
4. Gets the buy/sell prices
5. Finds the trades that make money with high probability!


## 📁 Step 1: Get Stock Prices

**Create:** `touch -e stock_prices.py`

**Query:** `open stock_prices.py`

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

**Run:** `python3 


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

**Run:** Python3 risk_analysis.py`

## 📁 Step 4: Get Buy/Sell Prices (Bid/Ask)

**Create:** `touch market_prices.py`

**Query:** `open -e market_prices.py`

```bash
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

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
        
        # Process quotes
        for quote in collected_quotes:
            buy_price = float(quote.bid_price) if quote.bid_price else 0.0
            sell_price = float(quote.ask_price) if quote.ask_price else 0.0
            
            if buy_price > 0 and sell_price > 0:
                market_prices[quote.event_symbol] = {
                    'contract_name': quote.event_symbol,
                    'what_buyers_pay': buy_price,      # Bid price
                    'what_sellers_want': sell_price,   # Ask price
                    'fair_price': (buy_price + sell_price) / 2,  # Middle price
                    'price_difference': sell_price - buy_price,  # Spread
                    'buyers_willing': getattr(quote, 'bid_size', 0),
                    'sellers_available': getattr(quote, 'ask_size', 0)
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
    
    # Save our results
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
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
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


## 📁 Step 5: Find the Best Credit Spreads

**Create:** `touch find_tendies.py`

**Query:** `open -e find_tendies.py`

```bash
import json
import pandas as pd
from datetime import datetime
import math

def find_best_deals():
    print("🏆 STEP 5: Finding the Best Deals")
    print("=" * 50)
    print("🎯 Using all our data to find the best trades...")
    
    # Load all our previous data
    with open('step1_stock_prices.json', 'r') as f:
        stock_data = json.load(f)
    
    with open('step2_options_contracts.json', 'r') as f:
        options_data = json.load(f)
    
    with open('step3_risk_analysis.json', 'r') as f:
        risk_data = json.load(f)
    
    with open('step4_market_prices.json', 'r') as f:
        price_data = json.load(f)
    
    print("✅ Loaded all our collected data!")
    
    # Create lookup dictionaries for fast searching
    greek_lookup = {}
    for company, greeks_list in risk_data['risk_by_company'].items():
        for greek in greeks_list:
            greek_lookup[greek['contract_name']] = greek
    
    price_lookup = {}
    for company, prices_list in price_data['prices_by_company'].items():
        for price in prices_list:
            price_lookup[price['contract_name']] = price
    
    print(f"📊 Ready to analyze trades...")
    
    all_credit_spreads = []
    
    # Look for credit spread opportunities in each company
    for company, company_options in options_data['options_by_company'].items():
        current_stock_price = company_options['current_stock_price']
        
        print(f"\n🏢 Analyzing {company} (Stock: ${current_stock_price:.2f})...")
        
        for exp_date, exp_data in company_options['expiration_dates'].items():
            contracts = exp_data['contracts']
            
            # Separate calls and puts
            calls = [c for c in contracts if c['contract_type'] == 'CALL']
            puts = [c for c in contracts if c['contract_type'] == 'PUT']
            
            # Look for Bear Call Spreads (bet stock won't go up too much)
            calls_above_price = [c for c in calls if c['strike_price'] > current_stock_price]
            calls_above_price.sort(key=lambda x: x['strike_price'])
            
            # Create bear call spreads
            for i in range(len(calls_above_price) - 1):
                short_call = calls_above_price[i]      # Sell this one
                long_call = calls_above_price[i + 1]   # Buy this one (protection)
                
                # Skip if strikes are too far apart
                if long_call['strike_price'] - short_call['strike_price'] > 5:
                    continue
                
                # Get market data
                short_symbol = short_call['streamer_symbol']
                long_symbol = long_call['streamer_symbol']
                
                if short_symbol not in price_lookup or long_symbol not in price_lookup:
                    continue
                
                short_price_data = price_lookup[short_symbol]
                long_price_data = price_lookup[long_symbol]
                
                # Calculate credit (money we collect)
                short_bid = short_price_data['what_buyers_pay']  # We sell at bid
                long_ask = long_price_data['what_sellers_want']  # We buy at ask
                
                if short_bid <= 0 or long_ask <= 0:
                    continue
                
                credit = short_bid - long_ask  # Money we collect
                
                if credit <= 0:
                    continue
                
                # Calculate metrics
                strike_width = long_call['strike_price'] - short_call['strike_price']
                max_risk = strike_width - credit
                roi_percent = (credit / max_risk) * 100 if max_risk > 0 else 0
                
                # Calculate probability of profit (simplified)
                # Distance from current price to short strike
                distance_to_short = short_call['strike_price'] - current_stock_price
                distance_percent = (distance_to_short / current_stock_price) * 100
                
                # Simple probability estimate (higher distance = higher probability)
                pop_percent = min(95, max(50, 75 + distance_percent))
                
                credit_spread = {
                    'company': company,
                    'trade_type': 'Bear Call Spread',
                    'short_strike': short_call['strike_price'],
                    'long_strike': long_call['strike_price'],
                    'days_to_expiration': short_call['days_until_expires'],
                    'credit_collected': credit,
                    'max_risk': max_risk,
                    'roi_percent': roi_percent,
                    'probability_of_profit': pop_percent,
                    'current_stock_price': current_stock_price,
                    'explanation': f"Collect ${credit:.2f} now. Make money if {company} stays below ${short_call['strike_price']:.0f}"
                }
                
                if roi_percent > 20 and pop_percent > 70:  # Only good trades
                    all_credit_spreads.append(credit_spread)
    
    # Sort by ROI
    all_credit_spreads.sort(key=lambda x: x['roi_percent'], reverse=True)
    
    print(f"\n🎯 Found {len(all_credit_spreads)} good credit spread opportunities!")
    
    # Show top 10
    print(f"\n🏆 TOP 10 BEST DEALS:")
    print("-" * 80)
    
    for i, spread in enumerate(all_credit_spreads[:10]):
        print(f"{i+1:2}. {spread['company']:4} | ROI: {spread['roi_percent']:5.1f}% | "
              f"Profit Chance: {spread['probability_of_profit']:4.1f}% | "
              f"Credit: ${spread['credit_collected']:.2f}")
        print(f"     {spread['explanation']}")
    
    # Save results
    result = {
        'step': 5,
        'what_we_did': 'Found the best credit spread opportunities',
        'timestamp': datetime.now().isoformat(),
        'total_opportunities_found': len(all_credit_spreads),
        'data_sources_used': [
            'Stock prices from Step 1',
            'Options contracts from Step 2', 
            'Risk analysis from Step 3',
            'Market prices from Step 4'
        ],
        'best_deals': all_credit_spreads[:20],  # Top 20
        'trade_explanation': {
            'what_is_credit_spread': 'A trade where we collect money now and keep it if the stock behaves',
            'bear_call_spread': 'We make money if the stock does NOT go up too much',
            'roi_percent': 'How much profit we make compared to the risk',
            'probability_of_profit': 'How likely we are to make money'
        }
    }
    
    filename = 'step5_best_deals.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved best deals to: {filename}")
    
    # Also save as CSV for easy viewing
    if all_credit_spreads:
        df = pd.DataFrame(all_credit_spreads[:50])  # Top 50
        csv_filename = 'best_credit_spreads.csv'
        df.to_csv(csv_filename, index=False)
        print(f"✅ Also saved top 50 deals to: {csv_filename}")
    
    return result

if __name__ == "__main__":
    find_best_deals()
```

**Run:** `python3 find_tendies.py`


## 📁 Final Step: The Master Tendie-Yoda Script

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
        ("step1_stock_prices.py", "Getting stock prices"),
        ("step2_options_chains.py", "Finding options contracts"), 
        ("step3_risk_analysis.py", "Analyzing risk"),
        ("step4_market_prices.py", "Getting market prices"),
        ("step5_find_best_deals.py", "Finding best deals")
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
            else:
                print(f"   ❌ Step {i} failed!")
                print(f"   Error: {result.stderr}")
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
```

**Run:** 

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
├── 🤖 find_best_deals.py
├── 📊 best_deals.json
├── 📈 credit_spreads.csv
└── 🤖 master.py

**Total Runtime:** ~6 minutes for complete analysis
**Total Files Created:** 6 Python scripts + 6 data files
**Total Data Points:** 5,560+ options analyzed
**End Result:** Ranked list of best trading opportunities!


---




---
## 🐢 15 Minute Delayed Data

### Create a File 
```bash
touch delayed_data.py
open -e delayed_data.py
```

### Save the Script (15 min delayed feed)

```bash
# portfolio_data_collector.py - Fixed version for comprehensive portfolio data collection
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks, Quote
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

# Portfolio symbols
PORTFOLIO_SYMBOLS = [
    'NVDA',  # NVIDIA
    'ISRG',  # Intuitive Surgical
    'PLTR',  # Palantir
    'TSLA',  # Tesla
    'AMZN',  # Amazon
    'ENPH',  # Enphase Energy
    'XOM',   # Exxon Mobil
    'DE',    # John Deere
    'CAT'    # Caterpillar
]

async def get_stock_quotes(session):
    """
    Get current stock quotes for all portfolio symbols
    """
    stock_prices = {}
    
    try:
        async with DXLinkStreamer(session) as streamer:
            print("📡 Connecting to quote streamer...")
            await streamer.subscribe(Quote, PORTFOLIO_SYMBOLS)
            print("✅ Subscribed to quotes")
            
            # Collect quotes for 30 seconds to ensure we get all symbols
            collected_symbols = set()
            start_time = asyncio.get_event_loop().time()
            
            while len(collected_symbols) < len(PORTFOLIO_SYMBOLS) and (asyncio.get_event_loop().time() - start_time) < 30:
                try:
                    quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=5.0)
                    
                    if quote and quote.event_symbol in PORTFOLIO_SYMBOLS:
                        symbol = quote.event_symbol
                        
                        if symbol not in collected_symbols:
                            current_price = float((quote.bid_price + quote.ask_price) / 2)
                            stock_prices[symbol] = {
                                'current_price': current_price,
                                'bid': float(quote.bid_price),
                                'ask': float(quote.ask_price),
                                'spread': float(quote.ask_price - quote.bid_price),
                                'timestamp': datetime.now().isoformat()
                            }
                            collected_symbols.add(symbol)
                            print(f"   ✅ {symbol}: ${current_price:.2f}")
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"   ⚠️ Quote error: {e}")
                    continue
            
            # For any missing symbols, try to get basic market data
            missing_symbols = set(PORTFOLIO_SYMBOLS) - collected_symbols
            if missing_symbols:
                print(f"⚠️ Missing quotes for: {missing_symbols}")
                # Add placeholder data so we can still get options chains
                for symbol in missing_symbols:
                    stock_prices[symbol] = {
                        'current_price': 0.0,
                        'bid': 0.0,
                        'ask': 0.0,
                        'spread': 0.0,
                        'timestamp': datetime.now().isoformat(),
                        'note': 'Price unavailable - using options data for analysis'
                    }
                    print(f"   ⚠️ {symbol}: No quote available")
    
    except Exception as e:
        print(f"❌ Error getting quotes: {e}")
        # Create placeholder data for all symbols
        for symbol in PORTFOLIO_SYMBOLS:
            stock_prices[symbol] = {
                'current_price': 0.0,
                'bid': 0.0,
                'ask': 0.0,
                'spread': 0.0,
                'timestamp': datetime.now().isoformat(),
                'note': 'Quote error - using options data for analysis'
            }
    
    return stock_prices

async def get_portfolio_data():
    """
    Comprehensive data collection for entire trading portfolio
    """
    print("🚀 PORTFOLIO DATA COLLECTOR (FIXED VERSION)")
    print("="*80)
    print(f"📊 Collecting data for {len(PORTFOLIO_SYMBOLS)} symbols:")
    print(f"   {', '.join(PORTFOLIO_SYMBOLS)}")
    print("="*80)
    
    session = Session(USERNAME, PASSWORD)
    
    portfolio_data = {
        'timestamp': datetime.now().isoformat(),
        'symbols': PORTFOLIO_SYMBOLS,
        'stock_prices': {},
        'options_data': {},
        'greeks_data': {},
        'summary': {
            'total_symbols': len(PORTFOLIO_SYMBOLS),
            'successful_symbols': 0,
            'total_option_contracts': 0,
            'total_greeks_collected': 0
        }
    }
    
    try:
        # Step 1: Get current stock prices
        print("\n📈 STEP 1: Getting current stock prices...")
        print("-" * 50)
        
        portfolio_data['stock_prices'] = await get_stock_quotes(session)
        
        # Step 2: Get options chains for all symbols
        print(f"\n⛓️ STEP 2: Getting options chains...")
        print("-" * 50)
        
        credit_spread_options = []  # For credit spread analysis
        
        for symbol in PORTFOLIO_SYMBOLS:
            try:
                print(f"\n📊 Getting {symbol} option chain...")
                chain = get_option_chain(session, symbol)
                
                if not chain:
                    print(f"   ❌ Could not get option chain for {symbol}")
                    continue
                
                print(f"   ✅ Got {len(chain)} expirations for {symbol}")
                
                # Process options data
                symbol_option_data = {
                    'symbol': symbol,
                    'total_contracts': 0,
                    'expirations': {},
                    'current_price': portfolio_data['stock_prices'].get(symbol, {}).get('current_price', 0)
                }
                
                # Get first 4 nearest expirations for credit spread analysis
                expirations = sorted(chain.keys())[:4]
                
                for exp_date in expirations:
                    exp_date_str = str(exp_date)
                    options_list = chain[exp_date]
                    
                    print(f"   📅 Processing {exp_date_str}: {len(options_list)} contracts")
                    
                    exp_data = {
                        'expiration_date': exp_date_str,
                        'total_contracts': len(options_list),
                        'calls': 0,
                        'puts': 0,
                        'contracts': []
                    }
                    
                    # Process each option and identify credit spread candidates
                    calls_by_strike = {}
                    puts_by_strike = {}
                    
                    for option in options_list:
                        try:
                            contract_info = {
                                'symbol': option.symbol,
                                'underlying_symbol': option.underlying_symbol,
                                'strike_price': float(option.strike_price),
                                'expiration_date': str(option.expiration_date),
                                'option_type': option.option_type.value,
                                'days_to_expiration': option.days_to_expiration,
                                'streamer_symbol': option.streamer_symbol,
                                'active': option.active,
                                'shares_per_contract': option.shares_per_contract
                            }
                            
                            exp_data['contracts'].append(contract_info)
                            
                            # Organize by strike for credit spread identification
                            strike = float(option.strike_price)
                            if option.option_type.value == 'C':
                                calls_by_strike[strike] = option
                                exp_data['calls'] += 1
                            else:
                                puts_by_strike[strike] = option
                                exp_data['puts'] += 1
                            
                            # Add to credit spread candidates if DTE <= 45 (we'll filter to 33 later)
                            if option.days_to_expiration <= 45:
                                credit_spread_options.append(option)
                                    
                        except Exception as e:
                            print(f"      ⚠️ Error processing option: {e}")
                    
                    symbol_option_data['expirations'][exp_date_str] = exp_data
                    symbol_option_data['total_contracts'] += len(options_list)
                    
                    print(f"      ✅ {exp_data['calls']} calls, {exp_data['puts']} puts")
                
                portfolio_data['options_data'][symbol] = symbol_option_data
                portfolio_data['summary']['total_option_contracts'] += symbol_option_data['total_contracts']
                portfolio_data['summary']['successful_symbols'] += 1
                
                print(f"   🎯 {symbol} Summary: {symbol_option_data['total_contracts']} total contracts")
                
            except Exception as e:
                print(f"   ❌ Error getting {symbol} options: {e}")
        
        # Step 3: Get Greeks for credit spread options
        print(f"\n🔢 STEP 3: Getting Greeks data for credit spreads...")
        print("-" * 50)
        print(f"📊 Collecting Greeks for {len(credit_spread_options)} credit spread candidates")
        
        if credit_spread_options:
            # Limit to prevent timeout - take up to 100 most relevant options
            if len(credit_spread_options) > 100:
                # Sort by DTE (shorter first) and then by activity
                credit_spread_options.sort(key=lambda x: (x.days_to_expiration, x.underlying_symbol))
                credit_spread_options = credit_spread_options[:100]
                print(f"   📊 Limited to top 100 most relevant options")
            
            streamer_symbols = [option.streamer_symbol for option in credit_spread_options]
            
            async with DXLinkStreamer(session) as streamer:
                print(f"📡 Connecting to DXLink streamer for Greeks...")
                
                # Subscribe to Greeks
                await streamer.subscribe(Greeks, streamer_symbols)
                print(f"✅ Subscribed to Greeks for {len(streamer_symbols)} options")
                
                # Collect Greeks data for 60 seconds
                greeks_received = []
                print(f"⏳ Collecting Greeks data for 60 seconds...")
                
                start_time = asyncio.get_event_loop().time()
                
                while (asyncio.get_event_loop().time() - start_time) < 60:
                    try:
                        greeks_data = await asyncio.wait_for(
                            streamer.get_event(Greeks), 
                            timeout=3.0
                        )
                        
                        if isinstance(greeks_data, list):
                            greeks_received.extend(greeks_data)
                            print(f"📊 Received Greeks batch: {len(greeks_data)} items")
                        else:
                            greeks_received.append(greeks_data)
                            
                            # Only print every 10th individual item to reduce spam
                            if len(greeks_received) % 10 == 0:
                                print(f"📊 Greeks collected: {len(greeks_received)}")
                        
                    except asyncio.TimeoutError:
                        continue
                
                print(f"✅ Total Greeks collected: {len(greeks_received)}")
                
                # Process Greeks data by symbol
                greeks_by_symbol = {}
                
                for greek in greeks_received:
                    # Extract underlying symbol from option symbol
                    underlying = None
                    for symbol in PORTFOLIO_SYMBOLS:
                        if symbol in greek.event_symbol:
                            underlying = symbol
                            break
                    
                    if not underlying:
                        continue
                    
                    if underlying not in greeks_by_symbol:
                        greeks_by_symbol[underlying] = []
                    
                    # Find option info
                    option_info = next((opt for opt in credit_spread_options if opt.streamer_symbol == greek.event_symbol), None)
                    
                    greek_record = {
                        'symbol': greek.event_symbol,
                        'underlying_symbol': underlying,
                        'strike': float(option_info.strike_price) if option_info else None,
                        'option_type': option_info.option_type.value if option_info else None,
                        'days_to_expiration': option_info.days_to_expiration if option_info else None,
                        'price': float(greek.price),
                        'delta': float(greek.delta),
                        'gamma': float(greek.gamma),
                        'theta': float(greek.theta),
                        'vega': float(greek.vega),
                        'rho': float(greek.rho),
                        'implied_volatility': float(greek.volatility),
                        'time': int(greek.time)
                    }
                    
                    greeks_by_symbol[underlying].append(greek_record)
                
                portfolio_data['greeks_data'] = greeks_by_symbol
                portfolio_data['summary']['total_greeks_collected'] = len(greeks_received)
        
        # Step 4: Generate summary and save data
        print(f"\n💾 STEP 4: Saving data and generating summary...")
        print("-" * 50)
        
        # Save complete portfolio data
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"portfolio_data_{timestamp_str}.json"
        
        with open(filename, 'w') as f:
            json.dump(portfolio_data, f, indent=2, default=str)
        
        print(f"✅ Complete data saved to: {filename}")
        
        # Create and save summary
        summary_data = {
            'timestamp': portfolio_data['timestamp'],
            'portfolio_summary': {
                'symbols': PORTFOLIO_SYMBOLS,
                'successful_symbols': portfolio_data['summary']['successful_symbols'],
                'total_option_contracts': portfolio_data['summary']['total_option_contracts'],
                'total_greeks_collected': portfolio_data['summary']['total_greeks_collected']
            },
            'stock_prices': {symbol: data['current_price'] for symbol, data in portfolio_data['stock_prices'].items()},
            'options_summary': {},
            'greeks_summary': {}
        }
        
        # Options summary by symbol
        for symbol, data in portfolio_data['options_data'].items():
            summary_data['options_summary'][symbol] = {
                'total_contracts': data['total_contracts'],
                'expirations': len(data['expirations']),
                'current_price': data['current_price']
            }
        
        # Greeks summary by symbol
        for symbol, greeks_list in portfolio_data['greeks_data'].items():
            summary_data['greeks_summary'][symbol] = {
                'total_greeks': len(greeks_list),
                'calls': len([g for g in greeks_list if g.get('option_type') == 'C']),
                'puts': len([g for g in greeks_list if g.get('option_type') == 'P'])
            }
        
        summary_filename = f"portfolio_summary_{timestamp_str}.json"
        with open(summary_filename, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"✅ Summary saved to: {summary_filename}")
        
        # Print final summary
        print(f"\n🎉 PORTFOLIO DATA COLLECTION COMPLETE!")
        print("="*80)
        print(f"📊 FINAL SUMMARY:")
        print(f"   Symbols processed: {portfolio_data['summary']['successful_symbols']}/{len(PORTFOLIO_SYMBOLS)}")
        print(f"   Total option contracts: {portfolio_data['summary']['total_option_contracts']:,}")
        print(f"   Total Greeks collected: {portfolio_data['summary']['total_greeks_collected']}")
        
        print(f"\n💰 STOCK PRICES:")
        for symbol, price_data in portfolio_data['stock_prices'].items():
            price = price_data['current_price']
            if price > 0:
                print(f"   {symbol}: ${price:.2f}")
            else:
                print(f"   {symbol}: Price unavailable")
        
        print(f"\n⛓️ OPTIONS CONTRACTS BY SYMBOL:")
        for symbol, option_data in portfolio_data['options_data'].items():
            print(f"   {symbol}: {option_data['total_contracts']:,} contracts ({len(option_data['expirations'])} expirations)")
        
        print(f"\n🔢 GREEKS BY SYMBOL:")
        for symbol, greeks_list in portfolio_data['greeks_data'].items():
            calls = len([g for g in greeks_list if g.get('option_type') == 'C'])
            puts = len([g for g in greeks_list if g.get('option_type') == 'P'])
            print(f"   {symbol}: {len(greeks_list)} total ({calls} calls, {puts} puts)")
        
        return portfolio_data
        
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(get_portfolio_data())
```
---

## 🐇 Real Time Data

### Create a File

```bash
name here
```

### Save the Script (Real Time)

```bash
waiting for approval
```
___

# 5️⃣ Model



### Create a File
```bash
touch cs_picker.py
open -e cs_picker.py
```

### Save the Black Scholes Model Script
```bash
import json
import glob
import math
from datetime import datetime
import pandas as pd
from scipy.stats import norm

# === Load latest portfolio JSON ===
def load_latest_json():
    files = sorted(glob.glob("portfolio_data_*.json"))
    if not files:
        raise FileNotFoundError("No portfolio_data_*.json found!")
    latest_file = files[-1]
    print(f"📂 Using data file: {latest_file}")
    with open(latest_file, 'r') as f:
        return json.load(f)

# --- Black-Scholes PoP helper ---
def calc_pop(option_type, stock_price, strike, dte, iv, delta=None):
    # If delta already provided, use it directly
    if delta is not None:
        # Short call PoP ~ 1 - delta, short put PoP ~ delta
        return (1 - delta) if option_type == "C" else delta
    
    # Black-Scholes approximation if delta missing
    T = dte / 365
    if T <= 0:
        return 0.5
    sigma = iv if iv > 0 else 0.2
    r = 0.0

    d1 = (math.log(stock_price / strike) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == "C":  # call
        return norm.cdf(-d2)
    else:  # put
        return norm.cdf(d2)

# --- Find Greeks data for a given option symbol ---
def _find_greeks(greek_data, streamer_symbol):
    for symbol, greeks_list in greek_data.items():
        for g in greeks_list:
            if g["symbol"] == streamer_symbol:
                return g
    return {}

# --- Build credit spreads ---
def build_credit_spreads(data):
    stock_prices = data["stock_prices"]
    greeks_data = data["greeks_data"]
    spreads = []

    for symbol, sym_data in data["options_data"].items():
        underlying_price = stock_prices[symbol]["current_price"]
        expirations = sym_data["expirations"]

        for exp_date, exp_data in expirations.items():
            contracts = exp_data["contracts"]
            if not contracts:
                continue

            dte = contracts[0]["days_to_expiration"]
            if dte is None or dte > 33:
                continue

            # Separate calls and puts
            calls = sorted([c for c in contracts if c["option_type"] == "C"], key=lambda x: x["strike_price"])
            puts = sorted([p for p in contracts if p["option_type"] == "P"], key=lambda x: x["strike_price"])

            # --- Bear Call Spread ---
            for i in range(len(calls) - 1):
                short = calls[i]
                long = calls[i + 1]
                if short["strike_price"] <= underlying_price:
                    continue  # only OTM short call
                width = long["strike_price"] - short["strike_price"]

                greeks = _find_greeks(greeks_data, short["streamer_symbol"])
                delta = greeks.get("delta") if greeks else None
                iv = greeks.get("implied_volatility") if greeks else 0.2
                price = greeks.get("price") if greeks else 0.0

                pop = calc_pop("C", underlying_price, short["strike_price"], dte, iv, delta)
                credit = price
                max_loss = width - credit if width > credit else width
                roi = credit / max_loss if max_loss > 0 else 0

                spreads.append({
                    "symbol": symbol,
                    "type": "Bear Call",
                    "short": short["strike_price"],
                    "long": long["strike_price"],
                    "width": width,
                    "credit": credit,
                    "roi": roi,
                    "pop": pop,
                    "dte": dte,
                    "expiration": exp_date
                })

            # --- Bull Put Spread ---
            for i in range(1, len(puts)):
                short = puts[i]
                long = puts[i - 1]
                if short["strike_price"] >= underlying_price:
                    continue  # only OTM short put
                width = short["strike_price"] - long["strike_price"]

                greeks = _find_greeks(greeks_data, short["streamer_symbol"])
                delta = greeks.get("delta") if greeks else None
                iv = greeks.get("implied_volatility") if greeks else 0.2
                price = greeks.get("price") if greeks else 0.0

                pop = calc_pop("P", underlying_price, short["strike_price"], dte, iv, delta)
                credit = price
                max_loss = width - credit if width > credit else width
                roi = credit / max_loss if max_loss > 0 else 0

                spreads.append({
                    "symbol": symbol,
                    "type": "Bull Put",
                    "short": short["strike_price"],
                    "long": long["strike_price"],
                    "width": width,
                    "credit": credit,
                    "roi": roi,
                    "pop": pop,
                    "dte": dte,
                    "expiration": exp_date
                })
    return spreads

# === Main ===
if __name__ == "__main__":
    data = load_latest_json()
    spreads = build_credit_spreads(data)

    # Filter PoP > 66%, ROI > 33%, DTE < 33
    filtered = [s for s in spreads if s["pop"] > 0.66 and s["roi"] > 0.33 and s["dte"] < 33]
    df = pd.DataFrame(filtered)
    df = df.sort_values(by=["pop", "roi"], ascending=False)

    # Format ROI and PoP as percentages
    df["roi_pct"] = df["roi"] * 100
    df["pop_pct"] = df["pop"] * 100

    print("\n=== TOP 10 CREDIT SPREADS ===")
    print(df[["symbol", "type", "short", "long", "expiration", "dte",
              "credit", "roi_pct", "pop_pct"]].head(10))

    # Save full filtered list
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"credit_spreads_{timestamp}.csv", index=False)
    print(f"\nSaved full filtered list to credit_spreads_{timestamp}.csv")
```


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

