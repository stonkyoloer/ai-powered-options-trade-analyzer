# ⬇️ AI Options Portfolio & Daily Trade Screener

## 📖 What This Does
This workflow builds an **AI‑driven trading portfolio** and screens for the day’s top option trades.  
It:
1. Selects **9 AI-focused stocks** across multiple sectors.
2. Pulls **live option chain and Greeks data** from Tastytrade.
3. Filters and ranks option trades using **defined rules and real‑time risk metrics**.
4. Outputs the **Top 3 highest‑probability trades** in a clean table.

The goal is to remove noise, automate the heavy data lifting, and focus only on **high‑quality trades with clear probabilities and defined risk**.

---

## 🧠 Why Build This?
- **Massive option universe:** Thousands of tickers and millions of option combinations exist daily. This workflow narrows focus to **AI sector leaders only**.
- **Objective filtering:** Uses liquidity, volatility, and momentum rules to eliminate weak setups.
- **Greeks integration:** Delta, Gamma, Theta, Vega are pulled live so trades are grounded in real risk data.
- **Risk control:** Only trades with high probability of profit and defined max loss are shown.

---




# 1️⃣  Collect Data


# 2️⃣  Prompt AI

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


# 3️⃣ TastyTrade API Connection 

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

# 4️⃣ TastyTrade (15 Min Delayed) Data | Unfunded Account

## Create a File 
```bash
touch delayed_data.py
open -e delayed_data.py
```

## Save the Script

