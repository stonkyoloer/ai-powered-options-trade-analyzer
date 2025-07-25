# 🚀 Overview  
Build and maintain a daily-refreshed, AI-driven, sector-diversified options portfolio—and power a daily screener for high-probability tendies!

# 🔍 Scope  

- **Download the Data**  

 

 
- **AI Prompting**  





- **Execution**







# 🗂 Download the Data

**TASTYTRADE**

  **STEP 1 | CREATE A TASTYTRADE FOLDER**
  ````bash
  mkdir tastytrade_data
  ````
  **STEP 2 | OPEN THE FOLDER**
  ````bash
  cd tastytrade_data
  ````
  **STEP 3 | INSTALL PACKAGES**
  ````bash
  pip3 install pandas requests
  ````
  **STEP 4 | CREATE A CONNECTION FILE**
  ````bash
  touch test_connection.py
  ````
  **STEP 5 | OPEN THE FILE IN A TEXT EDITOR**
  ````bash
  open -e test_connection.py
  ````
  **STEP 6 | CONNECT TO API**
  ````bash
  import requests
import json

# Test basic connection to TastyTrade
print("Testing TastyTrade API connection...")

url = "https://api.tastytrade.com/sessions"
print(f"API URL: {url}")
print("Ready for authentication test")
````
**STEP 7 | SAVE THE FILE**
````bash
CMD + S
````
**STEP 8 | RUN THE TEST**
````bash
python3 test_connection.py
````
**STEP 9 | CREATE AUTHENTICATION FILE**
````bash
touch auth_test.py
````
**STEP 10 | OPEN THE FILE**
````bash
open -e auth_test.py
````
**STEP 11 | SET UP AUTHENTICATION** 
````bash
import requests
import json

# Your TastyTrade credentials
USERNAME = "your_username_here"
PASSWORD = "your_password_here"

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
````
**STEP 12 | SAVE THE FILE**
````bash
CMD + S
````
**STEP 13 | RUN THE TEST**
````bash
python3 auth_test.py
````
**STEP 14 | CREATE ACCOUNT INFO FILE**
````bash
touch get_accounts.py
````
**STEP 15 | OPEN THE FILE**
````bash
open -e get_accounts.py
````
**STEP 16 | CONNECT TO TRADING ACCOUNT**
````bash
import requests
import json

# Your credentials
USERNAME = "your_username_here"
PASSWORD = "your_password_here"

# Step 1: Get session token
print("Getting session token...")
auth_url = "https://api.tastytrade.com/sessions"
auth_data = {"login": USERNAME, "password": PASSWORD}

response = requests.post(auth_url, json=auth_data)
session_token = response.json()['data']['session-token']
print("Got session token")

# Step 2: Get accounts
print("Getting account info...")
accounts_url = "https://api.tastytrade.com/customers/me/accounts"
headers = {"Authorization": session_token}

response = requests.get(accounts_url, headers=headers)
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    accounts = response.json()['data']['items']
    print(f"Found {len(accounts)} account(s)")
    
    for account in accounts:
        account_number = account['account']['account-number']
        print(f"Account number: {account_number}")
else:
    print("Failed to get accounts")
    print(response.text)
````
Remember to enter your username and password
**STEP 17 | RUN THE TEST**
````bash
python3 get_accounts.py
````
**STEP 18 | CREATE A POSITIONS FILE**
````bash
touch get_positions.py
````
**STEP 19 | OPEN THE FILE**
````bash
open -e get_positions.py
````
**STEP 20 | QUERY FOR OPEN POSITIONS**
````bash
import requests
import json

# Your credentials
USERNAME = "your_username_here"
PASSWORD = "your_password_here"

# Use your first account
ACCOUNT_NUMBER = "123456789"

# Step 1: Get session token
print("Getting session token...")
auth_url = "https://api.tastytrade.com/sessions"
auth_data = {"login": USERNAME, "password": PASSWORD}

response = requests.post(auth_url, json=auth_data)
session_token = response.json()['data']['session-token']
print("Got session token")

# Step 2: Get positions
print(f"Getting positions for account {ACCOUNT_NUMBER}...")
positions_url = f"https://api.tastytrade.com/accounts/{ACCOUNT_NUMBER}/positions"
headers = {"Authorization": session_token}

