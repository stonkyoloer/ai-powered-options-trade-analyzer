# 🚀 

Work in Progress... The script is pulling live market data from tastytrade server. Need a tool or automation for your project or idea? Hit me up, and I’ll build it from scratch!  

---

**Script_1:** `config.py`

**What:** Centralizes Tastytrade creds + API base URL (or reads from env vars) so other scripts just import config.

**Why:** Single source of truth for auth/settings—no copy-paste, easy rotation, safer via env vars + .gitignore.

---

# 1️⃣ Ticker Selection Project 

## ▪️ Attach Trading Universe

`XLK` https://www.sectorspdrs.com/mainfund/XLK

`XLC` https://www.sectorspdrs.com/mainfund/XLC

`XLY` https://www.sectorspdrs.com/mainfund/XLY

`XLP` https://www.sectorspdrs.com/mainfund/XLP

`XLV` https://www.sectorspdrs.com/mainfund/XLV

`XLF` https://www.sectorspdrs.com/mainfund/XLF

`XLI` https://www.sectorspdrs.com/mainfund/XLI

`XLE` https://www.sectorspdrs.com/mainfund/XLE

`XLU` https://www.sectorspdrs.com/mainfund/XLU

---

## ▪️ News Heat Ticker Selection

```python
# Prompt 1: News Heat Ticker Picker

## 1. Universe & Selection
1. **CSV Extract**: Pull ticker symbols by sector from provided files
2. **Yahoo Basic**: Get current price, market cap, basic volume (delayed)
3. **News Search**: Google News search for ticker + catalyst keywords
4. **Price Stability**: Skip if major gap or unusual price action visible
5. **Market Cap**: Note large vs small cap from Yahoo data
6. **Sector Balance**: Target 3 tickers per sector from CSV list
7. **Basic Volume**: Use Yahoo's reported daily volume (delayed data)
8. **Earnings Check**: Search Yahoo for upcoming earnings dates
9. **Company Size**: Prefer established companies with steady trading

## 2. News & Scoring
1. **News Search**: Google News for "ticker + merger/upgrade/FDA" last 72h
2. **Source Check**: Company press releases > major news outlets
3. **Time Filter**: Recent news (1-3 days) gets higher priority
4. **Event Type**: M&A news > analyst upgrades > product news
5. **Verification**: Look for multiple sources reporting same event
6. **Simple Score**: High/Medium/Low based on news quality and recency

## 3. Execution & Output
1. **Time Limit**: Reasonable research time per sector (no real-time pressure)
2. **Output Format**: Sector | Ticker | News_Summary | Score
3. **Ranking**: Sort by news quality and source credibility
```

## ▪️ Instructions for Edge 

```python
# Instructions 1: Ticker Selection

## 1. Available Data Sources
1. **Yahoo Finance**: Basic stock data (price, volume, market cap)
2. **Google News**: Recent news articles and press releases
3. **Company Websites**: Official press releases and announcements
4. **SEC EDGAR**: Filed documents (8-K, 10-K, 10-Q)
5. **Financial News Sites**: Reuters, Bloomberg articles via search
6. **Yahoo Calendar**: Basic earnings date information
7. **CSV Files**: Sector ticker lists provided by user
8. **Basic Charts**: Yahoo Finance price charts for visual context
9. **Company Profiles**: Basic business descriptions and metrics

## 2. Realistic Edge Factors
1. **News Timing**: Recent positive news may drive short-term momentum
2. **Multiple Sources**: Cross-verification reduces false signals
3. **Company Size**: Larger companies typically have better liquidity
4. **Sector Themes**: Group similar news events for trend identification
5. **Press Release Quality**: Official company news vs rumors
6. **Market Reaction**: Visible price response to news events

## 3. Honest Limitations
1. **No Real-Time Data**: All data has delays (15+ minutes minimum)
2. **No Options Data**: Cannot verify options liquidity or pricing
3. **No Advanced Metrics**: No IV rank, Greeks, or complex calculations
```