```bash
#!/usr/bin/env python3
"""
TASTYTRADE PRODUCTION DATA EXTRACTOR
SUCCESS: Now extracts real delayed market data from TastyTrade!

✅ Working Features:
- DXLink WebSocket protocol
- COMPACT data format parsing
- Real delayed quotes (15-min delay)
- Quote data: bid/ask/spreads
- Trade data: last/change/volume
- Multiple symbols support

Data Sources:
- Market metrics (IV, liquidity)
- WebSocket quotes (bid/ask/last)
- Option chains
- All saved to JSON
"""

import asyncio
import json
import websockets
from datetime import datetime
from decimal import Decimal
import warnings
from tastytrade import Session
from tastytrade.instruments import get_option_chain, Option, Equity

warnings.filterwarnings('ignore')

class TastyTradeProductionExtractor:
    def __init__(self, username: str, password: str):
        self.session = Session(username, password)
        self.websocket_token = None
        
    async def get_websocket_token(self, symbols: list):
        """Retrieve WebSocket token from /api-quote-tokens"""
        try:
            symbol_str = ','.join(symbols)
            response = await self.session.async_client.get(f"https://api.tastyworks.com/api-quote-tokens?symbols={symbol_str}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'token' in data['data']:
                    self.websocket_token = data['data']['token']
                    print(f"🎫 WebSocket token retrieved")
                    return True
            print(f"❌ Failed to get WebSocket token")
            return False
        except Exception as e:
            print(f"⚠️ Token error: {e}")
            return False

    async def get_market_data(self, symbols: list):
        """Get market metrics and instrument data"""
        print(f"📊 Fetching market data for {len(symbols)} symbols...")
        
        market_data = {}
        for symbol in symbols:
            market_data[symbol] = {
                'market_metrics': {},
                'instrument_info': {}
            }
            
            # Market metrics
            try:
                response = await self.session.async_client.get(f"https://api.tastyworks.com/market-metrics?symbols={symbol}")
                if response.status_code == 200:
                    data = response.json()
                    market_data[symbol]['market_metrics'] = data
                    if 'data' in data and 'items' in data['data']:
                        for item in data['data']['items']:
                            if item.get('symbol') == symbol:
                                iv = item.get('implied-volatility-index', 0)
                                liquidity = item.get('liquidity-rating', 0)
                                iv_pct = float(iv) * 100 if iv else 0
                                print(f"   {symbol}: IV={iv_pct:.1f}%, Liquidity={liquidity}")
            except Exception as e:
                print(f"   ⚠️ {symbol} market metrics error: {e}")
            
            # Instrument info
            try:
                response = await self.session.async_client.get(f"https://api.tastyworks.com/instruments/equities/{symbol}")
                if response.status_code == 200:
                    data = response.json()
                    market_data[symbol]['instrument_info'] = data
            except Exception as e:
                print(f"   ⚠️ {symbol} instrument error: {e}")
            
            await asyncio.sleep(0.1)  # Rate limiting
        
        return market_data

    async def stream_delayed_quotes(self, symbols: list, duration_seconds: int = 30):
        """Stream delayed quotes using DXLink WebSocket with COMPACT format parsing"""
        print(f"\n📺 Streaming delayed quotes for {duration_seconds} seconds...")
        
        # Get WebSocket token
        if not await self.get_websocket_token(symbols):
            return {}
        
        collected_data = {symbol: {'quotes': [], 'trades': []} for symbol in symbols}
        
        try:
            dxlink_url = self.session.dxlink_url
            headers = [('Authorization', f'Bearer {self.websocket_token}')]
            
            async with websockets.connect(dxlink_url, additional_headers=headers) as websocket:
                print(f"✅ Connected to delayed feed")
                
                # DXLink Protocol Flow
                
                # 1. SETUP
                setup_msg = {
                    "type": "SETUP",
                    "channel": 0,
                    "keepaliveTimeout": 60,
                    "acceptKeepaliveTimeout": 5,
                    "version": "0.1-DXLink-JS/8.0.0"
                }
                await websocket.send(json.dumps(setup_msg))
                await websocket.recv()  # Setup response
                
                # 2. AUTHENTICATE
                auth_msg = {
                    "type": "AUTH",
                    "channel": 0,
                    "token": self.websocket_token
                }
                await websocket.send(json.dumps(auth_msg))
                
                # Wait for AUTHORIZED state
                auth_success = False
                for _ in range(3):
                    auth_response = await websocket.recv()
                    auth_data = json.loads(auth_response)
                    if auth_data.get('type') == 'AUTH_STATE' and auth_data.get('state') == 'AUTHORIZED':
                        auth_success = True
                        print(f"🔑 Authentication successful")
                        break
                
                if not auth_success:
                    print(f"❌ Authentication failed")
                    return collected_data
                
                # 3. OPEN CHANNEL
                channel_msg = {
                    "type": "CHANNEL_REQUEST",
                    "channel": 1,
                    "service": "FEED",
                    "parameters": {"contract": "TICKER"}
                }
                await websocket.send(json.dumps(channel_msg))
                await websocket.recv()  # Channel opened response
                
                # 4. SUBSCRIBE TO SYMBOLS
                for symbol in symbols:
                    sub_msg = {
                        "type": "FEED_SUBSCRIPTION",
                        "channel": 1,
                        "add": [
                            {"symbol": symbol, "type": "Quote"},
                            {"symbol": symbol, "type": "Trade"}
                        ]
                    }
                    await websocket.send(json.dumps(sub_msg))
                    await asyncio.sleep(0.05)
                
                print(f"📤 Subscribed to {', '.join(symbols)}")
                
                # 5. COLLECT DATA
                start_time = datetime.now()
                quote_count = 0
                trade_count = 0
                
                while (datetime.now() - start_time).total_seconds() < duration_seconds:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        parsed = json.loads(message)
                        
                        if parsed.get('type') == 'FEED_DATA':
                            data_items = parsed.get('data', [])
                            
                            if len(data_items) >= 2:
                                event_type = data_items[0]
                                event_data = data_items[1]
                                
                                if event_type == "Quote" and len(event_data) >= 13:
                                    # COMPACT Quote: [eventType, symbol, eventTime, sequence, timeNanoPart, bidTime, bidExchangeCode, bidPrice, bidSize, askTime, askExchangeCode, askPrice, askSize]
                                    symbol = event_data[1]
                                    bid_price = event_data[7]
                                    bid_size = event_data[8]
                                    ask_price = event_data[11]
                                    ask_size = event_data[12]
                                    
                                    quote_data = {
                                        'timestamp': datetime.now().isoformat(),
                                        'symbol': symbol,
                                        'bid': bid_price,
                                        'ask': ask_price,
                                        'bid_size': bid_size,
                                        'ask_size': ask_size,
                                        'spread': round(ask_price - bid_price, 2) if ask_price and bid_price else None,
                                        'mid': round((ask_price + bid_price) / 2, 2) if ask_price and bid_price else None
                                    }
                                    
                                    if symbol in symbols:
                                        collected_data[symbol]['quotes'].append(quote_data)
                                        quote_count += 1
                                        if quote_count % 10 == 1:  # Print every 10th quote
                                            print(f"📊 {symbol}: Bid=${bid_price}, Ask=${ask_price}, Spread=${quote_data['spread']}")
                                
                                elif event_type == "Trade" and len(event_data) >= 12:
                                    # COMPACT Trade: [eventType, symbol, eventTime, time, timeNanoPart, sequence, exchangeCode, price, change, size, dayId, dayVolume, dayTurnover, ...]
                                    symbol = event_data[1]
                                    price = event_data[7]
                                    change = event_data[8]
                                    day_volume = event_data[11]
                                    
                                    trade_data = {
                                        'timestamp': datetime.now().isoformat(),
                                        'symbol': symbol,
                                        'last': price,
                                        'change': change,
                                        'day_volume': day_volume
                                    }
                                    
                                    if symbol in symbols:
                                        collected_data[symbol]['trades'].append(trade_data)
                                        trade_count += 1
                                        if trade_count % 5 == 1:  # Print every 5th trade
                                            print(f"🔄 {symbol}: Last=${price}, Change=${change}")
                        
                        elif parsed.get('type') == 'KEEPALIVE':
                            # Respond to keepalive
                            keepalive_response = {"type": "KEEPALIVE", "channel": 0}
                            await websocket.send(json.dumps(keepalive_response))
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"⚠️ Message error: {e}")
                
                print(f"\n✅ Data collection complete!")
                print(f"   📊 Quotes collected: {quote_count}")
                print(f"   🔄 Trades collected: {trade_count}")
                
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
        
        return collected_data

    async def get_option_chains(self, symbols: list):
        """Get option chain data for symbols"""
        print(f"\n⛓️ Fetching option chains...")
        
        option_data = {}
        for symbol in symbols[:2]:  # Limit to first 2 symbols for speed
            try:
                chain = get_option_chain(self.session, symbol)
                option_data[symbol] = {
                    'total_contracts': len(chain),
                    'sample_contracts': []
                }
                
                # Get sample of nearest expiration options
                for option in chain[:10]:
                    option_info = {
                        'symbol': option.symbol,
                        'strike': float(option.strike_price),
                        'expiration': str(option.expiration_date),
                        'type': option.option_type.value,
                        'days_to_expiry': option.days_to_expiration
                    }
                    option_data[symbol]['sample_contracts'].append(option_info)
                
                print(f"   {symbol}: {len(chain)} option contracts")
                
            except Exception as e:
                print(f"   ⚠️ {symbol} option chain error: {e}")
                option_data[symbol] = {'error': str(e)}
        
        return option_data

    async def comprehensive_data_extraction(self, symbols: list, stream_duration: int = 60):
        """Extract all available TastyTrade data"""
        print(f"🚀 TASTYTRADE COMPREHENSIVE DATA EXTRACTION")
        print(f"   Symbols: {', '.join(symbols)}")
        print(f"   Stream Duration: {stream_duration} seconds")
        print(f"   Feed Type: DELAYED (15-minute delay)")
        print("="*60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'symbols': symbols,
            'feed_type': 'delayed',
            'account_type': 'demo' if self.session.is_test else 'live',
            'market_data': {},
            'streaming_data': {},
            'option_chains': {}
        }
        
        # Phase 1: Market Data
        results['market_data'] = await self.get_market_data(symbols)
        
        # Phase 2: Streaming Quotes
        results['streaming_data'] = await self.stream_delayed_quotes(symbols, stream_duration)
        
        # Phase 3: Option Chains
        results['option_chains'] = await self.get_option_chains(symbols)
        
        return results

    def analyze_and_save(self, data: dict):
        """Analyze collected data and save to file"""
        print(f"\n💾 ANALYZING AND SAVING DATA")
        print("="*40)
        
        # Save raw data
        filename = f"tastytrade_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"📁 Raw data saved: {filename}")
        
        # Analysis
        symbols = data.get('symbols', [])
        streaming_data = data.get('streaming_data', {})
        
        print(f"\n📊 DATA ANALYSIS:")
        for symbol in symbols:
            if symbol in streaming_data:
                quotes = streaming_data[symbol].get('quotes', [])
                trades = streaming_data[symbol].get('trades', [])
                
                print(f"\n   {symbol}:")
                print(f"      Quotes received: {len(quotes)}")
                print(f"      Trades received: {len(trades)}")
                
                if quotes:
                    latest_quote = quotes[-1]
                    print(f"      Latest quote: Bid=${latest_quote.get('bid')}, Ask=${latest_quote.get('ask')}")
                    print(f"      Spread: ${latest_quote.get('spread')}")
                
                if trades:
                    latest_trade = trades[-1]
                    print(f"      Latest trade: ${latest_trade.get('last')} (change: ${latest_trade.get('change')})")
        
        # Market metrics summary
        market_data = data.get('market_data', {})
        print(f"\n📈 MARKET METRICS:")
        for symbol in symbols:
            if symbol in market_data:
                metrics = market_data[symbol].get('market_metrics', {})
                if 'data' in metrics and 'items' in metrics['data']:
                    for item in metrics['data']['items']:
                        if item.get('symbol') == symbol:
                            iv = item.get('implied-volatility-index', 0)
                            liquidity = item.get('liquidity-rating', 0)
                            iv_pct = float(iv) * 100 if iv else 0
                            print(f"   {symbol}: IV={iv_pct:.1f}%, Liquidity={liquidity}/5")
        
        # Option chains summary
        option_chains = data.get('option_chains', {})
        print(f"\n⛓️ OPTION CHAINS:")
        for symbol, chain_data in option_chains.items():
            if 'total_contracts' in chain_data:
                print(f"   {symbol}: {chain_data['total_contracts']} contracts available")
        
        return filename

async def main():
    """Main execution function"""
    print("🚀 TastyTrade Production Data Extractor")
    print("="*50)
    
    # Configuration
    username = input("Enter TastyTrade username: ")
    password = input("Enter TastyTrade password: ")
    
    # Symbols to extract (can customize)
    symbols = ['SPY', 'QQQ', 'AAPL', 'TSLA']
    stream_duration = 45  # seconds
    
    try:
        print(f"\n🔐 Connecting to TastyTrade...")
        extractor = TastyTradeProductionExtractor(username, password)
        print(f"✅ Connected successfully!")
        
        # Run comprehensive extraction
        results = await extractor.comprehensive_data_extraction(symbols, stream_duration)
        
        # Analyze and save
        filename = extractor.analyze_and_save(results)
        
        print(f"\n🎉 EXTRACTION COMPLETE!")
        print(f"📁 Data saved to: {filename}")
        print(f"💡 Successfully extracted TastyTrade delayed market data!")
        print(f"🔄 Run again anytime to get fresh data")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```






