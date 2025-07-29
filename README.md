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

# 4️⃣ Fetch TastyTrade Data

1. **Import libraries –** Brings in tools we need (async, websockets, json, etc.) so the script can work.
2. **Create class –** Groups all portfolio data functions to keep code organized.
3. **Login & portfolio list –** Logs into TastyTrade and loads tickers so we know what to track.
4. **Get WebSocket token –** Gets a streaming token so we can connect for live quotes.
5. **Fetch market data –** Pulls IV, liquidity, and instrument info to see stock risk and tradability.
6. **Stream quotes –** Connects to WebSocket and listens to bid/ask/last to capture price action.
7. **Get option chains –** Fetches option contracts to see strikes and expirations for trading.
8. **Run full extraction –** Calls all steps together to collect complete portfolio data.
9. **Analyze & save –** Saves data to JSON and prints summary so we can use it later.
10. **Main function –** Runs everything to make the script actually do its job.
11. **Run script –** Starts the program so data extraction happens when we execute it.
---

## 🐢 15 Minute Delayed Data

### Create a File 
```bash
touch delayed_data.py
open -e delayed_data.py
```

### Save the Script (15 min delayed feed)

```bash
#!/usr/bin/env python3
"""
TASTYTRADE PORTFOLIO DATA EXTRACTOR
Extracts real delayed market data from TastyTrade for your portfolio

✅ Working Features:
- DXLink WebSocket protocol
- COMPACT data format parsing
- Real delayed quotes (15-min delay)
- Quote data: bid/ask/spreads
- Trade data: last/change/volume
- Portfolio focus

Data Sources:
- Market metrics (IV, liquidity)
- WebSocket quotes (bid/ask/last)
- Option chains
- All saved to JSON

Portfolio Focus:
- NVDA (NVIDIA)
- ISRG (Intuitive Surgical)
- PLTR (Palantir)  
- TSLA (Tesla)
- AMZN (Amazon)
- ENPH (Enphase Energy)
- XOM (Exxon Mobil)
- DE (John Deere)
- CAT (Caterpillar)
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

class TastyTradePortfolioExtractor:
    def __init__(self, username: str, password: str):
        self.session = Session(username, password)
        self.websocket_token = None
        
        # Your portfolio configuration
        self.portfolio = [
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
        print(f"📊 Fetching market data for {len(symbols)} portfolio symbols...")
        
        market_data = {}
        for symbol in symbols:
            # Find company name from portfolio
            company_name = "Unknown"
            for stock in self.portfolio:
                if stock["ticker"] == symbol:
                    company_name = stock["name"]
                    break
            
            market_data[symbol] = {
                'company_name': company_name,
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
                                print(f"   {symbol} ({company_name}): IV={iv_pct:.1f}%, Liquidity={liquidity}")
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
        print(f"📋 Monitoring: {', '.join(symbols)}")
        
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
                
                print(f"📤 Subscribed to portfolio symbols")
                
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
                                        if quote_count % 15 == 1:  # Print every 15th quote (less spam with more symbols)
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
                                        if trade_count % 10 == 1:  # Print every 10th trade
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
        print(f"\n⛓️ Fetching option chains for portfolio...")
        
        option_data = {}
        
        # Process all symbols but limit details for speed
        for i, symbol in enumerate(symbols):
            try:
                print(f"   Processing {symbol} ({i+1}/{len(symbols)})...")
                
                chain = get_option_chain(self.session, symbol)
                option_data[symbol] = {
                    'total_contracts': len(chain),
                    'sample_contracts': []
                }
                
                # Get sample of nearest expiration options (first 5)
                for option in chain[:5]:
                    option_info = {
                        'symbol': option.symbol,
                        'strike': float(option.strike_price),
                        'expiration': str(option.expiration_date),
                        'type': option.option_type.value,
                        'days_to_expiry': option.days_to_expiration
                    }
                    option_data[symbol]['sample_contracts'].append(option_info)
                
                print(f"      {symbol}: {len(chain)} option contracts available")
                
                # Rate limiting - especially important with more symbols
                await asyncio.sleep(0.2)
                
            except Exception as e:
                print(f"   ⚠️ {symbol} option chain error: {e}")
                option_data[symbol] = {'error': str(e)}
        
        return option_data

    async def comprehensive_data_extraction(self, stream_duration: int = 60):
        """Extract all available TastyTrade data for your portfolio"""
        symbols = [stock["ticker"] for stock in self.portfolio]
        
        print(f"🚀 TASTYTRADE PORTFOLIO DATA EXTRACTION")
        print(f"   Portfolio Symbols: {', '.join(symbols)}")
        print(f"   Stream Duration: {stream_duration} seconds")
        print(f"   Feed Type: DELAYED (15-minute delay)")
        print("="*70)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'portfolio': self.portfolio,
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
        print(f"\n💾 ANALYZING AND SAVING PORTFOLIO DATA")
        print("="*50)
        
        # Save raw data
        filename = f"portfolio_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"📁 Raw data saved: {filename}")
        
        # Analysis
        portfolio = data.get('portfolio', [])
        symbols = data.get('symbols', [])
        streaming_data = data.get('streaming_data', {})
        
        print(f"\n📊 PORTFOLIO DATA ANALYSIS:")
        for i, symbol in enumerate(symbols):
            company_name = portfolio[i]["name"] if i < len(portfolio) else "Unknown"
            
            if symbol in streaming_data:
                quotes = streaming_data[symbol].get('quotes', [])
                trades = streaming_data[symbol].get('trades', [])
                
                print(f"\n   {symbol} ({company_name}):")
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
        print(f"\n📈 PORTFOLIO MARKET METRICS:")
        for symbol in symbols:
            if symbol in market_data:
                company_name = market_data[symbol].get('company_name', 'Unknown')
                metrics = market_data[symbol].get('market_metrics', {})
                if 'data' in metrics and 'items' in metrics['data']:
                    for item in metrics['data']['items']:
                        if item.get('symbol') == symbol:
                            iv = item.get('implied-volatility-index', 0)
                            liquidity = item.get('liquidity-rating', 0)
                            iv_pct = float(iv) * 100 if iv else 0
                            print(f"   {symbol} ({company_name}): IV={iv_pct:.1f}%, Liquidity={liquidity}/5")
        
        # Option chains summary
        option_chains = data.get('option_chains', {})
        print(f"\n⛓️ PORTFOLIO OPTION CHAINS:")
        for symbol, chain_data in option_chains.items():
            if 'total_contracts' in chain_data:
                company_name = next((stock["name"] for stock in portfolio if stock["ticker"] == symbol), "Unknown")
                print(f"   {symbol} ({company_name}): {chain_data['total_contracts']} contracts available")
        
        return filename

async def main():
    """Main execution function"""
    print("🚀 TastyTrade Portfolio Data Extractor")
    print("="*60)
    
    # Configuration
    username = "username"
    password = "password"
    
    # Stream duration (in seconds)
    stream_duration = 45  # Reduced for more symbols
    
    try:
        print(f"\n🔐 Connecting to TastyTrade...")
        extractor = TastyTradePortfolioExtractor(username, password)
        print(f"✅ Connected successfully!")
        
        print(f"\n💼 Your Portfolio:")
        for stock in extractor.portfolio:
            print(f"   {stock['ticker']} - {stock['name']}")
        
        # Run comprehensive extraction
        results = await extractor.comprehensive_data_extraction(stream_duration)
        
        # Analyze and save
        filename = extractor.analyze_and_save(results)
        
        print(f"\n🎉 PORTFOLIO EXTRACTION COMPLETE!")
        print(f"📁 Data saved to: {filename}")
        print(f"💡 Successfully extracted TastyTrade delayed market data for your portfolio!")
        print(f"🔄 Run the trade picker next: python3 credit_spreads_picker.py")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
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

1. **Import libraries** – Brings in math, options API, and analysis tools '**so we can fetch and calculate spreads.**'  
2. **Create `CreditSpread` data class** – Holds details of one trade **to keep trade info neat and structured.**  
3. **Create `CreditSpreadsAnalyzer` class** – Handles all analysis steps **so code stays organized.**  
4. **Login & load data** – Logs into TastyTrade and loads saved market data **so we know current prices and metrics.**  
5. **Utility functions (option type, strike, expiration)** – Pulls key details from option data **to help filter calls vs puts.**  
6. **Black‑Scholes pricing** – Calculates theoretical option prices **to estimate fair premiums.**  
7. **POP (Probability of Profit)** – Calculates chance a trade will profit **so we can filter only good trades.**  
8. **Get symbol data** – Finds price, IV, and liquidity for each stock **so we know trade quality.**  
9. **Flatten option chain** – Converts option data into one simple list **so it’s easier to search.**  
10. **Analyze bull put spreads** – Looks for **put credit spreads** by selling a higher strike put and buying a lower strike put **so we profit if the stock stays above the short strike (bullish).**  
11. **Analyze bear call spreads** – Looks for **call credit spreads** by selling a lower strike call and buying a higher strike call **so we profit if the stock stays below the short strike (bearish).**  
12. **Find all spreads** – Runs both bull put and bear call analysis across all symbols **to build one master list of trade candidates.**  
13. **Rank spreads** – Sorts all trades by confidence, ROI, and POP **so the best setups float to the top.**  
14. **Display results** – Prints the top trades clearly **so we can quickly review and select.**  
15. **Main function** – Loads data, runs analysis, ranks, displays, and saves results **so the workflow runs automatically.**  
16. **Run script** – Executes everything **so trade picking happens when we run the file.**


### Create a File
```bash
touch cs_picker.py
open -e cs_picker.py
```

### Save the Script
```bash
#!/usr/bin/env python3
"""
CREDIT SPREADS ONLY - TASTYTRADE TRADE PICKER
Focused on Bull Put Spreads and Bear Call Spreads

🎯 Target: 33%+ ROI, 66%+ POP
📊 Strategies:
- Bull Put Spreads (Put Credit Spreads)
- Bear Call Spreads (Call Credit Spreads)

Premium selling strategies for consistent income generation.
"""

