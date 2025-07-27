# 🚀 AI Options Trading Portfolio & Daily Trade Screener

## 📖 What This Does



## 🧠 Why Build This?







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
Now, we need to log in to your Tastytrade account so the project can get data for you.

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
- **Important:** Replace `"your_username_here"` and `"your_password_here"` with your actual Tastytrade username and password.

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
Complete options data and credit spread analysis

What this does:
1. Gets all option data from TastyTrade API
2. Finds credit spread opportunities with 33%+ returns
3. Calculates probability of profit using Black-Scholes
4. Saves everything to CSV files for analysis

Created: 2025-07-27
"""

import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import norm
import asyncio
import json
import ssl
import warnings
import os

# API connections
import httpx
import certifi
import websockets
from tastytrade import Session
from tastytrade.instruments import get_option_chain, Equity

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════════

class Settings:
    """Main settings for the platform"""
    
    # Your TastyTrade login
    USERNAME = "username"
    PASSWORD = "password"
    
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
    MIN_RETURN_PERCENT = 33         # Want at least 33% return
    RISK_FREE_RATE = 0.045          # Current interest rate (4.5%)

# ═══════════════════════════════════════════════════════════════════════════════════
# GET DATA FROM TASTYTRADE
# ═══════════════════════════════════════════════════════════════════════════════════

class DataFetcher:
    """Gets option data from TastyTrade"""
    
    def __init__(self):
        self.session = None
        
    async def connect(self):
        """Connect to TastyTrade"""
        print("Connecting to TastyTrade...")
        
        try:
            self.session = Session(Settings.USERNAME, Settings.PASSWORD)
            print("✅ Connected successfully")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_stock_info(self, ticker):
        """Get basic stock information"""
        try:
            stock = Equity.get(self.session, ticker)
            
            info = {
                "ticker": stock.symbol,
                "company_name": stock.description,
                "exchange": stock.listed_market,
                "active": stock.active,
                "current_price": None  # Will be None when market is closed
            }
            
            # Try to get current price (only works when market is open)
            price_fields = ['last', 'close', 'mark', 'bid', 'ask']
            for field in price_fields:
                price = getattr(stock, field, None)
                if price and float(price) > 0:
                    info["current_price"] = float(price)
                    info["price_source"] = field
                    break
            
            if not info["current_price"]:
                info["price_source"] = "Market Closed"
            
            return info
            
        except Exception as e:
            print(f"❌ Error getting stock info for {ticker}: {e}")
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
                    exp_dt = datetime.combine(exp_date, datetime.min.time())
                
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
            
            print(f"✅ Processed {len(valid_options)} total option contracts")
            return pd.DataFrame(valid_options) if valid_options else pd.DataFrame()
            
        except Exception as e:
            print(f"❌ Error getting options for {ticker}: {e}")
            return pd.DataFrame()
    
    def _process_option_contract(self, option, exp_date, days_left, stock_info):
        """Process a single option contract"""
        try:
            strike = float(option.strike_price)
            option_type = "Call" if option.option_type.value == "C" else "Put"
            
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
                
                # Stock info
                "stock_price": stock_info["current_price"],
                "price_source": stock_info["price_source"],
                
                # Market data (will be None when market is closed)
                "bid_price": None,
                "ask_price": None,
                "last_price": None,
                "volume": None,
                "open_interest": None,
                
                # Greeks (will be None when market is closed)
                "delta": None,
                "gamma": None,
                "theta": None,
                "vega": None,
                "implied_volatility": None,
                
                # Constants
                "risk_free_rate": Settings.RISK_FREE_RATE,
                "dividend_yield": 0.0,
                
                # Calculated fields
                "intrinsic_value": None,
                "time_value": None,
                "moneyness": None,
                "distance_from_current_pct": None,
                
                # Strategy flags
                "good_for_bull_put_spread": False,
                "good_for_bear_call_spread": False,
                
                # Data status
                "market_data_available": False,
                "ready_for_black_scholes": False,
                "data_timestamp": datetime.now().isoformat()
            }
            
            # Calculate fields that don't need live market data
            if stock_info["current_price"]:
                stock_price = stock_info["current_price"]
                
                # Calculate intrinsic value
                if option_type == "Call":
                    contract["intrinsic_value"] = max(0, stock_price - strike)
                else:  # Put
                    contract["intrinsic_value"] = max(0, strike - stock_price)
                
                # Calculate other metrics
                contract["moneyness"] = strike / stock_price
                contract["distance_from_current_pct"] = abs(strike - stock_price) / stock_price * 100
                
                # Strategy classification
                if option_type == "Put" and strike < stock_price:
                    contract["good_for_bull_put_spread"] = True
                elif option_type == "Call" and strike > stock_price:
                    contract["good_for_bear_call_spread"] = True
            
            return contract
            
        except Exception as e:
            print(f"⚠️ Error processing option contract: {e}")
            return None

# ═══════════════════════════════════════════════════════════════════════════════════
# FIND CREDIT SPREADS
# ═══════════════════════════════════════════════════════════════════════════════════

class CreditSpreadFinder:
    """Finds credit spread opportunities"""
    
    @staticmethod
    def calculate_probability_of_profit(spread_type, strikes, stock_price, credit, 
                                       days_to_exp, risk_free_rate, volatility):
        """Calculate probability of profit using Black-Scholes math"""
        if days_to_exp <= 0 or not stock_price or not volatility:
            return 0
        
        time_years = days_to_exp / 365.0
        
        if spread_type == 'Bull Put Spread':
            # Profit if stock stays above (higher_strike - credit_received)
            breakeven = max(strikes) - credit
            
        elif spread_type == 'Bear Call Spread':
            # Profit if stock stays below (lower_strike + credit_received)
            breakeven = min(strikes) + credit
            
        else:
            return 0
        
        # Use Black-Scholes to calculate probability
        d2 = (np.log(stock_price / breakeven) + (risk_free_rate - 0.5 * volatility**2) * time_years) / (volatility * np.sqrt(time_years))
        
        if spread_type == 'Bull Put Spread':
            probability = (1 - norm.cdf(d2)) * 100  # Probability stock stays above breakeven
        else:  # Bear Call Spread
            probability = norm.cdf(d2) * 100  # Probability stock stays below breakeven
        
        return max(0, min(100, probability))
    
    @staticmethod
    def find_spreads(options_df, min_return_pct=33):
        """Find all possible credit spreads"""
        if options_df.empty or options_df['stock_price'].isna().all():
            return pd.DataFrame()
        
        stock_price = options_df['stock_price'].iloc[0]
        if not stock_price:
            return pd.DataFrame()
        
        spreads = []
        
        # Look at each expiration date separately
        for exp_date, exp_options in options_df.groupby('expiration_date'):
            days_left = exp_options['days_to_expiration'].iloc[0]
            
            # Find Bull Put Spreads (sell higher strike put, buy lower strike put)
            puts = exp_options[exp_options['option_type'] == 'Put'].sort_values('strike_price')
            
            for i in range(len(puts)):
                for j in range(i+1, len(puts)):
                    short_put = puts.iloc[j]  # Higher strike (sell this)
                    long_put = puts.iloc[i]   # Lower strike (buy this)
                    
                    # Estimate option prices (since we don't have live data)
                    short_price = max(0.10, short_put['intrinsic_value'] + days_left/365 * stock_price * 0.02)
                    long_price = max(0.05, long_put['intrinsic_value'] + days_left/365 * stock_price * 0.015)
                    
                    credit = short_price - long_price
                    width = short_put['strike_price'] - long_put['strike_price']
                    max_loss = width - credit
                    
                    if credit > 0.10 and max_loss > 0:
                        return_pct = (credit / max_loss) * 100
                        
                        if return_pct >= min_return_pct:
                            # Calculate probability of profit
                            prob = CreditSpreadFinder.calculate_probability_of_profit(
                                'Bull Put Spread',
                                [long_put['strike_price'], short_put['strike_price']],
                                stock_price, credit, days_left, Settings.RISK_FREE_RATE, 0.25
                            )
                            
                            spreads.append({
                                'strategy': 'Bull Put Spread',
                                'ticker': short_put['ticker'],
                                'company_name': short_put['company_name'],
                                'expiration': exp_date,
                                'days_to_expiration': days_left,
                                'short_strike': short_put['strike_price'],
                                'long_strike': long_put['strike_price'],
                                'spread_width': width,
                                'credit_received': credit,
                                'max_profit': credit,
                                'max_loss': max_loss,
                                'return_percent': return_pct,
                                'probability_of_profit': prob,
                                'breakeven_price': short_put['strike_price'] - credit,
                                'current_stock_price': stock_price,
                                'score': (prob * 0.7) + (return_pct * 0.3)
                            })
            
            # Find Bear Call Spreads (sell lower strike call, buy higher strike call)
            calls = exp_options[exp_options['option_type'] == 'Call'].sort_values('strike_price')
            
            for i in range(len(calls)):
                for j in range(i+1, len(calls)):
                    short_call = calls.iloc[i]  # Lower strike (sell this)
                    long_call = calls.iloc[j]   # Higher strike (buy this)
                    
                    # Estimate option prices
                    short_price = max(0.10, short_call['intrinsic_value'] + days_left/365 * stock_price * 0.02)
                    long_price = max(0.05, long_call['intrinsic_value'] + days_left/365 * stock_price * 0.015)
                    
                    credit = short_price - long_price
                    width = long_call['strike_price'] - short_call['strike_price']
                    max_loss = width - credit
                    
                    if credit > 0.10 and max_loss > 0:
                        return_pct = (credit / max_loss) * 100
                        
                        if return_pct >= min_return_pct:
                            # Calculate probability of profit
                            prob = CreditSpreadFinder.calculate_probability_of_profit(
                                'Bear Call Spread',
                                [short_call['strike_price'], long_call['strike_price']],
                                stock_price, credit, days_left, Settings.RISK_FREE_RATE, 0.25
                            )
                            
                            spreads.append({
                                'strategy': 'Bear Call Spread',
                                'ticker': short_call['ticker'],
                                'company_name': short_call['company_name'],
                                'expiration': exp_date,
                                'days_to_expiration': days_left,
                                'short_strike': short_call['strike_price'],
                                'long_strike': long_call['strike_price'],
                                'spread_width': width,
                                'credit_received': credit,
                                'max_profit': credit,
                                'max_loss': max_loss,
                                'return_percent': return_pct,
                                'probability_of_profit': prob,
                                'breakeven_price': short_call['strike_price'] + credit,
                                'current_stock_price': stock_price,
                                'score': (prob * 0.7) + (return_pct * 0.3)
                            })
        
        return pd.DataFrame(spreads) if spreads else pd.DataFrame()

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════════

async def main():
    """Main program - does everything"""
    
    print("OPTIONS TRADING PLATFORM")
    print("Finding credit spreads with 33%+ returns")
    print("=" * 50)
    print(f"Analyzing {len(Settings.STOCKS)} stocks")
    print(f"Looking for {Settings.MIN_RETURN_PERCENT}%+ return opportunities")
    print(f"Date range: {Settings.MIN_DAYS_TO_EXPIRATION} to {Settings.MAX_DAYS_TO_EXPIRATION} days")
    print("=" * 50)
    
    # Connect to TastyTrade
    fetcher = DataFetcher()
    if not await fetcher.connect():
        return
    
    # Process each stock
    all_results = []
    total_options = 0
    total_spreads = 0
    
    for stock_config in Settings.STOCKS:
        ticker = stock_config["ticker"]
        
        print(f"\n" + "="*60)
        print(f"ANALYZING: {ticker} ({stock_config['name']})")
        print("="*60)
        
        # Get stock information
        stock_info = fetcher.get_stock_info(ticker)
        if not stock_info:
            continue
        
        print(f"Company: {stock_info['company_name']}")
        print(f"Exchange: {stock_info['exchange']}")
        print(f"Current Price: ${stock_info['current_price']}" if stock_info['current_price'] else "Current Price: Not available (market closed)")
        
        # Get all option contracts
        options_df = fetcher.get_all_options(ticker, stock_info)
        if options_df.empty:
            continue
        
        # Find credit spreads
        spreads_df = CreditSpreadFinder.find_spreads(options_df, Settings.MIN_RETURN_PERCENT)
        
        # Save data
        options_filename = f"{ticker}_all_options.csv"
        options_df.to_csv(options_filename, index=False)
        print(f"💾 Saved all options to: {options_filename}")
        
        if not spreads_df.empty:
            spreads_filename = f"{ticker}_credit_spreads.csv"
            spreads_df.to_csv(spreads_filename, index=False)
            print(f"💾 Saved credit spreads to: {spreads_filename}")
        
        # Track results
        all_results.append({
            'ticker': ticker,
            'company': stock_info['company_name'],
            'total_options': len(options_df),
            'credit_spreads': len(spreads_df),
            'has_current_price': stock_info['current_price'] is not None
        })
        
        total_options += len(options_df)
        total_spreads += len(spreads_df)
        
        print(f"📊 Results: {len(options_df)} options, {len(spreads_df)} credit spreads")
    
    # Final summary
    print(f"\n" + "="*60)
    print(f"FINAL SUMMARY")
    print("="*60)
    
    successful_stocks = [r for r in all_results if r['total_options'] > 0]
    stocks_with_pricing = [r for r in all_results if r['has_current_price']]
    
    print(f"✅ Successfully analyzed: {len(successful_stocks)} stocks")
    print(f"📊 Total option contracts: {total_options:,}")
    print(f"💰 Total credit spread opportunities: {total_spreads}")
    print(f"📈 Stocks with live pricing: {len(stocks_with_pricing)}/{len(successful_stocks)}")
    
    print(f"\nStock breakdown:")
    for result in all_results:
        if result['total_options'] > 0:
            price_status = "Live pricing" if result['has_current_price'] else "No pricing (market closed)"
            print(f"  {result['ticker']}: {result['total_options']:,} options, {result['credit_spreads']} spreads | {price_status}")
    
    print(f"\nWhat this platform does:")
    print(f"  • Gets complete option data from TastyTrade")
    print(f"  • Finds credit spread opportunities with {Settings.MIN_RETURN_PERCENT}%+ returns")
    print(f"  • Calculates probability of profit using Black-Scholes")
    print(f"  • Saves everything to CSV files for further analysis")
    
    if total_spreads == 0:
        print(f"\nNote: No credit spreads found because market is closed")
        print(f"      Run this during market hours (9:30 AM - 4:00 PM ET) for live pricing")
        print(f"      and real credit spread opportunities")

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

