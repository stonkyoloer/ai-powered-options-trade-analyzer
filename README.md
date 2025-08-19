# 🚀 Daily Portfolio and Credit Spread Screeners

"I am now AI, start with $400, ChatGPT vs Grok, I will do whatever they say.  I am not responsible for my actions.  No DD.  No Brains.  JUST VIBES!"  

---
# 🛠 Configure TastyTrade

## `Configure TastyTrade`


# 1️⃣ Select Trading Universe

## Download the Trading Universe

`XLK` https://www.sectorspdrs.com/mainfund/XLK

`XLC` https://www.sectorspdrs.com/mainfund/XLC

`XLY` https://www.sectorspdrs.com/mainfund/XLY

`XLP` https://www.sectorspdrs.com/mainfund/XLP

`XLV` https://www.sectorspdrs.com/mainfund/XLV

`XLF` https://www.sectorspdrs.com/mainfund/XLF

`XLI` https://www.sectorspdrs.com/mainfund/XLI

`XLE` https://www.sectorspdrs.com/mainfund/XLE

`XLU` https://www.sectorspdrs.com/mainfund/XLU


## Prompt
```
Use the attached ticker basket files as the universe.
Select the top 4 tickers per sector/theme for trading 0–45 DTE credit spreads today.
Apply this strict filter framework (real-time only):
  1. Earnings & Macro Events (Scheduled) – Must verify in today’s/week’s earnings calendars or official macro event schedules (Fed, CPI, jobs, OPEC, regulatory). Exclude if unverified.
  2. Headline & News Drivers – Must be sourced from live headlines (upgrades/downgrades, strikes, lawsuits, product launches, sector disruptions). Rank by strength of catalyst.
  3. Implied Volatility Context (Event-Driven) – Only flag if real-time news or analyst notes explicitly cite elevated IV or “fear premium.” Ignore historical averages.
  4. Directional Tilt – Classify bias as bullish, bearish, or neutral only if justified by current event/news flow. If unclear, mark as “Neutral.”
  5. Shock Disconnection / Factor Buckets  – Ensure coverage across growth (Tech/Discretionary), rates (Financials/Utilities), commodities (Energy/Industrials), and defensives (Staples/Healthcare). Avoid clustering.

Output_1 format (table):
  Sector | Ticker | Event/News Driver (1 short sentence, real-time) | Tilt (Bullish/Bearish/Neutral)

Output_2 format (portfolio):

A) PYTHON_PATCH
```python
SECTORS_GPT = {
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Communication Services": {
        "etf": "XLC",
        "description": "ads, platforms, media",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Consumer Staples": {
        "etf": "XLP",
        "description": "defensive cashflows, low vol",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Financials": {
        "etf": "XLF",
        "description": "rate curve/credit sensitivity",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Industrials": {
        "etf": "XLI",
        "description": "capex, global trade, PMIs",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity",
        "tickers": ["T1","T2","T3","T4"],
    },
}


Rules:
  1. Use only real-time, verifiable data.
  2. Exclude any ticker where data cannot be confirmed.
  3. Look ahead for scheduled events today/this week.
```
---

# 2️⃣ Daily Portfolio Screener

## `sectors.py`

Defines sector portfolios, merges them, manages symbols.

## `build_universe.py`

Validates tickers' options chains, saves results, logs status.

## `spot.py`

Streams live stock quotes, saves bid/ask/mid prices.

## `atm_iv.py`

Calculates ATM implied volatility, IV rank for tickers.

## `liquidity.py`

Analyzes options liquidity, creates sector-based trading baskets.

---

# 3️⃣ Daily Credit Spread Screener


## `stock_prices.py`

Collects live stock prices for universe tickers.

## `options_chains.py`

Discovers options contracts for credit spread analysis.

## `iv_data.py`

Collects implied volatility data for options contracts.

## `market_prices.py`

Collects real-time bid/ask prices for options contracts.

## `risk_analysis.py`


## `iv_liquidity.py`


## `find_tendies.py`


## `master.py`

```bash
python3 master.py`
```

---


# 4️⃣ AI Driven News Screener 

## Prompt

```text
You are my Credit-Spread Catalyst & Sanity Checker. Timezone: America/Los_Angeles.
Use absolute dates. When you fetch news/events, include links and sources.

INPUTS (paste below):
=== step7_complete_credit_spreads.json ===
{PASTE_JSON_HERE}
=== optional: step4_liquidity.json ===
{PASTE_JSON_HERE_OR_SKIP}
=== end ===

GOALS
For the top 20 spreads by combined_score:
  • Validate “sane to trade today?” across catalysts, liquidity, and calendar risk.
  • Surface reasons to Delay/Avoid (not advice—just risk signals).

CHECKLIST (per spread)
1) Calendar gates:
   - Earnings date between today and the spread’s expiration? Mark “Earnings-Inside-Trade”.
   - Ex-div date inside the trade window? Note potential assignment/price gap risk.
   - Sector macro events within 5 trading days (e.g., CPI/FOMC for Financials/Tech beta; OPEC/EIA for Energy; FDA calendar for biotech tickers). 
2) Fresh news (last 72h):
   - Pull 1–2 headlines that could move the underlying. Link them.
3) Liquidity sanity:
   - Confirm both legs have adequate OI (≥500 minimum; ≥1,000 preferred) and spreads not wider than 10¢ (tier-2) or 5¢ (tier-1 names). If step4_liquidity.json present, use Δ30 proxies; else infer from available fields.
4) Price sanity:
   - Credit ≤ width, ROI = credit/(width-credit). Recompute if needed; flag if odd (e.g., credit > width).
5) Risk note:
   - Summarize exposure (bear call = short upside; bull put = short downside) and distance-from-money (%). 
   - Note if IV regime seems low (<0.25) for premium selling or unusually high (>0.60) for gap risk.

OUTPUT FORMAT
- A ranked table with: 
  Ticker | Type (BearCall/BullPut) | Strikes | DTE | Credit | ROI% | Dist-OTM% | OI(min) | Spread sanity | Key Event(s) | Fresh News | Decision (Do / Delay / Avoid) + 1-line reason
- Then a short summary:
  • #Passing vs #Flagged 
  • Top 3 “Do” candidates with the clearest catalyst path (quiet calendar, sufficient OI, tight spreads)
  • Top 3 risk reasons observed (e.g., earnings inside window, macro landmines, thin OI)

RULES
- Information only; no trading advice. 
- Always include links for news/events you cite.
- If any required field is missing, mark “n/a” and continue; do not fabricate.
``` 

