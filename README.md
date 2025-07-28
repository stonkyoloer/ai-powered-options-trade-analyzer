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

## Fetch Delated Data From TastyTrade
```bash
#!/usr/bin/env python3
"""
TASTYTRADE DELAYED DATA ANALYZER
Optimized for unfunded accounts with delayed quotes

What delayed data is PERFECT for:
1. End-of-day analysis and backtesting
2. Identifying option pricing patterns
3. Building systematic trading strategies
4. Historical volatility analysis
5. Strategy development and testing

This script maximizes what you can get from delayed data!

Created: 2025-07-28
"""

import pandas as pd
from datetime import datetime, timedelta, time
import asyncio
import warnings
import time as time_module
from decimal import Decimal
import numpy as np

# Core TastyTrade imports
from tastytrade import Session
from tastytrade.instruments import get_option_chain, Equity

# Optional Black-Scholes (install with: pip install py-vollib)
try:
    from py_vollib.black_scholes.greeks.analytical import delta, gamma, theta, vega
    from py_vollib.black_scholes import black_scholes
    VOLLIB_AVAILABLE = True
except ImportError:
    VOLLIB_AVAILABLE = False

warnings.filterwarnings('ignore')

class Settings:
    """Settings optimized for delayed data analysis"""
    
    # Your TastyTrade login
    USERNAME = "username"
    PASSWORD = "password"
    
    # Stocks for analysis
    STOCKS = [
        {"ticker": "NVDA", "name": "NVIDIA"},
        {"ticker": "TSLA", "name": "Tesla"},
        {"ticker": "AMZN", "name": "Amazon"},
        {"ticker": "SPY", "name": "SPDR S&P 500"},
        {"ticker": "QQQ", "name": "Invesco QQQ"},
        {"ticker": "AAPL", "name": "Apple"},
        {"ticker": "MSFT", "name": "Microsoft"},
    ]
    
    # Analysis parameters (broader range for delayed data)
    MIN_DAYS_TO_EXPIRATION = 1
    MAX_DAYS_TO_EXPIRATION = 90
    
    # Risk-free rate for calculations
    RISK_FREE_RATE = 0.045
    
    # Focus on liquid strikes (within this % of current price)
    STRIKE_RANGE_PERCENT = 0.20  # +/- 20% from current price

def convert_decimal(value):
    """Convert Decimal to float safely"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value

def calculate_moneyness(stock_price, strike_price):
    """Calculate option moneyness"""
    if not stock_price or not strike_price:
        return None
    return stock_price / strike_price

def estimate_historical_volatility(prices, days=30):
    """Estimate historical volatility from price series"""
    if len(prices) < 2:
        return 0.20  # Default 20% if no history
    
    returns = np.diff(np.log(prices))
    return np.std(returns) * np.sqrt(252)  # Annualized volatility

class DelayedDataAnalyzer:
    """Analyzer optimized for delayed data from unfunded accounts"""
    
    def __init__(self):
        self.session = None
        self.session_token = None
        
    async def connect(self):
        """Connect and verify delayed data access"""
        print("🔌 Connecting to TastyTrade (Delayed Data Mode)...")
        
        try:
            self.session = Session(Settings.USERNAME, Settings.PASSWORD)
            self.session_token = self.session.session_token
            print(f"✅ Connected successfully")
            
            # Check account status
            try:
                customer = self.session.get_customer()
                accounts = customer.accounts
                
                total_value = sum(convert_decimal(acc.net_liquidating_value) or 0 for acc in accounts)
                
                if total_value > 0:
                    print(f"💰 Account funded: ${total_value:,.2f}")
                    print(f"🔄 Note: Running in delayed data mode anyway for comparison")
                else:
                    print(f"⏳ Account unfunded - perfect for delayed data analysis")
                    print(f"💡 Delayed data is excellent for strategy development!")
                
            except Exception as e:
                print(f"⚠️  Account check: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_enhanced_stock_data(self, ticker):
        """Get comprehensive stock data optimized for delayed analysis"""
        try:
            stock = Equity.get(self.session, ticker)
            
            # Get stock price data
            current_price = None
            previous_close = None
            
            # Try multiple endpoints for delayed data
            try:
                # Market metrics endpoint
                quote_data = self.session.get(f'/market-metrics?symbols={ticker}')
                if quote_data and 'data' in quote_data and quote_data['data']['items']:
                    market_data = quote_data['data']['items'][0]
                    current_price = convert_decimal(market_data.get('last-price'))
                    previous_close = convert_decimal(market_data.get('previous-close-price'))
            except:
                pass
            
            # Try instruments endpoint if first fails
            if not current_price:
                try:
                    stock_quote = self.session.get(f'/instruments/equities/{ticker}')
                    if stock_quote and 'data' in stock_quote:
                        current_price = convert_decimal(stock_quote['data'].get('close-price'))
                except:
                    pass
            
            # Calculate daily change if we have both prices
            daily_change = None
            daily_change_percent = None
            if current_price and previous_close and previous_close > 0:
                daily_change = current_price - previous_close
                daily_change_percent = (daily_change / previous_close) * 100
            
            return {
                "ticker": stock.symbol,
                "company_name": stock.description,
                "exchange": stock.listed_market,
                "current_price": current_price,
                "previous_close": previous_close,
                "daily_change": daily_change,
                "daily_change_percent": daily_change_percent,
                "active": stock.active
            }
            
        except Exception as e:
            print(f"❌ Error getting stock data for {ticker}: {e}")
            return None
    
    def analyze_delayed_options(self, ticker, stock_data):
        """Analyze options using delayed data approach"""
        print(f"\n📊 Analyzing {ticker} options (Delayed Data Focus)...")
        
        if not stock_data['current_price']:
            print(f"⚠️  No price data for {ticker} - skipping")
            return pd.DataFrame()
        
        try:
            chain = get_option_chain(self.session, ticker)
            print(f"📈 Found {len(chain)} expiration dates")
            
            current_price = stock_data['current_price']
            analysis_data = []
            
            # Calculate strike range for liquid options
            min_strike = current_price * (1 - Settings.STRIKE_RANGE_PERCENT)
            max_strike = current_price * (1 + Settings.STRIKE_RANGE_PERCENT)
            
            for exp_date, option_list in chain.items():
                # Date calculations
                if isinstance(exp_date, str):
                    exp_dt = datetime.strptime(exp_date, "%Y-%m-%d")
                else:
                    exp_dt = exp_date
                exp_dt = datetime.combine(exp_dt, datetime.min.time())
                days_left = (exp_dt - datetime.now()).days
                
                # Filter by expiration
                if Settings.MIN_DAYS_TO_EXPIRATION <= days_left <= Settings.MAX_DAYS_TO_EXPIRATION:
                    print(f"  📅 {exp_date}: {days_left} days, {len(option_list)} options")
                    
                    # Focus on liquid strikes
                    liquid_options = [opt for opt in option_list 
                                    if min_strike <= convert_decimal(opt.strike_price) <= max_strike]
                    
                    print(f"    🎯 {len(liquid_options)} liquid options (${min_strike:.0f}-${max_strike:.0f})")
                    
                    for option in liquid_options:
                        contract_data = self._analyze_delayed_contract(
                            option, exp_date, days_left, stock_data
                        )
                        if contract_data:
                            analysis_data.append(contract_data)
            
            df = pd.DataFrame(analysis_data)
            print(f"✅ Analyzed {len(df)} liquid option contracts")
            return df
            
        except Exception as e:
            print(f"❌ Error analyzing options for {ticker}: {e}")
            return pd.DataFrame()
    
    def _analyze_delayed_contract(self, option, exp_date, days_left, stock_data):
        """Analyze single contract optimized for delayed data"""
        try:
            strike = convert_decimal(option.strike_price)
            option_type = "Call" if option.option_type.value == "C" else "Put"
            time_to_expiration = max(days_left / 365.0, 1/365)
            
            # Extract available delayed data
            bid = convert_decimal(getattr(option, 'bid', None))
            ask = convert_decimal(getattr(option, 'ask', None))
            last = convert_decimal(getattr(option, 'last', None))
            mark = convert_decimal(getattr(option, 'mark', None))
            volume = convert_decimal(getattr(option, 'volume', None))
            open_interest = convert_decimal(getattr(option, 'open_interest', None))
            
            # Delayed Greeks (may be from previous close)
            delayed_delta = convert_decimal(getattr(option, 'delta', None))
            delayed_gamma = convert_decimal(getattr(option, 'gamma', None))
            delayed_theta = convert_decimal(getattr(option, 'theta', None))
            delayed_vega = convert_decimal(getattr(option, 'vega', None))
            delayed_iv = convert_decimal(getattr(option, 'implied_volatility', None))
            
            # Use last price as primary delayed price
            delayed_price = last or mark or ((bid + ask) / 2 if bid and ask else None)
            
            # Calculate key metrics
            moneyness = calculate_moneyness(stock_data['current_price'], strike)
            intrinsic_value = None
            time_value = None
            
            if stock_data['current_price'] and strike:
                if option_type == "Call":
                    intrinsic_value = max(0, stock_data['current_price'] - strike)
                else:
                    intrinsic_value = max(0, strike - stock_data['current_price'])
                
                if delayed_price:
                    time_value = delayed_price - intrinsic_value
            
            # Estimate current IV using delayed price (if available)
            estimated_iv = delayed_iv or 0.25  # Default to 25% if no IV available
            
            # Calculate theoretical values using Black-Scholes
            theoretical_data = {}
            if VOLLIB_AVAILABLE and estimated_iv:
                try:
                    flag = 'c' if option_type == "Call" else 'p'
                    theoretical_data = {
                        'theoretical_price': black_scholes(flag, stock_data['current_price'], strike, 
                                                         time_to_expiration, Settings.RISK_FREE_RATE, estimated_iv),
                        'theoretical_delta': delta(flag, stock_data['current_price'], strike, 
                                                 time_to_expiration, Settings.RISK_FREE_RATE, estimated_iv),
                        'theoretical_gamma': gamma(flag, stock_data['current_price'], strike, 
                                                 time_to_expiration, Settings.RISK_FREE_RATE, estimated_iv),
                        'theoretical_theta': theta(flag, stock_data['current_price'], strike, 
                                                 time_to_expiration, Settings.RISK_FREE_RATE, estimated_iv) / 365,
                        'theoretical_vega': vega(flag, stock_data['current_price'], strike, 
                                               time_to_expiration, Settings.RISK_FREE_RATE, estimated_iv) / 100
                    }
                except:
                    theoretical_data = {
                        'theoretical_price': None, 'theoretical_delta': None,
                        'theoretical_gamma': None, 'theoretical_theta': None, 'theoretical_vega': None
                    }
            
            # Calculate price deviation if we have both delayed and theoretical
            price_deviation = None
            if delayed_price and theoretical_data.get('theoretical_price'):
                price_deviation = delayed_price - theoretical_data['theoretical_price']
            
            # Liquidity scoring based on available data
            liquidity_score = 0
            if bid and ask:
                spread = ask - bid
                mid_price = (bid + ask) / 2
                if mid_price > 0:
                    spread_percent = (spread / mid_price) * 100
                    liquidity_score += 3 if spread_percent < 5 else 1  # Tight spread = liquid
            
            if volume and volume > 10:
                liquidity_score += 2
            if open_interest and open_interest > 100:
                liquidity_score += 1
            
            return {
                # Basic info
                'ticker': stock_data['ticker'],
                'symbol': option.symbol,
                'expiration_date': str(exp_date),
                'days_to_expiration': days_left,
                'time_to_expiration_years': time_to_expiration,
                'strike_price': strike,
                'option_type': option_type,
                'underlying_price': stock_data['current_price'],
                'moneyness': moneyness,
                
                # Delayed market data
                'delayed_bid': bid,
                'delayed_ask': ask,
                'delayed_last': last,
                'delayed_mark': mark,
                'delayed_price': delayed_price,
                'volume': volume,
                'open_interest': open_interest,
                
                # Delayed Greeks
                'delayed_delta': delayed_delta,
                'delayed_gamma': delayed_gamma,
                'delayed_theta': delayed_theta,
                'delayed_vega': delayed_vega,
                'delayed_iv': delayed_iv,
                
                # Calculated values
                'intrinsic_value': intrinsic_value,
                'time_value': time_value,
                'estimated_iv': estimated_iv,
                
                # Theoretical comparison
                **theoretical_data,
                'price_deviation': price_deviation,
                
                # Analysis metrics
                'liquidity_score': liquidity_score,
                'data_quality_score': sum([bool(delayed_price), bool(delayed_delta), bool(volume)]),
                
                # Flags for filtering
                'has_delayed_pricing': bool(delayed_price),
                'has_delayed_greeks': bool(delayed_delta),
                'has_volume_data': bool(volume),
                'is_liquid': liquidity_score >= 3,
                
                # Metadata
                'analysis_timestamp': datetime.now().isoformat(),
                'data_type': 'delayed'
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {option.symbol}: {e}")
            return None
    
    def generate_delayed_analysis_report(self, df, ticker, stock_data):
        """Generate comprehensive delayed data analysis report"""
        if df.empty:
            return f"No data available for {ticker}"
        
        # Data quality metrics
        total_contracts = len(df)
        with_pricing = df['has_delayed_pricing'].sum()
        with_greeks = df['has_delayed_greeks'].sum()
        with_volume = df['has_volume_data'].sum()
        liquid_options = df['is_liquid'].sum()
        
        report = f"""
{'='*80}
DELAYED DATA ANALYSIS REPORT: {ticker}
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Stock: {stock_data['company_name']} (${stock_data['current_price']:.2f})
Daily Change: {stock_data['daily_change_percent']:.2f}% (${stock_data['daily_change']:.2f})

📊 DATA SUMMARY:
─────────────────────────────────────────────────────────────────────────────
Total Liquid Contracts: {total_contracts:,}
With Delayed Pricing: {with_pricing:,} ({with_pricing/total_contracts*100:.1f}%)
With Delayed Greeks: {with_greeks:,} ({with_greeks/total_contracts*100:.1f}%)
With Volume Data: {with_volume:,} ({with_volume/total_contracts*100:.1f}%)
High Liquidity Options: {liquid_options:,} ({liquid_options/total_contracts*100:.1f}%)

🎯 DELAYED DATA QUALITY ASSESSMENT:
─────────────────────────────────────────────────────────────────────────────"""
        
        if with_pricing > total_contracts * 0.7:
            report += """
✅ EXCELLENT delayed pricing coverage
🎯 Perfect for end-of-day analysis and backtesting"""
        elif with_pricing > total_contracts * 0.3:
            report += """
✅ GOOD delayed pricing coverage
📊 Suitable for strategy development"""
        else:
            report += """
⚠️  LIMITED delayed pricing coverage
🔄 May need alternative data sources"""
        
        # Price analysis
        pricing_data = df.dropna(subset=['delayed_price'])
        if not pricing_data.empty:
            avg_price = pricing_data['delayed_price'].mean()
            report += f"""

💰 OPTION PRICING ANALYSIS:
─────────────────────────────────────────────────────────────────────────────
Average Option Price: ${avg_price:.2f}
Price Range: ${pricing_data['delayed_price'].min():.2f} - ${pricing_data['delayed_price'].max():.2f}
Options Under $1: {(pricing_data['delayed_price'] < 1.0).sum():,}
Options $1-$5: {((pricing_data['delayed_price'] >= 1.0) & (pricing_data['delayed_price'] < 5.0)).sum():,}
Options Over $5: {(pricing_data['delayed_price'] >= 5.0).sum():,}"""
        
        # Greeks analysis (if available)
        greeks_data = df.dropna(subset=['delayed_delta'])
        if not greeks_data.empty:
            report += f"""

🔢 DELAYED GREEKS ANALYSIS:
─────────────────────────────────────────────────────────────────────────────
Average Delta: {greeks_data['delayed_delta'].mean():.3f}
Delta Range: {greeks_data['delayed_delta'].min():.3f} to {greeks_data['delayed_delta'].max():.3f}
High Delta Options (>0.7): {(greeks_data['delayed_delta'] > 0.7).sum():,}
Medium Delta Options (0.3-0.7): {((greeks_data['delayed_delta'] >= 0.3) & (greeks_data['delayed_delta'] <= 0.7)).sum():,}
Low Delta Options (<0.3): {(greeks_data['delayed_delta'] < 0.3).sum():,}"""
        
        # Liquidity analysis
        if liquid_options > 0:
            liquid_df = df[df['is_liquid']]
            report += f"""

💧 LIQUIDITY ANALYSIS:
─────────────────────────────────────────────────────────────────────────────
High Liquidity Options: {liquid_options:,}
Avg Volume (Liquid): {liquid_df['volume'].mean():.0f}
Avg Open Interest (Liquid): {liquid_df['open_interest'].mean():.0f}"""
        
        # Theoretical comparison (if available)
        if VOLLIB_AVAILABLE:
            theoretical_data = df.dropna(subset=['theoretical_price', 'delayed_price'])
            if not theoretical_data.empty:
                price_diffs = theoretical_data['price_deviation']
                report += f"""

🧮 THEORETICAL vs DELAYED COMPARISON:
─────────────────────────────────────────────────────────────────────────────
Contracts with Both Prices: {len(theoretical_data):,}
Avg Price Difference: ${price_diffs.mean():.3f}
Overvalued Options: {(price_diffs > 0.50).sum():,}
Undervalued Options: {(price_diffs < -0.50).sum():,}"""
        
        # Top opportunities
        if not pricing_data.empty:
            # Sort by various criteria for opportunities
            high_volume = pricing_data[pricing_data['volume'] > 100].nlargest(5, 'volume') if 'volume' in pricing_data.columns else pd.DataFrame()
            
            if not high_volume.empty:
                report += f"""

🔥 TOP VOLUME OPTIONS (for liquidity):
─────────────────────────────────────────────────────────────────────────────"""
                for _, row in high_volume.iterrows():
                    report += f"""
{row['symbol']} | ${row['strike_price']:.0f} {row['option_type']} | Price: ${row['delayed_price']:.2f} | Vol: {row['volume']:.0f}"""
        
        report += f"""

💡 DELAYED DATA INSIGHTS:
─────────────────────────────────────────────────────────────────────────────
✅ Delayed data is PERFECT for:
  • End-of-day strategy analysis
  • Historical backtesting
  • Pattern recognition
  • Risk management planning
  • Options selection and filtering

🎯 STRATEGIC ADVANTAGES:
  • No emotional market noise
  • Consistent data for systematic analysis
  • Perfect for building and testing strategies
  • Great for identifying long-term opportunities

📈 RECOMMENDED ANALYSIS:
  • Focus on high-volume, liquid options
  • Use theoretical prices for fair value estimates
  • Build watchlists for when you get real-time data
  • Develop systematic selection criteria

{'='*80}
"""
        
        return report

async def main():
    """Main delayed data analysis program"""
    
    print("📊 TASTYTRADE DELAYED DATA ANALYZER")
    print("=" * 60)
    print(f"🎯 Optimized for unfunded account analysis")
    print(f"📈 Analyzing {len(Settings.STOCKS)} stocks")
    print(f"📅 Expiration range: {Settings.MIN_DAYS_TO_EXPIRATION}-{Settings.MAX_DAYS_TO_EXPIRATION} days")
    print(f"🧮 Black-Scholes available: {VOLLIB_AVAILABLE}")
    print("=" * 60)
    
    analyzer = DelayedDataAnalyzer()
    if not await analyzer.connect():
        return
    
    all_data = []
    
    for stock_config in Settings.STOCKS:
        ticker = stock_config["ticker"]
        
        print(f"\n{'='*50}")
        print(f"📊 ANALYZING: {ticker} ({stock_config['name']})")
        print("="*50)
        
        # Get enhanced stock data
        stock_data = analyzer.get_enhanced_stock_data(ticker)
        if not stock_data:
            continue
        
        print(f"🏢 Company: {stock_data['company_name']}")
        print(f"📈 Price: ${stock_data.get('current_price', 'N/A')}")
        if stock_data.get('daily_change_percent'):
            print(f"📊 Daily Change: {stock_data['daily_change_percent']:.2f}%")
        
        # Analyze options with delayed data focus
        df = analyzer.analyze_delayed_options(ticker, stock_data)
        if df.empty:
            continue
        
        # Generate comprehensive analysis
        report = analyzer.generate_delayed_analysis_report(df, ticker, stock_data)
        print(report)
        
        # Save detailed data
        csv_filename = f"{ticker}_delayed_analysis.csv"
        df.to_csv(csv_filename, index=False)
        print(f"💾 Saved detailed analysis: {csv_filename}")
        
        # Save report
        report_filename = f"{ticker}_delayed_report.txt"
        with open(report_filename, 'w') as f:
            f.write(report)
        print(f"📄 Saved report: {report_filename}")
        
        all_data.append(df)
        
        # Small delay between stocks
        time_module.sleep(1)
    
    # Combined analysis
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        print(f"\n{'='*60}")
        print(f"🌟 COMBINED DELAYED DATA ANALYSIS")
        print("="*60)
        
        total_contracts = len(combined_df)
        total_with_pricing = combined_df['has_delayed_pricing'].sum()
        total_liquid = combined_df['is_liquid'].sum()
        
        print(f"📊 Total contracts analyzed: {total_contracts:,}")
        print(f"💰 With delayed pricing: {total_with_pricing:,} ({total_with_pricing/total_contracts*100:.1f}%)")
        print(f"💧 High liquidity options: {total_liquid:,} ({total_liquid/total_contracts*100:.1f}%)")
        
        # Save combined dataset
        combined_filename = "combined_delayed_analysis.csv"
        combined_df.to_csv(combined_filename, index=False)
        print(f"💾 Combined dataset: {combined_filename}")
        
        print(f"\n🎯 DELAYED DATA SUCCESS!")
        print(f"✅ You now have comprehensive delayed data for strategy development")
        print(f"📈 Perfect for backtesting and systematic analysis")
        print(f"🚀 When real-time funding activates, you'll have both datasets to compare!")
        
        if not VOLLIB_AVAILABLE:
            print(f"\n💡 ENHANCEMENT OPPORTUNITY:")
            print(f"Install py-vollib for theoretical pricing comparison:")
            print(f"  pip install py-vollib")

if __name__ == "__main__":
    asyncio.run(main())
```



## 📈 Fetch Real Time Data From TastyTrade 

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
    USERNAME = "stonkyoloer"
    PASSWORD = "@!3X3R!kkamiles"
    
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

