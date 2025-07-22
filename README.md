# 🚀 Overview
1. Build an AI-powered, diversified trading portfolio, re-up monthly for max gains! 
2. Create a Trading Portfolio Screener for Daily Strategies (Daily)


# 👨‍🏫 Scope
1. Download Full Holdings List of: AIQ, ARKK, BOTZ, SHLD (AI ETF's)
2. Attach holdings lists to chatGPT/Grok project
3. Write Prompt
4. Run the Prompt to Build an AI-Optimized, Sector-Diversified, Options Trading Portfolio.
5. Program a TastyTrade data pipe
6. Program a yfinance data pipe
7. Program a merge of the two data sets
8. Attach datasets to ChatGPT/Grok project
9. Write Prompt
10. Run Prompt to Screen for Daily Trades
11. Tendies is cookin!  

# Workflow 1

## Download Full Holdings List of: AIQ, ARKK, BOTZ, SHLD 
Download and save holdings list, to be updated to chatGPT/Grok later
Visit: [https://www.globalxetfs.com/](https://www.globalxetfs.com/funds/aiq)
Visit: [https://www.globalxetfs.com/](https://www.globalxetfs.com/funds/botz)
Visit: [https://www.globalxetfs.com/](https://www.globalxetfs.com/funds/shld)
Visit: [https://www.ark-funds.com/](https://www.ark-funds.com/funds/arkk)



## Prompt ChatGPT/Grok to Build an AI-Optimized, Sector-Diversified, Options Trading Portfolio  
### Attachment: AIQ, BOTZ, SHLD, ARKK  
### Instructions:  
#### Goal:  
Construct a 9‑ticker, sector‑diversified options portfolio emphasizing:  
- **High Implied Volatility (IV)** (rich premiums & IV Rank ≥ 30%)  
- **Deep Liquidity** (OI ≥ 1,000 per leg; spreads ≤ $0.05 for top names, ≤ $0.10 for moderately liquid)  
- **Strong Short‑Term Swings** (same‑day to 30 days)  
- **Industry‑Leading AI Exposure** in each sector  
- **Significant Market Attention** (institutional/retail hype)  

#### Selection Criteria (ALL must be met):  
1. **AI Leadership**: Core business or initiative is AI‑driven.  
2. **Options Liquidity**: Weekly/monthly chains, ≥ 1,000 OI on each leg, tight spreads.  
3. **Elevated IV + IV Rank ≥ 30%**: Ensure options are richly priced relative to their history.  
4. **Public Buzz**: Recent catalysts, heavy newsflow, or social/institutional interest.  
5. **Robinhood‑Available**: U.S.‑listed and accessible to retail traders.  

#### Technical & Risk Filters:  
- **Primary Signal (RSI(5))**: Confirm short‑term momentum (oversold/overbought swings).  
- **Secondary Signal (MACD Crossover)**: Validate momentum for directional plays (debit spreads, straddles).  
- **Rebalance Triggers**:  
  - **IV Rank < 30%** → remove/replace  
  - **Stop‑Loss Hit** → exit and free capital  
  - **Profit Target Hit** → lock in gains  
- **Rebalance Cadence**: Event‑driven only (no routine weekly unless a trigger fires)  

#### Portfolio Construction:  
Select **exactly one ticker per sector** (no duplicates), drawn initially from the ETF holdings (AIQ, BOTZ, ARKK, SHLD), but include any **high‑IV recent IPOs or AI spin‑outs** that meet all criteria.

| Sector                   | AI Theme                                                       |
|--------------------------|----------------------------------------------------------------|
| **Agriculture**          | Precision farming, ag‑biotech, automation                     |
| **Technology**           | AI chips, semiconductors, cloud/LLM infrastructure            |
| **Industrials**          | Robotics, smart infrastructure, automation systems            |
| **Biotechnology**        | ML drug discovery (oncology, antivirals, genomics, psychedelics) |
| **Energy (Traditional)** | AI in oil/gas ops, predictive maintenance, commodities algos |
| **Energy (Renewable)**   | AI‑optimized solar/wind/hydro, grid/storage analytics         |
| **Financials**           | AI for risk models, fraud detection, quant trading           |
| **Consumer Staples**     | AI‑driven forecasting, supply chain, personalization          |
| **Transportation**       | Autonomous vehicles, predictive logistics, fleet AI           |

### Prompt:  
#### Rules:  
1. Refer to the **Goal**, **Selection Criteria**, **Filters**, and **Construction** above.  
2. Use the **attachments** as your candidate universe.  
3. Be resourceful—pull **live or most recent data** (IV%, IV Rank, OI, spreads, RSI(5), MACD) from public APIs or data feeds.  

**Task:**  
- **Shortlist** all ETF holdings by sector.  
- **Filter** by AI exposure, liquidity, IV & IVR ≥ 30%, OI ≥ 1,000, spread ≤ $0.05/0.10, and RSI+MACD confirmation.  
- **Select** the single best ticker per sector.  
- **Output** a markdown table with columns:  
  | Ticker | Sector | AI Leadership Summary | Avg IV % | IV Rank | RSI(5) | MACD Signal | Daily Volume | Liquidity Grade |  
- **Liquidity Grade**: A (ideal), B (acceptable), C (avoid).  
- **Explain** any sector where no perfect match exists by proposing the next best alternative and rationale.  
- **Include** rebalancing triggers and signal filters in your commentary block below the table.  

––  
_This prompt is battle‑tested for aggressive, short‑term premium extraction—modeled on Cohen, Rotter, Bruton, Arnold, Sosnoff, Minervini, Williams, Krieger, and Taleb._  


### Output: 
#### Portfolio Metrics Summary
#### Optimized AI-Driven Options Portfolio (2025-07-20)
#### CHAT GPT SELECTION(S)
| Ticker | Sector        | Rationale for AI Leadership                                                      | Avg_IV_% | Daily_Volume | Liquidity_Metrics                              |
|--------|---------------|----------------------------------------------------------------------------------|----------|--------------|------------------------------------------------|
| DE     | Agriculture   | AI-powered autonomous tractors & precision ag, leader in smart farming           | ~32      | ~1.2M        | Tight spreads (~$0.05–$0.10), deep OI          |
| NVDA   | Technology    | Dominates AI computing, >90% data center GPU share, foundation of AI workloads   | ~34      | ~180M        | Penny spreads, huge volume, deep OI            |
| SYM    | Industrials   | AI-powered warehouse automation for Walmart and others, logistics robotics       | ~100     | ~2M          | Spreads ~$0.10–$0.20, active weeklies          |
| RXRX   | Biotech       | AI-first drug discovery, automating target ID & preclinical with ML              | ~100     | ~25–30M      | Spreads ~$0.05–$0.10, thinner OI but active    |
| HLX    | Energy (Trad) | AI-driven robotics for oil/gas, subsea ROVs & automation                         | ~54      | ~1.8M        | Spreads ~$0.10+, concentrated OI               |
| GOOGL  | Energy (Ren)  | AI optimizing wind/solar, DeepMind grid AI, global leader in green AI apps       | ~35      | ~40M         | Penny spreads, huge OI, deep chain             |
| PLTR   | Cons. Staples | AI-driven supply chain, demand forecasting, logistics for FMCG/retail            | ~69      | ~85M         | Spreads $0.01–$0.05, deep OI, high retail flow |
| UPST   | Financials    | AI lending & credit modeling, disruptive loan/credit AI, wild price swings       | ~107     | ~6M          | Spreads $0.05–$0.10, active weeklies           |
| TSLA   | Transport     | AI for self-driving, robotics, logistics, undisputed auto AI leader              | ~54      | ~100M+       | Penny spreads, massive OI, liquid weeklies     |

#### GROK SELECTION(S)
| Ticker | Sector                                     | Rationale for AI Leadership                                                              | Average IV % | Daily Trading Volume | Liquidity Metrics                                      |
|--------|--------------------------------------------|------------------------------------------------------------------------------------------|--------------|---------------------|--------------------------------------------------------|
| NVDA   | Technology (Computing, Semiconductors)     | Leader in GPU technology, crucial for AI computations, with strong AI hardware/software  | 35%          | 203,628,106         | High, with tight spreads due to large volume           |
| LMT    | Industrials (AI-enabled Infrastructure)    | Leading defense contractor investing in AI for autonomous systems and data analysis      | 24%          | 1,454,609           | Moderate, supported by consistent institutional trading|
| ISRG   | Biotechnology (AI-driven Drug Discovery)   | Leader in robotic-assisted surgery, incorporating AI for precision and efficiency        | 37%          | 2,287,200           | High, with significant trading activity and tight spreads|
| HLX    | Energy (Traditional) (AI in Oil/Gas)       | Utilizes AI for predictive maintenance in energy sector, enhancing operational efficiency| 30%          | 2,020,000           | Moderate, with steady trading volume                   |
| TSLA   | Transportation & Shipping (AI Logistics)   | Pioneering AI in autonomous driving and fleet management, with high market attention     | 40%          | 110,997,140         | Very high, with deep liquidity and tight spreads       |
| COIN   | Financials (AI in Risk/Fraud Detection)    | Leading crypto platform leveraging AI for trading and fraud detection, with significant hype | 45%      | 14,040,296           | High, with robust trading activity                     |
| RBLX   | Consumer Staples (AI-driven Forecasting)   | Uses AI for personalized gaming experiences, with high retail engagement and attention   | 30%          | 8,538,116           | High, with active retail and institutional trading     |
| Z      | Real Estate Tech (AI in Property Analytics)| Assumed AI application in real estate analytics, with growing market presence            | 25%          | 2,162,012           | Moderate, with steady trading volume                   |
| AVAV   | Agriculture (Precision Farming, Automation)| Leverages AI for precision agriculture and drone technology, enhancing farm efficiency   | 28%          | 1,009,974           | Moderate, with growing trading interest                |



##  Program a TastyTrade and yfinance Data Pipe
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

#### Overwrite Script

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

### Visual Studio
#### Query

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

### Terminal 

#### Run the Qurey

````bash
python3 full_options_report.py
````



## Produce Linked Report 

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

### Terminal
#### Run Data Query 
````bash
python3 generate_final_options_report.py
````



##  Run Prompt to Screen for Trades

##  GROK3/GPTo3: Screen Trading Portfolio For Daily Moves

### Attachment: TastyTrade and Yahoo Finance Data
### Instructions: 
#### Trade Selection Criteria
1. Number of Trades: Exactly 5
2. Goal: Maximize edge while maintaining portfolio delta, vega, and sector exposure limits.
3. Quote age ≤ 10 minutes
4. Top option Probability of Profit (POP) ≥ 0.65
5. Top option credit / max loss ratio ≥ 0.33
6. Top option max loss ≤ 0.5% of $100,000 NAV (≤ $500)
#### Selection Rules
1. Assign a model_score.
2. Rank trades by model_score.
3. Ensure diversification: maximum of 2 trades per GICS sector.
4. Net basket Delta must remain between [-0.30, +0.30] × (NAV / 100k).
5. Net basket Vega must remain ≥ -0.05 × (NAV / 100k).
6. In case of ties, prefer higher momentum_z and flow_z scores.
#### Output Format
1. Provide output strictly as a clean, text-wrapped table.
3. Include Ticker
4. Include Strategy
5. Incude Legs
6. Include Thesis (≤ 30 words, plain language)
7. Includ POP
#### Additional Guidelines
1. Limit each trade thesis to ≤ 30 words.
2. Use straightforward language, free from exaggerated claims.
3. Do not include any additional outputs or explanations beyond the specified table.

### Prompt: 

Analyze the attached CSV files, which provide screenshots of live market data.
Follow the instructions already provided.
Then Follow the instructions in the prompt.

#### Screen for Trade Type Setups
1. Day Trade (0-9)DTE
2. Short Premium (9-27)DTE
3. Directional Swing (18-45)DTE
4. Event Play (Event Date+9)DTE

#### Screen for Strategies
1. Vertical Spreads
2. Straddle and Strangle
3. Condors
4. Long Puts and Calls
   
