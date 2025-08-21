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
# Sector Top-3 Selector (0–33 DTE Credit Spreads)
**Assistant-executable only.** Uses your sector CSVs **for tickers** and public web news **for catalysts**.  
No live quotes, no IV/Greeks, no broker data or options metrics.

---

## Universe & Pre-Filters
1. **Load & lock universe** — Read all sector CSVs; analyze *only* those tickers.
2. **Normalize** — Uppercase + dedupe tickers; drop obvious non-equities if a quick company/profile page confirms.
3. **News presence gate** — Keep tickers with ≥1 reputable article/press release in the last **7 days**; deprioritize others.
4. **Freshness gate** — Prioritize headlines from **today** or **yesterday after close** (≤ **72h** best window).
5. **Heat filter (text-based)** — From article language:  
   - **Tradable Heat (target):** “rallied/rose/slid,” “steady gains,” “heavy trading,” “follow-through.”  
   - **Too Hot (avoid):** “halted,” “gapped,” “limit up/down,” “whipsaw,” “plunged/soared.”
6. **Earnings guard** — If credible news/IR explicitly states an earnings date **≤ 33 days**, **skip/flag** (no binary holds).
7. **Binary-event guard** — If an FDA/regulatory decision, merger vote, or court ruling has a set date **≤ 33 days**, **skip/flag**.
8. **After-hours landmine** — If articles mention a scheduled event **after 4pm ET** or **pre-market next day**, avoid same-day/overnight holds → **skip/flag**.
9. **Sector balance** — Target **up to 3** qualified tickers **per sector** after scoring; do not force picks if a sector is cold.

---

## News & Edge Scoring
1. **Catalyst search (≤72h)** — For each candidate, pull items on: M&A/buyout, multi-analyst upgrades/downgrades, guidance updates, FDA/regulatory actions, large contracts, activist/exec changes.
2. **Source weighting** — Official **PR/8-K/IR** and top outlets (**Reuters/Bloomberg/Yahoo/CNBC**) > secondary sites; multi-source confirmation = boost.
3. **Recency weighting** — < **48h** = strongest; **3–7d** = medium; older = low unless clearly major **and** multi-source.
4. **Direction map** — Label **bullish / bearish / unclear** catalyst; propose **put-credit** (bullish drift) or **call-credit** (bearish fade); unclear = pass/Low.
5. **Reaction context (textual)** — Use article wording (“shares rose X%,” “heavy trading,” “orderly,” “profit-taking”) to tag **Tradable** vs **Too Hot**; prefer **Tradable**.
6. **Edge score** — Assign **High / Medium / Low** with a one-line reason **and at least one reputable citation** per ticker.

---

## 3 — Output & Selection (doable)
1. **Pick** — Within each sector, choose **up to 3** highest-edge tickers (avoid **Too Hot**/**flagged** unless clearly justified by durable news and multiple sources).
2. **Format (table)** —  
   **Sector | Ticker | Bias (Put-Cred / Call-Cred) | DTE | PoP | ROI| Catalyst (1-liner) | Flip Plan (Same-Day / Next-Day; why) | Edge (H/M/L) | Citation(s)**
3. **Teach-back** — Add **one sentence per sector** explaining why these beat peers (fresh credible catalyst, *tradable* heat, no near-term binaries).

---

## Runbook (end-to-end steps to execute)
1. Parse CSVs → build sector ticker lists.  
2. For each ticker: quick profile sanity; news scan (≤7d; focus ≤72h).  
3. Apply guards (earnings/binaries/after-hours) and heat filter.  
4. Score per **6-point rubric**; compile sector rankings.  
5. Output table (top-3 per sector) + sector teach-back, with citations.

---

### Scope & Limits (explicit)
- I **do not** fetch live quotes, IV, Greeks, OI, bid/ask, or broker-only data.  
- Liquidity is **inferred from news text only** (e.g., “heavy trading”)—no numerical option liquidity checks.  
- Picks are **research shortlists**; you place/verify trades and set your **+10%** TP and risk on your platform.
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
