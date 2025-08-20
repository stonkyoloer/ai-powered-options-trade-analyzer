# 🚀 Daily Credit Spread Screeners

"I am now AI, start with $400, ChatGPT vs Grok, I will do whatever they say.  I am not responsible for my actions.  No DD.  No Brains.  JUST VIBES!"  

---
# 🛠 Configure TastyTrade

File name `Configure TastyTrade`


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

---

# 2️⃣ Daily Options Screener

## How to use 

```bash
# Individual steps:
python sectors.py
python build_universe.py  
python spot.py
python ticker_ranker.py
python sector_selection.py
python stock_prices_focused.py
python options_chains_focused.py
python greeks_collector.py
python executable_pricing.py
python spread_analyzer.py

# OR run everything at once:
python master_pipeline.py
```

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