# 4️⃣ TastyTrade LIVE Data | Funded Account


### Create a File

```bash
name here
```

```bash
#!/usr/bin/env python3
"""
TASTYTRADE REAL-TIME DATA ANALYZER
Optimized for funded accounts with live market data

What real-time data gives you:
1. Live bid/ask spreads for precise entry/exit
2. Real-time Greeks for dynamic hedging
3. Current implied volatility for volatility trading
4. Live volume for momentum analysis
5. Instant market efficiency detection

Run this when your $25 deposit clears!

Created: 2025-07-28
"""

import pandas as pd
from datetime import datetime, time
import asyncio
import warnings
import time as time_module
from decimal import Decimal
import numpy as np

# Core TastyTrade imports
from tastytrade import Session
from tastytrade.instruments import get_option_chain, Equity

# Optional streaming imports (for advanced real-time)
try:
    from tastytrade import DXLinkStreamer
    from tastytrade.dxfeed import Greeks, Quote, Trade
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

# Optional Black-Scholes for comparison
try:
    from py_vollib.black_scholes.greeks.analytical import delta, gamma, theta, vega
    from py_vollib.black_scholes import black_scholes
    from py_vollib.black_scholes.implied_volatility import implied_volatility
    VOLLIB_AVAILABLE = True
except ImportError:
    VOLLIB_AVAILABLE = False

warnings.filterwarnings('ignore')

class Settings:
    """Settings optimized for real-time data analysis"""
    
    # Your TastyTrade login
    USERNAME = "username"
    PASSWORD = "password"
    
    # Focus on highly liquid stocks for real-time analysis
    STOCKS = [
        {"ticker": "SPY", "name": "SPDR S&P 500"},      # Highest liquidity
        {"ticker": "QQQ", "name": "Invesco QQQ"},       # High tech liquidity
        {"ticker": "NVDA", "name": "NVIDIA"},           # Your favorite
        {"ticker": "TSLA", "name": "Tesla"},            # High volatility
        {"ticker": "AAPL", "name": "Apple"},            # Consistent liquidity
        {"ticker": "AMZN", "name": "Amazon"},           # Large options market
    ]
    
    # Real-time analysis parameters (focus on near-term for best data)
    MIN_DAYS_TO_EXPIRATION = 1
    MAX_DAYS_TO_EXPIRATION = 45
    
    # Real-time thresholds
    MIN_VOLUME = 50                    # Focus on active options
    MIN_OPEN_INTEREST = 100           # Ensure liquidity
    MAX_BID_ASK_SPREAD_PERCENT = 10   # Filter out illiquid options
    
    # Risk-free rate
    RISK_FREE_RATE = 0.045
    
    # Market hours
    MARKET_OPEN = time(9, 30)
    MARKET_CLOSE = time(16, 0)

def convert_decimal(value):
    """Convert Decimal to float safely"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value

def is_market_hours():
    """Check if markets are currently open"""
    now = datetime.now().time()
    return Settings.MARKET_OPEN <= now <= Settings.MARKET_CLOSE

def calculate_bid_ask_spread(bid, ask):
    """Calculate bid-ask spread percentage"""
    if not bid or not ask or ask <= 0:
        return None
    return ((ask - bid) / ask) * 100

def calculate_implied_vol_from_price(market_price, stock_price, strike, time_to_exp, risk_free_rate, option_type):
    """Calculate implied volatility from market price"""
    if not VOLLIB_AVAILABLE or not all([market_price, stock_price, strike, time_to_exp]):
        return None
    
    try:
```