response = requests.get(positions_url, headers=headers)
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    positions = response.json()['data']['items']
    print(f"Found {len(positions)} position(s)")
    
    for position in positions:
        symbol = position['instrument']['symbol']
        quantity = position['quantity']
        instrument_type = position['instrument']['instrument-type']
        print(f"- {symbol}: {quantity} shares/contracts ({instrument_type})")
else:
    print("Failed to get positions")
    print(response.text)
````
**STEP 21 | RUN THE QUERY**
````bash
python3 get_positions.py
````

JUST IN CASE >>>>

**STEP 22 | CREATE OPTIONS CHAIN FILE**
````bash
touch get_options_chain_with_dxlink.py
````
**STEP 23 | OPEN FILE**
````bash
open -e get_options_chain_with_dxlink.py
````
**STEP 24 | QUERY FOR OPTIONS CHAIN**
````bash
#!/usr/bin/env python3
"""
Fixed version of options chain script with SSL certificate handling and robust error checking
"""

import asyncio
import json
import ssl
import websockets
import pandas as pd
from tastytrade import Session
from tastytrade.instruments import get_option_chain, Equity
import httpx
from typing import List, Dict, Any, Optional
import certifi

# ==== USER SETTINGS ====
USERNAME = "your_username"
PASSWORD = "your_password"
TICKER = "AAPL"