import json
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from scipy.stats import norm
import numpy as np
from tastytrade import Session
from tastytrade.instruments import get_option_chain, Option

@dataclass
class CreditSpread:
    """Represents a credit spread opportunity"""
    symbol: str
    strategy: str  # "Bull Put Spread" or "Bear Call Spread"
    description: str
    credit_received: float
    max_profit: float
    max_loss: float
    roi: float
    pop: float
    dte: int
    short_strike: float
    long_strike: float
    spread_width: float
    current_price: float
    breakeven: float
    confidence_score: float
    risk_reward_ratio: float
    expiration_date: str

class CreditSpreadsAnalyzer:
    def __init__(self, username: str, password: str, data_file: str = None):
        self.session = Session(username, password)
        self.market_data = {}
        self.risk_free_rate = 0.045
        
        if data_file:
            self.load_market_data(data_file)
    
    def load_market_data(self, filename: str):
        """Load market data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.market_data = data
                print(f"📁 Loaded market data from {filename}")
                return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def get_option_type(self, option) -> str:
        """Extract option type from option object"""
        try:
            if hasattr(option, 'option_type') and hasattr(option.option_type, 'value'):
                return option.option_type.value
            return ''
        except:
            return ''

    def get_strike_price(self, option) -> float:
        """Extract strike price from option object"""
        try:
            if hasattr(option, 'strike_price'):
                return float(option.strike_price)
            return 0.0
        except:
            return 0.0

    def get_expiration_date(self, option):
        """Extract expiration date from option object"""
        try:
            if hasattr(option, 'expiration_date'):
                return option.expiration_date
            return None
        except:
            return None
    
    def calculate_black_scholes_put(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Black-Scholes put option price"""
        if T <= 0:
            return max(K - S, 0)
        
        try:
            d1 = (math.log(S/K) + (r + sigma**2/2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            return max(put_price, 0)
        except:
            return max(K - S, 0)
    
    def calculate_black_scholes_call(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Black-Scholes call option price"""
        if T <= 0:
            return max(S - K, 0)
        
        try:
            d1 = (math.log(S/K) + (r + sigma**2/2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            return max(call_price, 0)
        except:
            return max(S - K, 0)
    
    def calculate_pop_credit_spread(self, current_price: float, short_strike: float, 
                                  iv: float, dte: int, is_put_spread: bool = True) -> float:
        """Calculate Probability of Profit for credit spreads"""
        T = dte / 365.0
        
        try:
            if is_put_spread:
                # Bull Put Spread: profitable if stock stays above short strike
                d = (math.log(current_price / short_strike) + (self.risk_free_rate - iv**2/2) * T) / (iv * math.sqrt(T))
                pop = norm.cdf(d) * 100
            else:
                # Bear Call Spread: profitable if stock stays below short strike  
                d = (math.log(current_price / short_strike) + (self.risk_free_rate - iv**2/2) * T) / (iv * math.sqrt(T))
                pop = norm.cdf(-d) * 100
            
            return min(max(pop, 1), 99)  # Cap between 1% and 99%
        except:
            return 50  # Default to 50% if calculation fails
    
    def get_symbol_data(self, symbol: str) -> Optional[Dict]:
        """Extract current market data for symbol"""
        if symbol not in self.market_data.get('streaming_data', {}):
            return None
            
        streaming = self.market_data['streaming_data'][symbol]
        market_metrics = self.market_data['market_data'].get(symbol, {}).get('market_metrics', {})
        
        quotes = streaming.get('quotes', [])
        trades = streaming.get('trades', [])
        
        if not quotes or not trades:
            return None
            
        latest_quote = quotes[-1]
        latest_trade = trades[-1]
        
        # Extract IV from market metrics
        iv = 0.25  # Default 25%
        liquidity = 3
        
        if 'data' in market_metrics and 'items' in market_metrics['data']:
            for item in market_metrics['data']['items']:
                if item.get('symbol') == symbol:
                    iv_raw = item.get('implied-volatility-index', 0.25)
                    iv = float(iv_raw) if iv_raw else 0.25
                    liquidity = item.get('liquidity-rating', 3)
        
        return {
            'symbol': symbol,
            'current_price': latest_trade.get('last', 0),
            'bid': latest_quote.get('bid', 0),
            'ask': latest_quote.get('ask', 0),
            'spread': latest_quote.get('spread', 0),
            'iv': iv,
            'liquidity': liquidity,
            'change': latest_trade.get('change', 0)
        }
    
    def flatten_option_chain(self, chain):
        """Extract all options from chain structure"""
        all_options = []
        
        if isinstance(chain, dict):
            for exp_date, option_list in chain.items():
                if isinstance(option_list, list):
                    all_options.extend(option_list)
        elif hasattr(chain, '__iter__'):
            for item in chain:
                if isinstance(item, list):
                    all_options.extend(item)
                else:
                    all_options.append(item)
        else:
            all_options = list(chain) if chain else []
        
        return all_options
    
    async def analyze_bull_put_spreads(self, symbol: str, symbol_data: dict, 
                                     target_roi: float = 33, target_pop: float = 66) -> List[CreditSpread]:
        """Find bull put spread opportunities (put credit spreads)"""
        opportunities = []
        current_price = symbol_data['current_price']
        iv = symbol_data['iv']
        
        try:
            chain = get_option_chain(self.session, symbol)
            all_options = self.flatten_option_chain(chain)
            
            # Filter for puts
            puts = [opt for opt in all_options if self.get_option_type(opt) == 'P']
            
            # Group by expiration
            expirations = {}
            for put in puts:
                exp_date = self.get_expiration_date(put)
                if exp_date:
                    if exp_date not in expirations:
                        expirations[exp_date] = []
                    expirations[exp_date].append(put)
            
            print(f"   📊 Analyzing {len(puts)} puts across {len(expirations)} expirations")
            
            # Analyze each expiration (focus on 15-45 DTE)
            for exp_date, exp_puts in expirations.items():
                dte = (exp_date - datetime.now().date()).days
                if dte < 15 or dte > 45:
                    continue
                
                # Sort puts by strike (descending - highest strike first)
                exp_puts.sort(key=lambda x: self.get_strike_price(x), reverse=True)
                
                # Look for bull put spread opportunities
                # Bull Put = Sell higher strike put + Buy lower strike put
                for i in range(min(20, len(exp_puts) - 1)):
                    short_put = exp_puts[i]  # Higher strike (short)
                    short_strike = self.get_strike_price(short_put)
                    
                    if short_strike <= 0:
                        continue
                    
                    # Only consider strikes below current price (out of the money)
                    # Target ~10-20% below current price for good risk/reward
                    if short_strike >= current_price * 0.92:  # No more than 8% below current
                        continue
                    if short_strike < current_price * 0.75:   # No more than 25% below current
                        continue
                    
                    # Look for long puts (lower strikes)
                    for j in range(i + 1, min(i + 10, len(exp_puts))):
                        long_put = exp_puts[j]  # Lower strike (long)
                        long_strike = self.get_strike_price(long_put)
                        
                        if long_strike <= 0:
                            continue
                        
                        spread_width = short_strike - long_strike
                        
                        # Target spread widths: $2.50, $5, $10 (common spreads)
                        if spread_width not in [2.5, 5, 10]:
                            # Allow some flexibility for odd strike spacing
                            if not (2 <= spread_width <= 12):
                                continue
                        
                        # Calculate option prices using Black-Scholes
                        T = dte / 365.0
                        short_put_price = self.calculate_black_scholes_put(
                            current_price, short_strike, T, self.risk_free_rate, iv
                        )
                        long_put_price = self.calculate_black_scholes_put(
                            current_price, long_strike, T, self.risk_free_rate, iv
                        )
                        
                        # Credit received (premium we collect)
                        credit = short_put_price - long_put_price
                        
                        # Skip spreads with very small credits
                        if credit <= 0.15:  # Need at least $15 credit per spread
                            continue
                        
                        # Calculate P&L metrics
                        max_profit = credit * 100  # Per contract
                        max_loss = (spread_width - credit) * 100
                        
                        if max_loss <= 0:
                            continue
                        
                        # ROI calculation
                        roi = (max_profit / max_loss) * 100
                        
                        # Breakeven point
                        breakeven = short_strike - credit
                        
                        # POP calculation
                        pop = self.calculate_pop_credit_spread(current_price, short_strike, iv, dte, True)
                        
                        # Check if meets criteria
                        if roi >= target_roi and pop >= target_pop:
                            # Calculate confidence score
                            liquidity_score = min(symbol_data['liquidity'] / 5.0, 1.0)
                            dte_score = 1.0 - abs(30 - dte) / 30.0  # Prefer ~30 DTE
                            distance_score = min((current_price - short_strike) / current_price * 10, 1.0)  # Prefer OTM
                            iv_score = min(iv / 0.5, 1.0)  # Higher IV = better premiums
                            
                            confidence = (liquidity_score + dte_score + distance_score + iv_score) / 4.0
                            
                            opportunity = CreditSpread(
                                symbol=symbol,
                                strategy="Bull Put Spread",
                                description=f"Sell {short_strike:.0f}P / Buy {long_strike:.0f}P",
                                credit_received=credit,
                                max_profit=max_profit,
                                max_loss=max_loss,
                                roi=roi,
                                pop=pop,
                                dte=dte,
                                short_strike=short_strike,
                                long_strike=long_strike,
                                spread_width=spread_width,
                                current_price=current_price,
                                breakeven=breakeven,
                                confidence_score=confidence,
                                risk_reward_ratio=max_profit / max_loss,
                                expiration_date=str(exp_date)
                            )
                            
                            opportunities.append(opportunity)
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing {symbol} bull put spreads: {e}")
        
        return opportunities
    
    async def analyze_bear_call_spreads(self, symbol: str, symbol_data: dict, 
                                      target_roi: float = 33, target_pop: float = 66) -> List[CreditSpread]:
        """Find bear call spread opportunities (call credit spreads)"""
        opportunities = []
        current_price = symbol_data['current_price']
        iv = symbol_data['iv']
        
        try:
            chain = get_option_chain(self.session, symbol)
            all_options = self.flatten_option_chain(chain)
            
            # Filter for calls
            calls = [opt for opt in all_options if self.get_option_type(opt) == 'C']
            
            # Group by expiration
            expirations = {}
            for call in calls:
                exp_date = self.get_expiration_date(call)
                if exp_date:
                    if exp_date not in expirations:
                        expirations[exp_date] = []
                    expirations[exp_date].append(call)
            
            print(f"   📊 Analyzing {len(calls)} calls across {len(expirations)} expirations")
            
            # Analyze each expiration
            for exp_date, exp_calls in expirations.items():
                dte = (exp_date - datetime.now().date()).days
                if dte < 15 or dte > 45:
                    continue
                
                # Sort calls by strike (ascending - lowest strike first)
                exp_calls.sort(key=lambda x: self.get_strike_price(x))
                
                # Look for bear call spread opportunities
                # Bear Call = Sell lower strike call + Buy higher strike call
                for i in range(min(20, len(exp_calls) - 1)):
                    short_call = exp_calls[i]  # Lower strike (short)
                    short_strike = self.get_strike_price(short_call)
                    
                    if short_strike <= 0:
                        continue
                    
                    # Only consider strikes above current price (out of the money)
                    # Target ~10-20% above current price for good risk/reward
                    if short_strike <= current_price * 1.08:  # At least 8% above current
                        continue
                    if short_strike > current_price * 1.35:   # No more than 35% above current
                        continue
                    
                    # Look for long calls (higher strikes)
                    for j in range(i + 1, min(i + 10, len(exp_calls))):
                        long_call = exp_calls[j]  # Higher strike (long)
                        long_strike = self.get_strike_price(long_call)
                        
                        if long_strike <= 0:
                            continue
                        
                        spread_width = long_strike - short_strike
                        
                        # Target spread widths
                        if spread_width not in [2.5, 5, 10]:
                            if not (2 <= spread_width <= 12):
                                continue
                        
                        # Calculate option prices
                        T = dte / 365.0
                        short_call_price = self.calculate_black_scholes_call(
                            current_price, short_strike, T, self.risk_free_rate, iv
                        )
                        long_call_price = self.calculate_black_scholes_call(
                            current_price, long_strike, T, self.risk_free_rate, iv
                        )
                        
                        # Credit received
                        credit = short_call_price - long_call_price
                        
                        if credit <= 0.15:
                            continue
                        
                        # Calculate P&L metrics
                        max_profit = credit * 100
                        max_loss = (spread_width - credit) * 100
                        
                        if max_loss <= 0:
                            continue
                        
                        # ROI calculation
                        roi = (max_profit / max_loss) * 100
                        
                        # Breakeven point
                        breakeven = short_strike + credit
                        
                        # POP calculation
                        pop = self.calculate_pop_credit_spread(current_price, short_strike, iv, dte, False)
                        
                        # Check if meets criteria
                        if roi >= target_roi and pop >= target_pop:
                            # Calculate confidence score
                            liquidity_score = min(symbol_data['liquidity'] / 5.0, 1.0)
                            dte_score = 1.0 - abs(30 - dte) / 30.0
                            distance_score = min((short_strike - current_price) / current_price * 10, 1.0)
                            iv_score = min(iv / 0.5, 1.0)
                            
                            confidence = (liquidity_score + dte_score + distance_score + iv_score) / 4.0
                            
                            opportunity = CreditSpread(
                                symbol=symbol,
                                strategy="Bear Call Spread",
                                description=f"Sell {short_strike:.0f}C / Buy {long_strike:.0f}C",
                                credit_received=credit,
                                max_profit=max_profit,
                                max_loss=max_loss,
                                roi=roi,
                                pop=pop,
                                dte=dte,
                                short_strike=short_strike,
                                long_strike=long_strike,
                                spread_width=spread_width,
                                current_price=current_price,
                                breakeven=breakeven,
                                confidence_score=confidence,
                                risk_reward_ratio=max_profit / max_loss,
                                expiration_date=str(exp_date)
                            )
                            
                            opportunities.append(opportunity)
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing {symbol} bear call spreads: {e}")
        
        return opportunities
    
    async def find_all_credit_spreads(self, target_roi: float = 33.0, target_pop: float = 66.0) -> List[CreditSpread]:
        """Find all credit spread opportunities across portfolio"""
        print(f"🎯 CREDIT SPREADS SCANNER")
        print(f"   Target: ROI {target_roi}%+, POP {target_pop}%+")
        print(f"   Strategies: Bull Put Spreads & Bear Call Spreads")
        print(f"   DTE Range: 15-45 days")
        print("="*60)
        
        all_opportunities = []
        symbols = self.market_data.get('symbols', [])
        
        for symbol in symbols:
            print(f"\n📊 Analyzing {symbol}...")
            
            symbol_data = self.get_symbol_data(symbol)
            if not symbol_data:
                print(f"   ❌ No data available for {symbol}")
                continue
            
            print(f"   Current: ${symbol_data['current_price']:.2f}")
            print(f"   IV: {symbol_data['iv']*100:.1f}% (Higher = Better Premiums)")
            print(f"   Liquidity: {symbol_data['liquidity']}/5")
            
            # Analyze both strategies
            bull_puts = await self.analyze_bull_put_spreads(symbol, symbol_data, target_roi, target_pop)
            bear_calls = await self.analyze_bear_call_spreads(symbol, symbol_data, target_roi, target_pop)
            
            total_found = len(bull_puts) + len(bear_calls)
            
            if total_found > 0:
                all_opportunities.extend(bull_puts + bear_calls)
                print(f"   ✅ Found {total_found} credit spreads ({len(bull_puts)} bull puts, {len(bear_calls)} bear calls)")
            else:
                print(f"   ⚪ No credit spreads meeting criteria")
        
        return all_opportunities
    
    def rank_credit_spreads(self, opportunities: List[CreditSpread]) -> List[CreditSpread]:
        """Rank credit spreads by attractiveness"""
        # Sort by confidence score, then ROI, then POP
        ranked = sorted(opportunities, 
                       key=lambda x: (x.confidence_score, x.roi, x.pop), 
                       reverse=True)
        
        return ranked
    
    def display_credit_spreads(self, opportunities: List[CreditSpread], top_n: int = 15):
        """Display top credit spread opportunities"""
        if not opportunities:
            print("\n❌ No credit spreads found matching your criteria")
            print("\n💡 SUGGESTIONS:")
            print("   • Lower ROI target: Try 25-30% instead of 33%")
            print("   • Lower POP target: Try 60-65% instead of 66%") 
            print("   • Higher IV stocks perform better for credit spreads")
            print("   • Market conditions may not favor credit spreads today")
            return
        
        print(f"\n🏆 TOP {min(top_n, len(opportunities))} CREDIT SPREAD OPPORTUNITIES")
        print("="*80)
        
        bull_puts = [opp for opp in opportunities if opp.strategy == "Bull Put Spread"]
        bear_calls = [opp for opp in opportunities if opp.strategy == "Bear Call Spread"]
        
        print(f"   📈 {len(bull_puts)} Bull Put Spreads (bullish/neutral)")
        print(f"   📉 {len(bear_calls)} Bear Call Spreads (bearish/neutral)")
        
        for i, opp in enumerate(opportunities[:top_n], 1):
            direction = "📈" if opp.strategy == "Bull Put Spread" else "📉"
            
            print(f"\n#{i} {direction} {opp.symbol} - {opp.strategy}")
            print(f"   📋 Trade: {opp.description}")
            print(f"   💰 Credit Received: ${opp.credit_received:.2f} per spread")
            print(f"   🎯 Max Profit: ${opp.max_profit:.0f} (keep full credit)")
            print(f"   📉 Max Loss: ${opp.max_loss:.0f}")
            print(f"   📊 ROI: {opp.roi:.1f}%")
            print(f"   🎲 POP: {opp.pop:.1f}%")
            print(f"   📅 DTE: {opp.dte} days ({opp.expiration_date})")
            print(f"   ⚖️ Risk/Reward: {opp.risk_reward_ratio:.2f}")
            print(f"   ⭐ Confidence: {opp.confidence_score:.2f}")
            print(f"   💵 Current Price: ${opp.current_price:.2f}")
            print(f"   🎪 Strikes: {opp.short_strike:.0f}/{opp.long_strike:.0f} (${opp.spread_width:.0f} wide)")
            print(f"   ⚖️ Breakeven: ${opp.breakeven:.2f}")
            
            # Add management tips
            if opp.strategy == "Bull Put Spread":
                distance = ((opp.current_price - opp.short_strike) / opp.current_price) * 100
                print(f"   📍 Short strike is {distance:.1f}% below current price")
            else:
                distance = ((opp.short_strike - opp.current_price) / opp.current_price) * 100
                print(f"   📍 Short strike is {distance:.1f}% above current price")

async def main():
    """Main execution function"""
    print("🎯 Credit Spreads Focused Trade Picker")
    print("="*50)
    
    # Configuration
    username = "username"
    password = "password"
    
    # Find latest market data file
    import glob
    import os
    
    data_files = glob.glob("portfolio_data_*.json") + glob.glob("tastytrade_production_*.json")
    if not data_files:
        print("❌ No market data files found!")
        return
    
    latest_file = max(data_files, key=os.path.getctime)
    print(f"📁 Using market data: {latest_file}")
    
    # Your criteria
    target_roi = 33.0   # 33% ROI minimum
    target_pop = 66.0   # 66% POP minimum
    
    try:
        analyzer = CreditSpreadsAnalyzer(username, password, latest_file)
        
        print(f"\n💼 Portfolio Analysis for Credit Spreads:")
        portfolio = [
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
        
        for stock in portfolio:
            print(f"   {stock['ticker']} - {stock['name']}")
        
        # Find credit spread opportunities
        opportunities = await analyzer.find_all_credit_spreads(target_roi, target_pop)
        
        # Rank and display
        ranked_opportunities = analyzer.rank_credit_spreads(opportunities)
        analyzer.display_credit_spreads(ranked_opportunities, top_n=15)
        
        # Save results
        if ranked_opportunities:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"credit_spreads_{timestamp}.json"
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'criteria': {
                    'target_roi': target_roi,
                    'target_pop': target_pop,
                    'dte_range': '15-45 days'
                },
                'total_opportunities': len(ranked_opportunities),
                'bull_put_spreads': len([opp for opp in ranked_opportunities if opp.strategy == "Bull Put Spread"]),
                'bear_call_spreads': len([opp for opp in ranked_opportunities if opp.strategy == "Bear Call Spread"]),
                'opportunities': []
            }
            
            for opp in ranked_opportunities:
                opp_data = {
                    'symbol': opp.symbol,
                    'strategy': opp.strategy,
                    'description': opp.description,
                    'credit_received': opp.credit_received,
                    'max_profit': opp.max_profit,
                    'max_loss': opp.max_loss,
                    'roi': opp.roi,
                    'pop': opp.pop,
                    'dte': opp.dte,
                    'short_strike': opp.short_strike,
                    'long_strike': opp.long_strike,
                    'spread_width': opp.spread_width,
                    'current_price': opp.current_price,
                    'breakeven': opp.breakeven,
                    'confidence_score': opp.confidence_score,
                    'expiration_date': opp.expiration_date
                }
                data['opportunities'].append(opp_data)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n💾 Credit spreads saved to: {filename}")
            
            print(f"\n📈 CREDIT SPREADS SUMMARY:")
            print(f"   Total opportunities: {len(ranked_opportunities)}")
            print(f"   Bull Put Spreads: {data['bull_put_spreads']}")
            print(f"   Bear Call Spreads: {data['bear_call_spreads']}")
            
            # Symbol breakdown
            symbol_breakdown = {}
            for opp in ranked_opportunities:
                if opp.symbol not in symbol_breakdown:
                    symbol_breakdown[opp.symbol] = {'bull_puts': 0, 'bear_calls': 0}
                if opp.strategy == "Bull Put Spread":
                    symbol_breakdown[opp.symbol]['bull_puts'] += 1
                else:
                    symbol_breakdown[opp.symbol]['bear_calls'] += 1
            
            print(f"\n🏢 By Symbol:")
            for symbol, counts in sorted(symbol_breakdown.items()):
                company_name = next((stock["name"] for stock in portfolio if stock["ticker"] == symbol), "Unknown")
                total = counts['bull_puts'] + counts['bear_calls']
                print(f"   {symbol} ({company_name}): {total} total ({counts['bull_puts']} bull puts, {counts['bear_calls']} bear calls)")
        
        else:
            print(f"\n⚪ No credit spreads found meeting your criteria.")
            print(f"\n🔧 TROUBLESHOOTING SUGGESTIONS:")
            print(f"   1. Try relaxed criteria:")
            print(f"      • ROI: 25-30% instead of {target_roi}%")
            print(f"      • POP: 60-65% instead of {target_pop}%")
            print(f"   2. High IV stocks work best:")
            print(f"      • PLTR (68.6% IV) - Should have good opportunities")
            print(f"      • ENPH (59.3% IV) - Good for premium selling") 
            print(f"      • TSLA (52.7% IV) - Usually active options")
            print(f"   3. Market conditions:")
            print(f"      • Credit spreads work best in sideways/trending markets")
            print(f"      • Very low or very high volatility can limit opportunities")
            print(f"   4. Timing:")
            print(f"      • Try running closer to market open (9:30-10:30 AM)")
            print(f"      • Options pricing is most active during market hours")
        
        print(f"\n💡 CREDIT SPREADS TRADING TIPS:")
        print(f"   📈 Bull Put Spreads:")
        print(f"      • Use when bullish/neutral on stock")
        print(f"      • Profit if stock stays above short strike")
        print(f"      • Manage at 25-50% of max profit")
        print(f"   📉 Bear Call Spreads:")
        print(f"      • Use when bearish/neutral on stock") 
        print(f"      • Profit if stock stays below short strike")
        print(f"      • Manage at 25-50% of max profit")
        print(f"   ⏰ General Tips:")
        print(f"      • Target 15-45 DTE for good theta decay")
        print(f"      • Aim for strikes with ~15-20 delta")
        print(f"      • Close early if you can capture 25-50% of max profit")
        print(f"      • High IV rank/percentile = better entry opportunities")
        
        print(f"\n✅ Credit spreads analysis complete!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```




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

