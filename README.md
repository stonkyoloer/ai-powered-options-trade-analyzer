# 🚀 Overview  
Build and maintain a daily-refreshed, AI-driven, sector-diversified options portfolio—and power a daily screener for high-probability tendies!

# 👨‍🏫 Scope  
- **Fetch NASDAQ list**  
  - Download complete list of tickers on NASDAQ  
- **Data Pipeline**
  - Ingest options data via TastyTrade API  
  - Pull market/IV data via yfinance  
  - Merge TastyTrade and yfinance into a single dataset  
- **AI Prompting**  
  - Attach data to ChatGPT/Grok  
  - Run customized prompt to:  
    - Select 1 high-IV, high-liquidity ticker per sector  
    - Generate AI-Optimized portfolio  
    - Screen daily setups  
- **Execution**  
  - Review AI-generated ideas each morning  
  - Execute and monitor positions—tendies incoming!

# 📈  Data Pipe: NASDAQ

 **Create your project folder and virtual env**
````bash
mkdir -p ~/Desktop/US_Tickers && cd ~/Desktop/US_Tickers
python3 -m venv .venv
source .venv/bin/activate
````

**Install Pandas**
````bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pandas requests
````

**Download the raw symbol lists**
````bash
curl -s -o nasdaqlisted.txt ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt
curl -s -o otherlisted.txt  ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt
````

**Create the parsing script**
````bash
cat > fetch_us_tickers.py << 'EOF'
import pandas as pd

# Load Nasdaq list and drop its footer row
nas = pd.read_csv('nasdaqlisted.txt', sep='|')
nas = nas[:-1]

# Load other exchanges list and drop its footer row
oth = pd.read_csv('otherlisted.txt', sep='|')
oth = oth[:-1]

# Combine symbols, remove NaNs, dedupe, sort
symbols = pd.concat([nas['Symbol'], oth['ACT Symbol'].rename('Symbol')])
symbols = symbols.dropna().unique()
symbols = sorted(symbols)

# Write out to CSV
pd.Series(symbols, name='Ticker').to_csv('us_all_tickers.csv', index=False)
print(f"Fetched {len(symbols)} tickers → us_all_tickers.csv")
EOF
````

**Run the parser and generate your master list**
````bash
python fetch_us_tickers.py
````


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