class TokenManager:
    def __init__(self, session: Session):
        self.session = session
        self._token_cache = {}
    
    async def get_dxlink_token(self) -> Optional[tuple]:
        """Get DXLink token with proper error handling"""
        try:
            # Use session token directly without Bearer prefix
            headers = {"Authorization": self.session.session_token}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.tastytrade.com/api-quote-tokens",
                    headers=headers
                )
                
                print(f"DXLink token response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        token = data['data']['token']
                        dxlink_url = data['data']['dxlink-url']
                        print(f"✅ Got DXLink token, URL: {dxlink_url}")
                        return token, dxlink_url
                    else:
                        print(f"❌ Unexpected response format: {data}")
                        return None
                else:
                    print(f"❌ Token request failed: HTTP {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Exception getting DXLink token: {e}")
            return None

async def get_options_greeks_websocket(symbols: List[str], token: str, dxlink_url: str) -> List[Dict]:
    """Connect to DXLink WebSocket with SSL certificate verification disabled"""
    
    if not symbols:
        print("⚠️ No symbols provided")
        return []
    
    print(f"🔗 Connecting to DXLink: {dxlink_url}")
    print(f"📊 Requesting data for {len(symbols)} symbols")
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Alternative: Use system certificates
    # ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    try:
        async with websockets.connect(
            dxlink_url,
            ssl=ssl_context,
            extra_headers={"Authorization": f"Bearer {token}"},
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10
        ) as websocket:
            
            # Send subscription request
            subscription_message = {
                "channel": "trades",
                "symbols": symbols,
                "types": ["Greeks", "Quote", "Trade"]
            }
            
            await websocket.send(json.dumps(subscription_message))
            print(f"📤 Sent subscription for {len(symbols)} symbols")
            
            # Collect data with timeout
            data_received = []
            timeout_seconds = 30
            
            try:
                async with asyncio.timeout(timeout_seconds):
                    message_count = 0
                    while message_count < 100:  # Limit messages to avoid infinite loop
                        try:
                            message = await websocket.recv()
                            message_count += 1
                            
                            if message_count % 10 == 0:
                                print(f"📥 Received {message_count} messages...")
                            
                            try:
                                data = json.loads(message)
                                if isinstance(data, dict):
                                    data_received.append(data)
                                elif isinstance(data, list):
                                    data_received.extend(data)
                            except json.JSONDecodeError:
                                continue
                                
                        except websockets.exceptions.ConnectionClosed:
                            print("🔌 WebSocket connection closed")
                            break
                        except Exception as e:
                            print(f"⚠️ Error receiving message: {e}")
                            continue
                            
            except asyncio.TimeoutError:
                print(f"⏰ Timeout after {timeout_seconds} seconds")
            
            print(f"📊 Collected {len(data_received)} total messages")
            return data_received
            
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("💡 Try updating your certificates or using a VPN")
        return []
    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        return []

def process_websocket_data(raw_data: List[Dict], symbols: List[str]) -> pd.DataFrame:
    """Process raw websocket data into a structured DataFrame"""
    
    if not raw_data:
        print("⚠️ No raw data to process")
        return pd.DataFrame()
    
    processed_data = []
    
    for item in raw_data:
        if not isinstance(item, dict):
            continue
            
        # Look for Greeks data
        if 'Greeks' in item or 'greeks' in item:
            greeks_data = item.get('Greeks') or item.get('greeks', {})
            symbol = item.get('symbol', '')
            
            if symbol in symbols and isinstance(greeks_data, dict):
                row = {
                    'symbol': symbol,
                    'delta': greeks_data.get('delta'),
                    'gamma': greeks_data.get('gamma'),
                    'theta': greeks_data.get('theta'),
                    'vega': greeks_data.get('vega'),
                    'rho': greeks_data.get('rho'),
                    'iv': greeks_data.get('impliedVolatility'),
                    'timestamp': item.get('timestamp')
                }
                processed_data.append(row)
        
        # Also check for direct data format
        elif 'symbol' in item and any(greek in item for greek in ['delta', 'gamma', 'theta', 'vega']):
            if item['symbol'] in symbols:
                row = {
                    'symbol': item['symbol'],
                    'delta': item.get('delta'),
                    'gamma': item.get('gamma'),
                    'theta': item.get('theta'),
                    'vega': item.get('vega'),
                    'rho': item.get('rho'),
                    'iv': item.get('impliedVolatility') or item.get('iv'),
                    'timestamp': item.get('timestamp')
                }
                processed_data.append(row)
    
    df = pd.DataFrame(processed_data)
    print(f"📊 Processed {len(df)} rows of Greeks data")
    
    if not df.empty:
        print(f"📊 Available columns: {list(df.columns)}")
        # Show sample of non-null values
        for col in ['delta', 'gamma', 'theta', 'vega']:
            if col in df.columns:
                non_null_count = df[col].notna().sum()
                print(f"   {col}: {non_null_count} non-null values")
    
    return df

async def fetch_chain_with_greeks(session: Session, token_manager: TokenManager, ticker: str):
    """Fetch options chain with Greeks data and robust error handling"""
    
    print(f"🔍 Processing {ticker}...")
    
    # Get options chain from tastytrade using the correct method
    try:
        # First get the underlying equity
        equity = Equity.get(session, ticker)
        print(f"📈 Got equity: {equity.symbol} - {equity.description}")
        
        # Get the options chain
        chain = get_option_chain(session, ticker)
        print(f"📅 Got options chain with {len(chain)} options")
    except Exception as e:
        print(f"❌ Failed to get options chain: {e}")
        import traceback
        traceback.print_exc()
        return
    
    all_data = []
    
    # The chain is already a dictionary with expiration dates as keys
    print(f"📅 Total expirations: {len(chain)}")
    print(f"📅 Available expirations: {list(chain.keys())[:5]}...")  # Show first 5 expiration dates
    
    # Process each expiration (limit to first 2 for testing)
    for exp_date, options_list in list(chain.items())[:2]:
        print(f"\n--- 📊 Expiration: {exp_date} ---")
        
        # Limit options for testing (take first 20)
        options_subset = options_list[:20] if len(options_list) > 20 else options_list
        
        # Build streaming symbols and chain rows
        streaming_symbols = []
        chain_rows = []
        
        for option in options_subset:
            try:
                row = {
                    'expiration': exp_date,
                    'strike': option.strike_price,
                    'option_type': 'Call' if option.option_type.value == 'C' else 'Put',
                    'symbol': option.symbol,
                    'streamer_symbol': option.streamer_symbol,
                    'underlying_symbol': option.underlying_symbol
                }
                chain_rows.append(row)
                streaming_symbols.append(option.streamer_symbol)
            except AttributeError as e:
                print(f"⚠️ Error processing option {option}: {e}")
                # Print available attributes for debugging
                print(f"   Available attributes: {[attr for attr in dir(option) if not attr.startswith('_')]}")
                continue
        
        print(f"🎯 Number of options: {len(options_subset)}")
        print(f"🔗 Streaming symbols: {len(streaming_symbols)}")
        
        if not streaming_symbols:
            print("⚠️ No streaming symbols found")
            continue
        
        # Get DXLink token
        print("🔄 Getting DXLink token...")
        token_result = await token_manager.get_dxlink_token()
        
        if not token_result:
            print(f"❌ Could not get DXLink token for {exp_date}")
            # Add rows without Greeks data
            all_data.extend(chain_rows)
            continue
        
        token, dxlink_url = token_result
        
        # Get Greeks data via WebSocket
        try:
            raw_greeks_data = await get_options_greeks_websocket(
                streaming_symbols, token, dxlink_url
            )
            
            if raw_greeks_data:
                greeks_df = process_websocket_data(raw_greeks_data, streaming_symbols)
                
                if not greeks_df.empty:
                    # Merge Greeks data with chain data
                    chain_df = pd.DataFrame(chain_rows)
                    merged_df = chain_df.merge(
                        greeks_df, 
                        left_on='streamer_symbol', 
                        right_on='symbol', 
                        how='left',
                        suffixes=('', '_greeks')
                    )
                    all_data.extend(merged_df.to_dict('records'))
                    print(f"✅ Added {len(merged_df)} rows with Greeks data")
                else:
                    print("⚠️ No Greeks data processed")
                    all_data.extend(chain_rows)
            else:
                print("⚠️ No raw Greeks data received")
                all_data.extend(chain_rows)
                
        except Exception as e:
            print(f"❌ Error getting data for {exp_date}: {e}")
            # Add rows without Greeks data
            all_data.extend(chain_rows)
    
    # Save to CSV
    if all_data:
        df = pd.DataFrame(all_data)
        filename = f"{ticker}_options_chain_with_greeks.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(df)} rows to {filename}")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Check for Greeks data
        greek_columns = ['delta', 'gamma', 'theta', 'vega', 'rho', 'iv']
        has_greeks = any(col in df.columns and df[col].notna().any() for col in greek_columns)
        
        if has_greeks:
            print("✅ Greeks data collected successfully!")
            # Show sample of Greeks data
            for col in greek_columns:
                if col in df.columns:
                    non_null = df[col].notna().sum()
                    if non_null > 0:
                        avg_val = df[col].mean()
                        print(f"   {col}: {non_null} values, avg: {avg_val:.4f}")
        else:
            print("⚠️ No Greeks data collected")
    else:
        print("❌ No data collected")

