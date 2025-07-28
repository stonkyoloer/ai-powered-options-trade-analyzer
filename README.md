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

# 4️⃣ TastyTrade Data Import & Analysis

## 📈 Fetch Real-Time Data, Calculate PoP, Rank Trades

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

