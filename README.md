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

## Step 1 | Install tastytrade and websockets
```bash
pip install tastytrade websockets
```
## Step 2 | Create a file `config.py`
```bash
touch config.py
open -e config.py
```
## Step 3 | Save user name and password in file
```bash
# config.py
USERNAME = "your_username_here"
PASSWORD = "your_password_here"

print("Config file loaded!")
```
## Step 4 | Create a file `test1.py`
```bash
touch test1.py
open -e test1.py
```
## Step 5 | Login to TastyTrade Script
```bash
# test1.py
from tastytrade import Session
from config import USERNAME, PASSWORD

print("Trying to log in...")

try:
    session = Session(USERNAME, PASSWORD)
    print("✅ SUCCESS! You're logged in!")
    print(f"Account type: {'demo' if session.is_test else 'live'}")
except Exception as e:
    print(f"❌ FAILED: {e}")
```
## Step 6 | Create a file `test2.py`
```bash
touch test2.py
open -e test2.py
```
## Step 7 | Query NVDA Data Script
```bash
# test2.py
import asyncio
import json
from tastytrade import Session
from config import USERNAME, PASSWORD

async def get_basic_data():
    print("Getting basic data for NVDA...")
    
    session = Session(USERNAME, PASSWORD)
    
    try:
        response = await session.async_client.get("https://api.tastyworks.com/market-metrics?symbols=NVDA")
        
        if response.status_code == 200:
            data = response.json()
            
            # Save it to a file so you can look at it
            with open("nvda_data.json", "w") as f:
                json.dump(data, f, indent=2)
            
            print("✅ SUCCESS! Data saved to nvda_data.json")
            print("Go look at that file to see what we got!")
            
        else:
            print(f"❌ FAILED: Got status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Run it
asyncio.run(get_basic_data())
```
## Step 8 | Create a file `test3.py`
```bash
touch test3.py
open -e test3.py
```
## Step 0 | Get WebSocket token needed for live data
```bash
# test3.py
import asyncio
from tastytrade import Session
from config import USERNAME, PASSWORD

async def get_token():
    print("Getting WebSocket token...")
    
    session = Session(USERNAME, PASSWORD)
    
    try:
        response = await session.async_client.get("https://api.tastyworks.com/api-quote-tokens?symbols=NVDA")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'token' in data['data']:
                token = data['data']['token']
                
                # Save the token to a file
                with open("token.txt", "w") as f:
                    f.write(token)
                
                print("✅ SUCCESS! Token saved to token.txt")
                print(f"Token preview: {token[:50]}...")
                
            else:
                print("❌ FAILED: No token in response")
                
        else:
            print(f"❌ FAILED: Got status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Run it
asyncio.run(get_token())
```
## Step 10 | Create a file `test4`
```bash
touch test4.py
open -e test4.py
```
## Step 11 | Test live data streaming 
```bash
# test4.py
import asyncio
import json
import websockets
from datetime import datetime
from tastytrade import Session
from config import USERNAME, PASSWORD

async def test_live_data():
    print("Testing live data streaming...")
    
    # Read the token we saved earlier
    try:
        with open("token.txt", "r") as f:
            token = f.read().strip()
        print("✅ Token loaded from file")
    except:
        print("❌ FAILED: No token file found. Run test3.py first!")
        return
    
    session = Session(USERNAME, PASSWORD)
    quotes_collected = []
    
    try:
        # Connect to the WebSocket
        url = session.dxlink_url
        headers = [('Authorization', f'Bearer {token}')]
        
        print("Connecting to live data feed...")
        
        async with websockets.connect(url, additional_headers=headers) as websocket:
            print("✅ Connected!")
            
            # Setup the connection (this is required protocol stuff)
            setup_msg = {"type": "SETUP", "channel": 0, "keepaliveTimeout": 60, "acceptKeepaliveTimeout": 5, "version": "0.1-DXLink-JS/8.0.0"}
            await websocket.send(json.dumps(setup_msg))
            await websocket.recv()
            
            # Login
            auth_msg = {"type": "AUTH", "channel": 0, "token": token}
            await websocket.send(json.dumps(auth_msg))
            
            # Wait for login confirmation
            for _ in range(3):
                response = await websocket.recv()
                data = json.loads(response)
                if data.get('type') == 'AUTH_STATE' and data.get('state') == 'AUTHORIZED':
                    print("✅ Logged in to live feed!")
                    break
            
            # Open a channel for data
            channel_msg = {"type": "CHANNEL_REQUEST", "channel": 1, "service": "FEED", "parameters": {"contract": "TICKER"}}
            await websocket.send(json.dumps(channel_msg))
            await websocket.recv()
            
            # Subscribe to NVDA quotes
            sub_msg = {"type": "FEED_SUBSCRIPTION", "channel": 1, "add": [{"symbol": "NVDA", "type": "Quote"}]}
            await websocket.send(json.dumps(sub_msg))
            
            print("📡 Listening for NVDA quotes for 15 seconds...")
            print("(This is REAL live data with a 15-minute delay)")
            
            # Collect data for 15 seconds
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < 15:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    parsed = json.loads(message)
                    
                    if parsed.get('type') == 'FEED_DATA':
                        data_items = parsed.get('data', [])
                        if len(data_items) >= 2 and data_items[0] == "Quote":
                            event_data = data_items[1]
                            if len(event_data) >= 13:
                                bid_price = event_data[7]
                                ask_price = event_data[11]
                                
                                quote = {
                                    'time': datetime.now().isoformat(),
                                    'bid': bid_price,
                                    'ask': ask_price,
                                    'spread': round(ask_price - bid_price, 2) if ask_price and bid_price else None
                                }
                                
                                quotes_collected.append(quote)
                                print(f"📊 Quote #{len(quotes_collected)}: Bid=${bid_price}, Ask=${ask_price}, Spread=${quote['spread']}")
                
                except asyncio.TimeoutError:
                    continue
            
            print(f"\n✅ DONE! Collected {len(quotes_collected)} quotes")
            
            # Save the quotes
            with open("live_quotes.json", "w") as f:
                json.dump(quotes_collected, f, indent=2)
            
            print("💾 Quotes saved to live_quotes.json")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Run it
asyncio.run(test_live_data())
```
## Step 12 | Create a file `test5.py`
```bash
touch test5.py
open -e test5.py
```
## Step 13 | Query the options chain 
```bash
# test5_final.py - FINAL WORKING VERSION - only uses attributes that exist
import asyncio
import json
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

async def get_option_data_final():
    print("Getting NVDA option chain data (FINAL WORKING VERSION)...")
    
    session = Session(USERNAME, PASSWORD)
    
    try:
        # Get the option chain
        print("📥 Fetching option chain...")
        chain_dict = get_option_chain(session, "NVDA")
        
        print(f"✅ Retrieved option chain!")
        print(f"   Type: {type(chain_dict)}")
        print(f"   Expiration dates found: {len(chain_dict)} dates")
        
        # Process the defaultdict structure correctly
        option_data = {
            'symbol': 'NVDA',
            'total_contracts': 0,
            'expirations': {},
            'all_contracts': []
        }
        
        print("📊 Processing option contracts by expiration...")
        
        # Iterate through each expiration date
        for expiration_date, options_list in chain_dict.items():
            exp_date_str = str(expiration_date)
            print(f"\n📅 Processing expiration: {exp_date_str}")
            print(f"   Options for this date: {len(options_list)}")
            
            # Initialize expiration data
            option_data['expirations'][exp_date_str] = {
                'expiration_date': exp_date_str,
                'total_contracts': len(options_list),
                'calls': 0,
                'puts': 0,
                'contracts': []
            }
            
            # Process each option in this expiration
            for i, option in enumerate(options_list):
                try:
                    # Only use attributes that definitely exist (based on your debug output)
                    contract_info = {
                        'symbol': option.symbol,
                        'underlying_symbol': option.underlying_symbol,
                        'strike_price': float(option.strike_price),
                        'expiration_date': str(option.expiration_date),
                        'option_type': option.option_type.value,  # 'C' or 'P'
                        'days_to_expiration': option.days_to_expiration,
                        'exercise_style': str(option.exercise_style),
                        'shares_per_contract': option.shares_per_contract,
                        'is_closing_only': option.is_closing_only,
                        'active': option.active,
                        'settlement_type': str(option.settlement_type),
                        'streamer_symbol': option.streamer_symbol,
                        'instrument_type': str(option.instrument_type),
                        'option_chain_type': str(option.option_chain_type),
                        'expiration_type': str(option.expiration_type)
                    }
                    
                    # Try to get optional attributes safely
                    try:
                        contract_info['stops_trading_at'] = str(option.stops_trading_at)
                    except:
                        contract_info['stops_trading_at'] = None
                    
                    try:
                        contract_info['expires_at'] = str(option.expires_at)
                    except:
                        contract_info['expires_at'] = None
                    
                    try:
                        contract_info['market_time_instrument_collection'] = str(option.market_time_instrument_collection)
                    except:
                        contract_info['market_time_instrument_collection'] = None
                    
                    # Add to expiration-specific data
                    option_data['expirations'][exp_date_str]['contracts'].append(contract_info)
                    
                    # Add to overall contracts list
                    option_data['all_contracts'].append(contract_info)
                    
                    # Count calls vs puts
                    if option.option_type.value == 'C':
                        option_data['expirations'][exp_date_str]['calls'] += 1
                    else:
                        option_data['expirations'][exp_date_str]['puts'] += 1
                    
                    # Print first few from each expiration
                    if i < 3:
                        print(f"      ✅ {i+1}. {option.symbol} | ${option.strike_price} {option.option_type.value} | DTE: {option.days_to_expiration}")
                
                except Exception as e:
                    print(f"      ⚠️ Error processing option {i}: {e}")
                    # Add error record but continue
                    error_contract = {
                        'symbol': f'ERROR_{i}',
                        'error': str(e),
                        'strike_price': 0,
                        'expiration_date': exp_date_str,
                        'option_type': 'ERROR'
                    }
                    option_data['all_contracts'].append(error_contract)
            
            # Update total count
            option_data['total_contracts'] += len(options_list)
            
            exp_data = option_data['expirations'][exp_date_str]
            print(f"   ✅ {exp_date_str}: {exp_data['calls']} calls, {exp_data['puts']} puts ({exp_data['total_contracts']} total)")
        
        # Save all option data
        with open("nvda_options_final.json", "w") as f:
            json.dump(option_data, f, indent=2, default=str)
        
        print(f"\n💾 Final option data saved to nvda_options_final.json")
        
        # Create summary
        summary = {
            'symbol': 'NVDA',
            'total_contracts': option_data['total_contracts'],
            'total_expirations': len(option_data['expirations']),
            'expiration_summary': {}
        }
        
        # Summarize each expiration
        total_calls = 0
        total_puts = 0
        for exp_date, exp_data in option_data['expirations'].items():
            summary['expiration_summary'][exp_date] = {
                'total': exp_data['total_contracts'],
                'calls': exp_data['calls'],
                'puts': exp_data['puts'],
                'days_to_expiration': exp_data['contracts'][0]['days_to_expiration'] if exp_data['contracts'] else 0
            }
            total_calls += exp_data['calls']
            total_puts += exp_data['puts']
        
        summary['total_calls'] = total_calls
        summary['total_puts'] = total_puts
        
        with open("nvda_options_final_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"📋 Summary saved to nvda_options_final_summary.json")
        
        # Print comprehensive stats
        print(f"\n📈 COMPREHENSIVE OPTION CHAIN STATS:")
        print(f"   Total contracts: {option_data['total_contracts']:,}")
        print(f"   Total calls: {total_calls:,}")
        print(f"   Total puts: {total_puts:,}")
        print(f"   Expiration dates: {len(option_data['expirations'])}")
        
        # Show each expiration
        print(f"\n📅 ALL EXPIRATIONS:")
        sorted_expirations = sorted(option_data['expirations'].items())
        for exp_date, exp_data in sorted_expirations:
            dte = exp_data['contracts'][0]['days_to_expiration'] if exp_data['contracts'] else 0
            print(f"   {exp_date} (DTE: {dte:2d}): {exp_data['calls']:3d} calls + {exp_data['puts']:3d} puts = {exp_data['total_contracts']:3d} total")
        
        # Show strike range for nearest expiration
        if sorted_expirations:
            nearest_exp_date, nearest_exp_data = sorted_expirations[0]
            strikes = [contract['strike_price'] for contract in nearest_exp_data['contracts'] if contract.get('strike_price', 0) > 0]
            if strikes:
                print(f"\n🎯 NEAREST EXPIRATION ({nearest_exp_date}):")
                print(f"   Strike range: ${min(strikes):.2f} - ${max(strikes):.2f}")
                print(f"   Total strikes: {len(set(strikes))}")
        
        # Show sample contracts
        print(f"\n📊 SAMPLE CONTRACTS (first 5 successful):")
        successful_contracts = [c for c in option_data['all_contracts'] if not c.get('error')]
        for i, contract in enumerate(successful_contracts[:5]):
            print(f"   {i+1}. {contract['symbol']}")
            print(f"      Strike: ${contract['strike_price']} {contract['option_type']}")
            print(f"      Expiration: {contract['expiration_date']} (DTE: {contract['days_to_expiration']})")
            print(f"      Streamer: {contract['streamer_symbol']}")
            print()
        
        print(f"🎉 SUCCESS! Collected {len(successful_contracts):,} valid option contracts!")
        
        return option_data
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

# Run it
if __name__ == "__main__":
    asyncio.run(get_option_data_final())
```
## Create a file `test6.py`
## Query for the greeks
```bash
# comprehensive_greeks_fetcher.py - Get Greeks for more realistic strike prices
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks, Quote
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

async def get_comprehensive_greeks():
    """
    Get Greeks for more realistic NVDA option strikes that are likely to have active data
    """
    print("🎯 COMPREHENSIVE GREEKS FETCHER")
    print("="*60)
    
    session = Session(USERNAME, PASSWORD)
    
    try:
        # Get NVDA current price first
        print("📊 Getting NVDA stock quote first...")
        async with DXLinkStreamer(session) as temp_streamer:
            await temp_streamer.subscribe(Quote, ['NVDA'])
            nvda_quote = await asyncio.wait_for(
                temp_streamer.get_event(Quote), 
                timeout=10.0
            )
            nvda_price = float((nvda_quote.bid_price + nvda_quote.ask_price) / 2)
            print(f"💰 NVDA Current Price: ~${nvda_price:.2f}")
        
        # Get option chain
        print(f"\n📊 Getting NVDA option chain...")
        chain = get_option_chain(session, 'NVDA')
        
        if not chain:
            print("❌ Could not get option chain")
            return None
        
        print(f"✅ Got option chain with {len(chain)} expirations")
        
        # Get options from the first 2 nearest expirations
        expirations = sorted(chain.keys())[:2]
        
        all_test_options = []
        
        for exp_date in expirations:
            print(f"\n📅 Processing expiration: {exp_date}")
            options = chain[exp_date]
            
            # Select strikes around the current stock price
            target_strikes = [
                nvda_price * 0.95,  # 5% OTM put / ITM call
                nvda_price * 0.98,  # 2% OTM put / ITM call  
                nvda_price * 1.00,  # ATM
                nvda_price * 1.02,  # 2% OTM call / ITM put
                nvda_price * 1.05,  # 5% OTM call / ITM put
            ]
            
            exp_options = []
            
            for target_strike in target_strikes:
                # Find closest actual strikes for calls and puts
                # Convert Decimal strike_price to float for comparison
                closest_call = min(
                    [opt for opt in options if opt.option_type.value == 'C'],
                    key=lambda x: abs(float(x.strike_price) - target_strike),
                    default=None
                )
                closest_put = min(
                    [opt for opt in options if opt.option_type.value == 'P'],
                    key=lambda x: abs(float(x.strike_price) - target_strike),
                    default=None
                )
                
                if closest_call and closest_call not in exp_options:
                    exp_options.append(closest_call)
                if closest_put and closest_put not in exp_options:
                    exp_options.append(closest_put)
            
            # Limit to 8 options per expiration
            exp_options = exp_options[:8]
            all_test_options.extend(exp_options)
            
            print(f"   📈 Selected {len(exp_options)} options around ${nvda_price:.0f}")
            for opt in exp_options:
                strike_price = float(opt.strike_price)  # Convert Decimal to float
                distance = ((strike_price / nvda_price) - 1) * 100
                moneyness = "ITM" if (opt.option_type.value == 'C' and strike_price < nvda_price) or \
                                   (opt.option_type.value == 'P' and strike_price > nvda_price) else "OTM"
                print(f"      {opt.option_type.value} ${strike_price:.0f} ({distance:+.1f}% {moneyness})")
        
        print(f"\n🎯 Total options to test: {len(all_test_options)}")
        
        # Get streamer symbols
        streamer_symbols = [option.streamer_symbol for option in all_test_options]
        
        # Connect to streamer and get data
        print(f"\n📡 Connecting to DXLink streamer...")
        
        async with DXLinkStreamer(session) as streamer:
            print(f"✅ Connected!")
            
            # Subscribe to Greeks and Quotes
            print(f"📊 Subscribing to Greeks and Quotes...")
            await streamer.subscribe(Greeks, streamer_symbols)
            await streamer.subscribe(Quote, streamer_symbols)
            
            print(f"✅ Subscribed! Waiting for data...")
            
            # Collect Greeks data for up to 30 seconds
            greeks_received = []
            quotes_received = []
            
            print(f"⏳ Collecting data for 30 seconds...")
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < 30:
                try:
                    # Try to get Greeks
                    greeks_data = await asyncio.wait_for(
                        streamer.get_event(Greeks), 
                        timeout=2.0
                    )
                    
                    if isinstance(greeks_data, list):
                        greeks_received.extend(greeks_data)
                    else:
                        greeks_received.append(greeks_data)
                    
                    print(f"📊 Received Greeks for: {greeks_data.event_symbol if not isinstance(greeks_data, list) else f'{len(greeks_data)} symbols'}")
                    
                except asyncio.TimeoutError:
                    # Try to get quotes instead
                    try:
                        quote_data = await asyncio.wait_for(
                            streamer.get_event(Quote),
                            timeout=2.0
                        )
                        
                        if isinstance(quote_data, list):
                            quotes_received.extend(quote_data)
                        else:
                            quotes_received.append(quote_data)
                            
                    except asyncio.TimeoutError:
                        continue
            
            # Process and display results
            print(f"\n🎉 DATA COLLECTION COMPLETE!")
            print("="*60)
            print(f"📊 Greeks received: {len(greeks_received)}")
            print(f"💰 Quotes received: {len(quotes_received)}")
            
            if greeks_received:
                print(f"\n🔢 GREEKS DATA:")
                print("="*60)
                
                # Group by expiration for better display
                greeks_by_exp = {}
                for greek in greeks_received:
                    # Extract expiration from symbol (e.g., .NVDA250801C140 -> 250801)
                    exp_part = greek.event_symbol.split('250801')[0] + '250801' if '250801' in greek.event_symbol else 'Unknown'
                    if exp_part not in greeks_by_exp:
                        greeks_by_exp[exp_part] = []
                    greeks_by_exp[exp_part].append(greek)
                
                for exp, greeks_list in greeks_by_exp.items():
                    print(f"\n📅 Expiration: {exp}")
                    print("-" * 40)
                    
                    for greek in sorted(greeks_list, key=lambda x: (x.event_symbol[-1], float(x.event_symbol.split('C')[-1] if 'C' in x.event_symbol else x.event_symbol.split('P')[-1]))):
                        # Find option info
                        option_info = next((opt for opt in all_test_options if opt.streamer_symbol == greek.event_symbol), None)
                        
                        # Calculate moneyness
                        if option_info:
                            strike_price = float(option_info.strike_price)  # Convert Decimal to float
                            if option_info.option_type.value == 'C':
                                moneyness = (nvda_price - strike_price) / nvda_price * 100
                                itm_otm = "ITM" if moneyness > 0 else "OTM"
                            else:  # Put
                                moneyness = (strike_price - nvda_price) / nvda_price * 100
                                itm_otm = "ITM" if moneyness > 0 else "OTM"
                        else:
                            moneyness = 0
                            itm_otm = "UNK"
                            strike_price = 0
                        
                        print(f"📊 {greek.event_symbol}")
                        if option_info:
                            print(f"   📋 {option_info.option_type.value} ${strike_price:.0f} ({moneyness:+.1f}% {itm_otm})")
                        print(f"   💲 Price: ${greek.price:.4f}")
                        print(f"   📈 Delta: {greek.delta:.6f}")
                        print(f"   🔄 Gamma: {greek.gamma:.8f}")
                        print(f"   ⏰ Theta: {greek.theta:.6f}")
                        print(f"   📊 Vega: {greek.vega:.6f}")
                        print(f"   🏦 Rho: {greek.rho:.6f}")
                        print(f"   📉 IV: {greek.volatility*100:.2f}%")
                        print()
            
            # Save data to file
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'nvda_price': nvda_price,
                'total_greeks_received': len(greeks_received),
                'total_quotes_received': len(quotes_received),
                'greeks_data': []
            }
            
            for greek in greeks_received:
                option_info = next((opt for opt in all_test_options if opt.streamer_symbol == greek.event_symbol), None)
                
                output_data['greeks_data'].append({
                    'symbol': greek.event_symbol,
                    'strike': float(option_info.strike_price) if option_info else None,
                    'option_type': option_info.option_type.value if option_info else None,
                    'price': float(greek.price),
                    'delta': float(greek.delta),
                    'gamma': float(greek.gamma),
                    'theta': float(greek.theta),
                    'vega': float(greek.vega),
                    'rho': float(greek.rho),
                    'implied_volatility': float(greek.volatility),
                    'time': int(greek.time)
                })
            
            filename = f"nvda_comprehensive_greeks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"💾 Saved comprehensive data to: {filename}")
            
            return output_data
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(get_comprehensive_greeks())
```

# 4️⃣ Fetch TastyTrade Data

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