async def main():
    """Main function with comprehensive error handling"""
    try:
        print("🔐 Logging in to tastytrade...")
        session = Session(USERNAME, PASSWORD)
        print("✅ Login successful!")
        
        # Test authentication first
        print("🧪 Testing authentication methods first...")
        print("🔍 Testing basic API access...")
        
        # Test different auth methods
        auth_methods = [
            ("Direct token (no Bearer)", lambda: session.session_token),
            ("Bearer token", lambda: f"Bearer {session.session_token}"),
        ]
        
        working_auth = None
        
        async with httpx.AsyncClient() as client:
            for method_name, auth_func in auth_methods:
                try:
                    print(f"\nTesting {method_name}...")
                    headers = {"Authorization": auth_func()}
                    
                    # Test customer API
                    response = await client.get(
                        "https://api.tastytrade.com/customers/me",
                        headers=headers
                    )
                    print(f"Customer API status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"✅ {method_name} works for basic API!")
                        data = response.json()
                        if 'data' in data and 'email' in data['data']:
                            print(f"Customer email: {data['data']['email']}")
                        
                        # Test quote tokens
                        quote_response = await client.get(
                            "https://api.tastytrade.com/api-quote-tokens",
                            headers=headers
                        )
                        print(f"Quote token status: {quote_response.status_code}")
                        
                        if quote_response.status_code == 200:
                            print(f"✅ Quote tokens work with {method_name}!")
                            working_auth = method_name
                            break
                        else:
                            print(f"❌ Quote tokens failed with {method_name}")
                    
                except Exception as e:
                    print(f"❌ {method_name} failed: {e}")
        
        if not working_auth:
            print("❌ No working authentication method found")
            return
        
        print(f"\n🚀 Authentication works! Proceeding with options chain...")
        
        # Create token manager and fetch data
        token_manager = TokenManager(session)
        await fetch_chain_with_greeks(session, token_manager, TICKER)
        
    except Exception as e:
        print(f"❌ Main error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 All done!")

if __name__ == "__main__":
    asyncio.run(main())
````
**STEP 25 | RUN THE QUERY**
````bash
python3 get_options_chain_with_dxlink.py
````












  -**Save Workflow Steps in a VS notbook**















# 🤖 Project Prompt: AI Pick 9 Tickers

#### Attachment
- us_tickers.csv

#### Instructions 

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

#### Prompt
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

#### Prompt Output
**Portfolio Metrics Summary**  
_Optimized AI-Driven Options Portfolio (2025-07-20)_  
**CHAT GPT SELECTION(S)**
```markdown
| Ticker | Sector             | AI Leadership Summary                                                      | Avg IV % | IV Rank | RSI(5)       | MACD Signal | Daily Volume | Liquidity Grade   |
|--------|--------------------|-----------------------------------------------------------------------------|----------|---------|--------------|-------------|--------------|-------------------|
| GOOGL  | Comm. Services     | Global leader in AI research & applications (search, cloud, generative AI) | 36%      | 43%     | 55 (neutral) | Bullish     | 24M          | A (ideal)         |
| TSLA   | Cons. Discretionary| Autonomous driving pioneer; deploys advanced AI at scale in vehicles       | 55%      | 17%     | 60 (bullish) | Bullish     | 85M          | A (ideal)         |
| HLX    | Energy             | Offshore energy services firm specializing in subsea robotics              | 52%      | 84%     | 60 (bullish) | Bullish     | 1.8M         | C (avoid)         |
| UPST   | Financials         | Leading AI-driven lending platform expanding credit access for banks       | 109%     | 55%     | 50 (neutral) | Slight Bull | 6.3M         | B (acceptable)    |
| ISRG   | Health Care        | Pioneer of robotic surgery – its da Vinci system is an AI-powered platform  | 38%      | 85%     | 60 (bullish) | Bullish     | 1.7M         | B (acceptable)    |
| SYM    | Industrials        | Leading AI-powered robotics provider automating warehouse supply chains    | 114%     | 62%     | 80 (overbought)| Bullish   | 1.7M         | B (acceptable)    |
| PLTR   | Info. Technology   | Defense & big-data software leader; “indispensable” AI partner for govts   | 66%      | 40%     | 50 (neutral) | Bullish     | 45M          | A (ideal)         |
```
**GROK SELECTION(S)**


# ✈️ Data Pipe: TastyTrade and yfinance

## Get the Raw Data
### Terminal

#### Create Project Folder 

````bash
mkdir -p ~/Desktop/StonkYoloer
````

#### Open Stonk Yoler Project Foler

````bash
cd ~/Desktop/StonkYoloer
````

#### Wipe old venv (if it exists)

````bash
rm -rf .venv
````

#### Create Virtual Environment

````bash
python3 -m venv .venv
````

#### Open Virtual Environment

````bash
source .venv/bin/activate
````

#### Install Packages

````bash
pip install pandas numpy scipy yfinance
````

#### Enter UN and PW

````bash
export TASTYTRADE_USER='stonkyoloer'
export TASTYTRADE_PASS='PASSWORD'
````

#### Enter Script into terminal

````bash
nano full_options_report.py
````

````bash
#!/usr/bin/env python3
import os, sys
import pandas as pd
import yfinance as yf
from tastytrade import Session
from tastytrade.instruments import get_option_chain

TICKERS = [
    'NVDA','LMT','ISRG','HLX','TSLA','COIN','RBLX','Z','AVAV',
    'DE','SYM','RXRX','GOOGL','PLTR','UPST'
]

def get_session():
    user, pw = os.getenv('TASTYTRADE_USER'), os.getenv('TASTYTRADE_PASS')
    if not user or not pw:
        print("ERROR: set TASTYTRADE_USER & TASTYTRADE_PASS")
        sys.exit(1)
    return Session(user, pw)

def fetch_metadata_df(session, ticker):
    print(f"Fetching metadata for {ticker}...")
    try:
        chain = get_option_chain(session, ticker)
    except Exception as e:
        print(f"  ⚠️  {e}")
        return pd.DataFrame()
    rows = []
    for exp_date, opts in chain.items():
        exp = exp_date.isoformat()
        for opt in opts:
            raw = opt.model_dump()
            rows.append({
                'ticker': ticker,
                'expiration': exp,
                'strike_price': raw['strike_price'],
                'option_type': raw['option_type'],
                'symbol': raw['symbol'],
                'streamer_symbol': raw.get('streamer_symbol') or f".{raw['symbol']}"
            })
    return pd.DataFrame(rows)

def fetch_market_df(ticker):
    print(f"Fetching market data for {ticker}...")
    tk = yf.Ticker(ticker)
    all_rows = []
    for exp in tk.options:
        try:
            chain = tk.option_chain(exp)
        except:
            continue
        for side, df_side in [('Call', chain.calls), ('Put', chain.puts)]:
            if df_side.empty: continue
            df2 = df_side.copy()
            df2['ticker'], df2['expiration'], df2['option_type'] = ticker, exp, side
            df2.rename(columns={
                'strike':'strike_price',
                'lastPrice':'last',
                'openInterest':'open_interest',
                'impliedVolatility':'implied_volatility'
            }, inplace=True)
            keep = ['ticker','expiration','strike_price','option_type','bid','ask','last','volume','open_interest','implied_volatility']
            all_rows.append(df2[keep])
    return pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()

def main():
    sess = get_session()
    all_meta = [fetch_metadata_df(sess, t) for t in TICKERS]
    all_market = [fetch_market_df(t) for t in TICKERS]

    meta_df = pd.concat(all_meta, ignore_index=True)
    market_df = pd.concat(all_market, ignore_index=True)

    meta_df.to_csv("metadata.csv", index=False)
    market_df.to_csv("market_data.csv", index=False)
    print("✅ Saved metadata.csv and market_data.csv")

if __name__ == '__main__':
    main()
````

#### Launch Query

````bash
#!/usr/bin/env python3
"""
Full Options Report Builder:
- Pulls full option chain from Tastytrade
- Grabs live quote data from Yahoo
- Subscribes to real-time Greeks using Tastytrade's DXFeed
- Merges all data into one CSV for analysis
"""
import os, sys, subprocess, time
import pandas as pd
import yfinance as yf
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from tastytrade.dxfeed import DXLinkStreamer, EventType

# —————————————————————————————————————————————
# CONFIGURE your tickers here:
TICKERS = [
    'NVDA','LMT','ISRG','HLX','TSLA','COIN','RBLX','Z','AVAV',
    'DE','SYM','RXRX','GOOGL','PLTR','UPST'
]
# —————————————————————————————————————————————

def get_session():
    user, pw = os.getenv('TASTYTRADE_USER'), os.getenv('TASTYTRADE_PASS')
    if not user or not pw:
        print("ERROR: set TASTYTRADE_USER & TASTYTRADE_PASS")
        sys.exit(1)
    return Session(user, pw)

def fetch_metadata_df(session, ticker):
    print(f"Fetching metadata for {ticker}...")
    try:
        chain = get_option_chain(session, ticker)
    except Exception as e:
        print(f"  ⚠️  {e}")
        return pd.DataFrame()
    rows = []
    for exp_date, opts in chain.items():
        exp = exp_date.isoformat()
        for opt in opts:
            raw = opt.model_dump()
            base = {
                'ticker': ticker,
                'expiration': exp,
                'strike_price': raw['strike_price'],
                'option_type': raw['option_type'],
                'symbol': raw['symbol'],
                'streamer_symbol': raw.get('streamer_symbol') or f".{raw['symbol']}"
            }
            rows.append(base)
    df = pd.DataFrame(rows)
    print(f"  → {len(df)} chain rows")
    return df

def fetch_market_df(ticker):
    print(f"Fetching market data for {ticker}...")
    tk = yf.Ticker(ticker)
    exps = getattr(tk, 'options', []) or []
    all_rows = []
    for exp in exps:
        try:
            chain = tk.option_chain(exp)
        except:
            continue
        for side, df_side in [('CALL', chain.calls), ('PUT', chain.puts)]:
            if df_side.empty: continue
            df2 = df_side.copy()
            df2['ticker'], df2['expiration'], df2['option_type'] = ticker, exp, side.title()
            df2.rename(columns={
                'strike':'strike_price',
                'lastPrice':'last',
                'openInterest':'open_interest',
                'impliedVolatility':'implied_volatility'
            }, inplace=True)
            cols = ['ticker','expiration','strike_price','option_type',
                    'bid','ask','last','volume','open_interest','implied_volatility']
            all_rows.append(df2[cols])
    if not all_rows:
        return pd.DataFrame()
    mdf = pd.concat(all_rows, ignore_index=True)
    print(f"  → {len(mdf)} market rows")
    return mdf

def subscribe_greeks(streamer_symbols):
    print("Subscribing to Greeks...")
    streamer = DXLinkStreamer()
    streamer.subscribe(EventType.GREEKS, streamer_symbols)
    time.sleep(4)  # Allow time for data to stream in
    greeks = streamer.greeks
    greek_rows = []
    for symbol, g in greeks.items():
        greek_rows.append({
            'streamer_symbol': symbol,
            'delta': g.delta,
            'gamma': g.gamma,
            'theta': g.theta,
            'vega': g.vega,
            'rho': g.rho,
            'theoretical_price': g.price
        })
    return pd.DataFrame(greek_rows)

def main():
    sess = get_session()
    all_meta, all_market = [], []

    for t in TICKERS:
        m = fetch_metadata_df(sess, t)
        if not m.empty: all_meta.append(m)
        q = fetch_market_df(t)
        if not q.empty: all_market.append(q)

    if not all_meta:
        print("No metadata fetched; aborting.")
        sys.exit(1)

    meta_df = pd.concat(all_meta, ignore_index=True)
    market_df = pd.concat(all_market, ignore_index=True) if all_market else pd.DataFrame()

    greeks_df = subscribe_greeks(meta_df['streamer_symbol'].dropna().unique().tolist())

    # Merge all 3 datasets
    merged = pd.merge(meta_df, greeks_df, on='streamer_symbol', how='left')
    if not market_df.empty:
        merged = pd.merge(merged, market_df, on=['ticker','expiration','strike_price','option_type'], how='left')

    final_csv = 'options_report.csv'
    merged.to_csv(final_csv, index=False)
    print(f"✅ Saved full options report to {final_csv} ({len(merged)} rows)")

    if os.path.exists(final_csv):
        subprocess.run(['open', final_csv], check=False)

if __name__ == '__main__':
    main()
````


#### Download the Files

````bash
python3 full_options_report.py
````

# 📂  Data Join: TastyTrade and yfinance

#### Produce Linked Report and calculations

````bash
import pandas as pd
import numpy as np
from scipy.stats import norm

# Load original CSVs
meta_df = pd.read_csv("metadata.csv")
market_df = pd.read_csv("market_data.csv")

# Normalize option type for join
meta_df['option_type'] = meta_df['option_type'].replace({'C': 'Call', 'P': 'Put'})

# Merge metadata + market data
merged = pd.merge(meta_df, market_df, on=['ticker','expiration','strike_price','option_type'], how='inner')

# Add days to expiration if missing
if 'days_to_expiration' not in merged.columns:
    merged['days_to_expiration'] = (
        pd.to_datetime(merged['expiration']) - pd.Timestamp.now()
    ).dt.days.clip(lower=1)

# Estimate spot prices from bid/ask or last
market_df['mid'] = (market_df['bid'] + market_df['ask']) / 2
spot_by_mid = market_df.groupby('ticker')['mid'].median()
spot_by_last = market_df.groupby('ticker')['last'].median()

spot_estimates = {}
for ticker in set(spot_by_mid.index).union(spot_by_last.index):
    spot_estimates[ticker] = (
        spot_by_mid.get(ticker)
        if not pd.isna(spot_by_mid.get(ticker))
        else spot_by_last.get(ticker)
    )

# Greek + PoP calculation
def calculate_greeks(row, S, r=0.03):
    K = row['strike_price']
    T = float(row['days_to_expiration']) / 365
    iv = float(row.get('implied_volatility', 0.30))
    if iv < 0.0001: iv = 0.30

    d1 = (np.log(S / K) + (r + 0.5 * iv**2) * T) / (iv * np.sqrt(T))
    d2 = d1 - iv * np.sqrt(T)

    if row['option_type'] == 'Call':
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * iv / (2 * np.sqrt(T))) - r * K * np.exp(-r*T) * norm.cdf(d2)
        vega = S * norm.pdf(d1) * np.sqrt(T)
        gamma = norm.pdf(d1) / (S * iv * np.sqrt(T))
        rho = K * T * np.exp(-r*T) * norm.cdf(d2)
        pop = norm.cdf((S - K) / (iv * S * np.sqrt(T)))
    else:
        delta = -norm.cdf(-d1)
        theta = (-S * norm.pdf(d1) * iv / (2 * np.sqrt(T))) + r * K * np.exp(-r*T) * norm.cdf(-d2)
        vega = S * norm.pdf(d1) * np.sqrt(T)
        gamma = norm.pdf(d1) / (S * iv * np.sqrt(T))
        rho = -K * T * np.exp(-r*T) * norm.cdf(-d2)
        pop = norm.cdf((K - S) / (iv * S * np.sqrt(T)))

    return pd.Series([delta, gamma, theta, vega, rho, pop],
                     index=['delta','gamma','theta','vega','rho','pop_estimate'])