### Create a File
```bash
touch select_top_trades.py
open -e select_top_trades.py
```

### Save the Script
```python
#!/usr/bin/env python3
"""
OPTIONS TRADING PLATFORM
Imports all option data from TastyTrade API

What this does:
1. Gets all option data for specified stocks from TastyTrade
2. Saves everything to CSV files for analysis
3. Logs raw option attributes for debugging

Created: 2025-07-27
"""

import pandas as pd
from datetime import datetime
import asyncio
import json
import warnings
import os
import time

# API connections
from tastytrade import Session
from tastytrade.instruments import get_option_chain, Equity

warnings.filterwarnings('ignore')

# SETTINGS
class Settings:
    """Main settings for the platform"""
    
    # Your TastyTrade login
    USERNAME = "username"
    PASSWORD = "password"
    
    # TastyTrade API base URL
    API_BASE_URL = "https://api.tastyworks.com"
    
    # Which stocks to analyze
    STOCKS = [
        {"ticker": "NVDA", "name": "NVIDIA"},
        {"ticker": "ISRG", "name": "Intuitive Surgical"}, 
        {"ticker": "PLTR", "name": "Palantir"},
        {"ticker": "TSLA", "name": "Tesla"},
        {"ticker": "AMZN", "name": "Amazon"},
        {"ticker": "ENPH", "name": "Enphase Energy"},
        {"ticker": "XOM", "name": "Exxon Mobil"},
        {"ticker": "DE", "name": "John Deere"},
        {"ticker": "CAT", "name": "Caterpillar"}
    ]
    
    # Trading rules
    MIN_DAYS_TO_EXPIRATION = 0      # Include all expirations
    MAX_DAYS_TO_EXPIRATION = 99     # Up to 99 days out

# GET DATA FROM TASTYTRADE
class DataFetcher:
    """Gets option data from TastyTrade"""
    
    def __init__(self):
        self.session = None
        self.session_token = None
        
    async def connect(self):
        """Connect to TastyTrade"""
        print("Connecting to TastyTrade...")
        
        try:
            self.session = Session(Settings.USERNAME, Settings.PASSWORD)
            self.session_token = self.session.session_token
            print(f"Connected successfully, session token: {self.session_token[:10]}...")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_stock_info(self, ticker):
        """Get basic stock information"""
        try:
            # Get basic stock information
            stock = Equity.get(self.session, ticker)
            
            info = {
                "ticker": stock.symbol,
                "company_name": stock.description,
                "exchange": stock.listed_market,
                "active": stock.active
            }
            
            # Refresh session token
            try:
                self.session = Session(Settings.USERNAME, Settings.PASSWORD)
                self.session_token = self.session.session_token
                print(f"Refreshed session token for {ticker}: {self.session_token[:10]}...")
            except Exception as e:
                print(f"Failed to refresh session token for {ticker}: {e}")
            
            # Add delay to avoid rate limits
            time.sleep(2)
            
            return info
            
        except Exception as e:
            print(f"Error getting stock info for {ticker}: {e}")
            return None
    
    def get_all_options(self, ticker, stock_info):
        """Get all option contracts for a stock"""
        print(f"\nGetting options for {ticker} ({stock_info['company_name']})")
        
        try:
            # Get the complete option chain
            chain = get_option_chain(self.session, ticker)
            print(f"Found {len(chain)} expiration dates")
            
            # Filter by days to expiration
            valid_options = []
            
            for exp_date, option_list in chain.items():
                # Calculate days to expiration
                if isinstance(exp_date, str):
                    exp_dt = datetime.strptime(exp_date, "%Y-%m-%d")
                else:
                    exp_dt = exp_date
                exp_dt = datetime.combine(exp_dt, datetime.min.time())
                days_left = (exp_dt - datetime.now()).days
                
                # Only include options within our date range
                if Settings.MIN_DAYS_TO_EXPIRATION <= days_left <= Settings.MAX_DAYS_TO_EXPIRATION:
                    print(f"  {exp_date}: {days_left} days, {len(option_list)} options")
                    
                    # Process each option contract
                    for option in option_list:
                        contract = self._process_option_contract(
                            option, exp_date, days_left, stock_info
                        )
                        if contract:
                            valid_options.append(contract)
            
            print(f"Processed {len(valid_options)} total option contracts")
            return pd.DataFrame(valid_options) if valid_options else pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting options for {ticker}: {e}")
            return pd.DataFrame()
    
    def _process_option_contract(self, option, exp_date, days_left, stock_info):
        """Process a single option contract"""
        try:
            from decimal import Decimal
            
            def convert_decimal(value):
                """Convert Decimal to float, handle None values"""
                if value is None:
                    return None
                if isinstance(value, Decimal):
                    return float(value)
                return value
            
            strike = float(option.strike_price)
            option_type = "Call" if option.option_type.value == "C" else "Put"
            
            # Log raw option attributes for debugging - convert Decimals for JSON serialization
            option_attrs = {
                "symbol": option.symbol,
                "strike_price": convert_decimal(option.strike_price),
                "option_type": option.option_type.value,
                "expiration_date": str(exp_date),
                "bid": convert_decimal(getattr(option, 'bid', None)),
                "ask": convert_decimal(getattr(option, 'ask', None)),
                "last": convert_decimal(getattr(option, 'last', None)),
                "mark": convert_decimal(getattr(option, 'mark', None)),
                "volume": convert_decimal(getattr(option, 'volume', None)),
                "open_interest": convert_decimal(getattr(option, 'open_interest', None)),
                "delta": convert_decimal(getattr(option, 'delta', None)),
                "gamma": convert_decimal(getattr(option, 'gamma', None)),
                "theta": convert_decimal(getattr(option, 'theta', None)),
                "vega": convert_decimal(getattr(option, 'vega', None)),
                "implied_volatility": convert_decimal(getattr(option, 'implied_volatility', None)),
                "in_the_money": getattr(option, 'in_the_money', None),
                "multiplier": convert_decimal(getattr(option, 'multiplier', None)),
                "contract_size": convert_decimal(getattr(option, 'contract_size', None))
            }
            print(f"Option {option.symbol} (exp {exp_date}): {json.dumps(option_attrs, indent=2)}")
            
            contract = {
                # Basic info
                "ticker": stock_info["ticker"],
                "company_name": stock_info["company_name"],
                "option_symbol": option.symbol,
                "expiration_date": exp_date,
                "days_to_expiration": days_left,
                "time_to_expiration_years": max(days_left / 365.0, 1/365),
                "strike_price": strike,
                "option_type": option_type,
                
                # Market data
                "bid_price": convert_decimal(getattr(option, 'bid', None)),
                "ask_price": convert_decimal(getattr(option, 'ask', None)),
                "last_price": convert_decimal(getattr(option, 'last', None)),
                "mark_price": convert_decimal(getattr(option, 'mark', None)),
                "volume": int(option.volume) if hasattr(option, 'volume') and option.volume is not None else None,
                "open_interest": int(option.open_interest) if hasattr(option, 'open_interest') and option.open_interest is not None else None,
                
                # Greeks
                "delta": convert_decimal(getattr(option, 'delta', None)),
                "gamma": convert_decimal(getattr(option, 'gamma', None)),
                "theta": convert_decimal(getattr(option, 'theta', None)),
                "vega": convert_decimal(getattr(option, 'vega', None)),
                "implied_volatility": convert_decimal(getattr(option, 'implied_volatility', None)),
                
                # Additional fields
                "in_the_money": bool(option.in_the_money) if hasattr(option, 'in_the_money') and option.in_the_money is not None else None,
                "multiplier": convert_decimal(getattr(option, 'multiplier', None)),
                "contract_size": convert_decimal(getattr(option, 'contract_size', None)),
                
                # Data status
                "data_timestamp": datetime.now().isoformat()
            }
            
            return contract
            
        except Exception as e:
            print(f"Error processing option contract {option.symbol}: {e}")
            return None

# MAIN PROGRAM
async def main():
    """Main program - imports all option data"""
    
    print("OPTIONS TRADING PLATFORM")
    print("Importing all option data from TastyTrade")
    print("=" * 50)
    print(f"Analyzing {len(Settings.STOCKS)} stocks")
    print(f"Date range: {Settings.MIN_DAYS_TO_EXPIRATION} to {Settings.MAX_DAYS_TO_EXPIRATION} days")
    print("=" * 50)
    
    # Connect to TastyTrade
    fetcher = DataFetcher()
    if not await fetcher.connect():
        print("Exiting due to connection failure. Please check API credentials and try again.")
        return
    
    # Process each stock
    all_results = []
    total_options = 0
    
    for stock_config in Settings.STOCKS:
        ticker = stock_config["ticker"]
        
        print(f"\n" + "="*60)
        print(f"ANALYZING: {ticker} ({stock_config['name']})")
        print("="*60)
        
        # Get stock information
        stock_info = fetcher.get_stock_info(ticker)
        if not stock_info:
            print(f"Skipping {ticker} due to failure in fetching stock info")
            continue
        
        print(f"Company: {stock_info['company_name']}")
        print(f"Exchange: {stock_info['exchange']}")
        
        # Get all option contracts
        options_df = fetcher.get_all_options(ticker, stock_info)
        if options_df.empty:
            print(f"No options data retrieved for {ticker}")
            continue
        
        # Save data
        options_filename = f"{ticker}_all_options.csv"
        options_df.to_csv(options_filename, index=False)
        print(f"Saved all options to: {options_filename}")
        
        # Track results
        all_results.append({
            'ticker': ticker,
            'company': stock_info['company_name'],
            'total_options': len(options_df)
        })
        
        total_options += len(options_df)
        
        print(f"Results: {len(options_df)} options")
    
    # Final summary
    print(f"\n" + "="*60)
    print(f"FINAL SUMMARY")
    print("="*60)
    
    successful_stocks = [r for r in all_results if r['total_options'] > 0]
    
    print(f"Successfully analyzed: {len(successful_stocks)} stocks")
    print(f"Total option contracts: {total_options:,}")
    
    print(f"\nStock breakdown:")
    for result in all_results:
        if result['total_options'] > 0:
            print(f"  {result['ticker']}: {result['total_options']:,} options")
    
    print(f"\nWhat this platform does:")
    print(f"  - Gets complete option data from TastyTrade")
    print(f"  - Saves everything to CSV files for further analysis")
    
    if total_options == 0:
        print(f"\nNo option data retrieved")
        print(f"    Please verify:")
        print(f"    1. API credentials in Settings.USERNAME and Settings.PASSWORD")
        print(f"    2. Market data access enabled for your TastyTrade account (contact support: api.support@tastytrade.com)")
        print(f"    3. Running during market hours (9:30 AM - 4:00 PM ET, Mon-Fri) for complete data")
        print(f"    If issues persist, check error messages above for specific API response details")

if __name__ == "__main__":
    asyncio.run(main())
```

### Run the Script
```bash
python3 select_top_trades.py
```


# 6️⃣ Calculate Percent Chance of Profit




# 6️⃣ Prompt AI

## 🗂 Attachment
select_top_trades.csv

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