# 2️⃣ Daily Options Screener

## ▪️ How to use 

Run `individual steps` or use the `master pipeline`

```bash

# Individual steps:

python3 sectors.py
python3 build_universe.py  
python3 spot.py
python3 ticker_ranker.py
python3 options_chains.py
python3 greeks.py
python3 spread_analyzer.py

# OR run everything at once:

python3 master.py
```

---

**Script_2:** `build_universe.py`  

**What:** Tests if stocks have options chains  

**Why:** No options = no credit spreads possible

---

**Step 2:** `spot.py`  

**What:** Gets current stock prices  

**Why:** Need prices for strike selection

---


**Script_3:** `ticker_ranker.py`  

**What:** Ranks stocks by options liquidity  

**Why:** Liquid options = better fills

---

**Script_4** `options_chains.py`  

**What:** Downloads all option contracts  

**Why:** Need contracts to build spreads

---

**Script_5:** `greeks.py`  

**What:** Gets option prices + Greeks  

**Why:** Need real data for PoP/ROI

---

**Script_6:** `spread_analyzer.py`  

**What:** Builds spreads, calculates PoP/ROI, picks best  

**Why:** This creates your final table

---



# 3️⃣ Credit Spread Optimizer (AI)

## ▪️ Credit Spread Optimizer

```python
# Prompt 2: Basic Spread Analysis

## 1. JSON Analysis
1. **Data Parsing**: Extract spread details from provided Tastytrade JSON
2. **Ticker Matching**: Match JSON tickers with Stage 1 selections
3. **PoP Review**: Use provided probability of profit numbers
4. **ROI Analysis**: Evaluate return on investment from JSON data
5. **DTE Assessment**: Consider days to expiration provided
6. **Distance Check**: Review distance from current price in JSON
7. **Spread Types**: Categorize Bear Call vs Bull Put spreads
8. **Risk Review**: Calculate potential loss vs gain from JSON
9. **Simple Ranking**: Order spreads by basic risk/reward metrics

## 2. Basic Scoring
1. **PoP Priority**: Higher probability of profit gets better score
2. **ROI Consideration**: Balance returns with probability
3. **Time Factor**: Prefer reasonable DTE (not too short/long)
4. **Safety Distance**: Favor spreads with price buffer
5. **Spread Width**: Consider risk amount vs potential profit
6. **Simple Formula**: Combine PoP and ROI with distance factor

## 3. Selection Process
1. **JSON Ranking**: Order all available spreads by score
2. **Basic Limits**: Don't concentrate too heavily in one sector
3. **Output Table**: AI Bot | Sector| Ticker | Spread_Type | Legs | DTE | PoP | ROI | Score
```

## ▪️ Spread Optimization Edge

```python
# Instructions 2: Realistic Spread Analysis

## 1. JSON Data Processing
1. **File Reading**: Parse the provided Tastytrade JSON structure
2. **Data Validation**: Ensure all required fields are present
3. **Basic Calculations**: Simple math on provided numbers
4. **Ticker Cross-Reference**: Match against Stage 1 portfolio
5. **Spread Categorization**: Group by type and characteristics
6. **Risk Assessment**: Basic risk/reward from provided data
7. **Sorting Logic**: Rank by simple scoring criteria
8. **Output Formatting**: Clean table presentation
9. **Error Handling**: Manage missing or invalid data gracefully

## 2. Simple Edge Factors
1. **Higher PoP**: Generally better for consistent wins
2. **Reasonable ROI**: Good returns without excessive risk
3. **Time Balance**: Not too short or too long DTE
4. **Price Buffer**: Some distance from current price for safety
5. **Portfolio Balance**: Don't put all eggs in one basket
6. **Data Quality**: Use only verified information from JSON

## 3. Honest Limitations
1. **No Live Verification**: Cannot confirm current market conditions
2. **Static Analysis**: Based only on provided JSON snapshot
3. **No Market Context**: Cannot assess current volatility environment
```