# Apply calculations row by row
greeks = []
for _, row in merged.iterrows():
    spot = spot_estimates.get(row['ticker'], None)
    if spot is None: continue
    greeks.append(calculate_greeks(row, spot))

# Combine results
greeks_df = pd.DataFrame(greeks)
final_df = pd.concat([merged.reset_index(drop=True), greeks_df.reset_index(drop=True)], axis=1)

# Export final CSV
final_df.to_csv("final_options_report_full_columns.csv", index=False)
print("✅ CSV saved: final_options_report_full_columns.csv")
````

#### Run Data Query 
````bash
python3 generate_final_options_report.py
````



# 🤖 Project Prompt: AI Pick 3 Trades 
**Attachment**  
**Instructions**  
**Goal** Select **exactly 3** option trades from the AI‑optimized 9‑ticker portfolio (Prompt 1) that each target ≥ 33% return and ≥ 66% POP, with max loss ≤ $500, while respecting portfolio Greek and sector limits.  

#### Data Inputs  
- **Underlying Pool:** 9‑ticker sector‑diversified AI portfolio (from Prompt 1)  
- **Market Data:** TastyTrade options chains + Yahoo Finance pricing/IV  

#### Selection Criteria  
1. **POP ≥ 0.66**  
2. **Credit/Max‑Loss ≥ 0.33** (for credit strategies)  
3. **Max loss ≤ $500** per trade  
4. **Implied Volatility ≥ 30%**, **IV Rank ≥ 30%**  
5. **Open Interest ≥ 1,000** per leg  
6. **Bid/Ask Spread ≤ $0.10**  
7. **Contract Cost ≤ $500**  
8. **Quote Age ≤ 10 min**  

#### Portfolio Constraints  
- **Max 2 trades per GICS sector**  
- **Net Delta** ∈ [–0.30, +0.30] × (NAV/100k)  
- **Net Vega ≥ –0.05** × (NAV/100k)  

#### Scoring Weights  
- **POP:** 40%  
- **Expected Return:** 30%  
- **momentum_z:** 20%  
- **flow_z:** 10%  

#### Trade Buckets & Allowed Strategies  
- **DTE Buckets:** 0–9 (Day Trades), 9–27 (Short Premium), 18–45 (Directional Swing), Event Plays (earnings/catalyst + up to 9 DTE)  
- **Strategies:** Vertical spreads, Iron condors, Straddles/strangles, Long calls/puts

#### Output Table Schema
| Ticker | Strategy | Legs | Thesis (≤ 30 words) | POP | Credit/Max‑Loss | DTE | Sector |  

---

### Prompt:  
Apply **the Instructions** to the attached data. Filter, score (POP 40%, Return 30%, momentum_z 20%, flow_z 10%), rank, enforce sector/Greek limits, and **output only** the clean, markdown‑wrapped table with columns:  
`Ticker, Strategy, Legs, Thesis (≤ 30 words), POP, Credit/Max‑Loss, DTE, Sector`.  
