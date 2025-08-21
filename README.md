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
# News Heat Ticker Picker - Prompt 1

**Input**: 9 Sector CSV files (tickers only)  
**Output**: 27 tickers (3 per sector) with verified catalysts

## 1. Universe & Selection
* **CSV Extract**: Pull ticker symbols by sector, verify via Yahoo Finance
* **Volume Gate**: Min 10M daily, 50K options (Yahoo real-time)
* **IV Rank**: 30-70% for optimal premium collection
* **Market Cap**: $2B+ for institutional liquidity  
* **Float Check**: >100M shares via Yahoo statistics
* **Earnings Block**: No earnings <33 DTE (Yahoo calendar)
* **Options Chain**: Weekly expirations + 1000+ OI both strikes
* **Technical**: Note 20/50MA proximity for strike placement
* **Halt Check**: No trading halts last 30 days

## 2. News & Scoring
* **M&A Confirmed**: SEC 8-K filing = 4000 points
* **FDA Events**: Phase results/approvals = 3500 points  
* **Analyst Actions**: Upgrades with price targets = 2000 points
* **Contract Wins**: $100M+ deals = 1500 points
* **Guidance Beats**: Raised estimates = 1200 points
* **Time Decay**: -300 per day >24h, floor 500 points

## 3. Execution & Output
* **Speed Run**: 45 seconds per sector max
* **Verification**: Cross-check Yahoo + Google News + SEC
* **Output**: Sector | Ticker | Heat | Volume | IV_Rank
```

## ▪️ Instructions for Edge 

```python
# Instructions 1: Ticker Selection Edge

## 1. Real-Time Verification
* **Yahoo Finance**: Live volume, IV rank, market cap, float
* **SEC EDGAR**: 8-K filings for M&A, material events <72h
* **Google News**: Verified sources only, no rumors/speculation
* **Options Data**: Real OI/volume at money strikes via Yahoo
* **Earnings Calendar**: Precise dates, not estimates
* **Company IR**: Press releases for contract/guidance updates
* **Analyst Sites**: Verified upgrades with reasoning/targets
* **FDA Tracker**: Clinical trial databases for biotech events
* **Trading Halts**: Exchange official halt/resume notifications

## 2. Edge Factors
* **Volume Surge**: 3x+ average = institution knowledge
* **IV Expansion**: 30-70% rank = premium without event risk
* **OI Concentration**: Heavy call/put activity = directional bias
* **Sector Rotation**: Compare vs sector ETF momentum
* **Catalyst Timing**: Events 5-15 days out = IV decay edge
* **Float Analysis**: Low float + news = explosive moves

## 3. Quality Control
* **Liquidity Test**: Spread <$0.10 on ATM options
* **Institution Check**: 40%+ ownership via 13F filings
* **Volatility Stability**: No binary events in DTE window
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
# Credit Spread Optimizer - Prompt 2
**Input**: Tastytrade JSON + 27 ticker portfolio  
**Goal**: Optimal credit spreads for execution

## 1. JSON Analysis
* **Spread Extraction**: Parse PoP, ROI, DTE, distance, legs
* **Ticker Match**: Cross-reference with Stage 1 portfolio
* **PoP Filter**: Minimum 52% probability required
* **ROI Target**: 80%+ returns for risk undertaken
* **DTE Sweet**: 15-25 days for theta decay peak
* **Distance Buffer**: >1.5% from current for safety
* **Credit Collect**: 18-25% of spread width optimal
* **Volume Check**: Both strikes >500 OI minimum
* **IV Rank**: Confirm high IV environment from spreads

## 2. Risk Scoring
* **Base Formula**: (PoP-50) × 2 + ROI × 0.5 + Distance × 20
* **DTE Bonus**: +10 if 15-25 DTE, -15 outside range
* **Width Penalty**: -20 if spread >$5 wide (liquidity risk)
* **Sector Limit**: -25 if >25% portfolio in sector
* **Correlation**: -15 if similar delta/underlying movement
* **IV Bonus**: +15 if IV rank >60% (premium expansion)

## 3. Portfolio Construction
* **Top Selection**: Rank all spreads by risk-adjusted score
* **Diversification**: Max 20% any sector, 8% any ticker
* **Execution Order**: Highest score first for best fills
```

## ▪️ Spread Optimization Edge

```python
# Instructions 2: Spread Optimization Edge

## 1. JSON Processing Power
* **Data Validation**: Verify PoP/ROI calculations vs. Black-Scholes
* **Strike Analysis**: Confirm delta positioning (16-20 short delta)
* **IV Environment**: Calculate IV rank from option prices
* **Time Decay**: Verify theta acceleration in DTE window
* **Liquidity Deep**: Check bid-ask spreads <$0.05 difference
* **Greeks Balance**: Ensure positive theta, manageable gamma
* **Assignment Risk**: Flag ITM probability >10% at expiration
* **Early Exercise**: Check dividend dates for assignment risk
* **Volatility Skew**: Identify advantageous put/call pricing

## 2. Statistical Edge
* **Win Rate Focus**: Target 75%+ portfolio win rate
* **Kelly Sizing**: Position size = (PoP × 2 - 1) × account %
* **Correlation Math**: Measure underlying price correlations
* **Sector Beta**: Weight by sector volatility vs SPY
* **VIX Context**: Adjust for macro volatility environment
* **Term Structure**: Exploit front-month vs back-month pricing

## 3. Execution Intelligence
* **Market Timing**: Best fills in first/last 30 minutes
* **Order Flow**: Use limit orders at mid-point of spread
* **Assignment Management**: Close at 50% profit or 21 DTE
```
