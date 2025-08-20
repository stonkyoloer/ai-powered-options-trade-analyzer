# 🚀 Prompt: News Heat Ticker Picker

```text
Date: [enter date & time]
Universe (must use): Only tickers in the attached CSVs: XLK, XLC, XLY, XLP, XLV, XLF, XLI, XLE, XLU.
Goal (must do): Pick exactly 3 tickers per sector (9 sectors = 27 total) for 0–33 DTE credit spreads today. Tickers only, no option legs.

Rules (real-time only, no guesses)

Use your browsing tools to pull live, verifiable info.

If you can’t verify now, leave it out (treat as no news).

Don’t estimate IV or use historical IV. Only use IV if a source explicitly says it’s elevated because of an event.

Step 1 — Score News (≤24h preferred; fallback ≤72h)

Assign each ticker one News Heat Score Unit (NHSU) based on the strongest current, verifiable item:

4000 — Confirmed M&A (announced/definitive).

3500 — Product launch/major dated event OR major regulatory/litigation decision (SEC/FDA/court/government).

1500 — Analyst upgrade/downgrade (reputable firm) OR formal guidance change/credible pre-earnings company commentary.

1200 — Lawsuit/strike news with credible sourcing (non-rumor).

500 — Minor update. (Exclude from selection unless used as fallback.)

0 — No verifiable fresh news.

Boost: If a reputable source explicitly states elevated/implied volatility due to an event, add +500 to that ticker’s NHSU.
Threshold: To qualify as a news pick, NHSU ≥ 1000.

Step 2 — Event Gate (avoid event landmines)

Exclude any ticker with a confirmed company earnings date inside 0–33 DTE.

Exclude tickers directly impacted by a dated macro/regulatory event within ~5 trading days relevant to their sector (e.g., Fed/Jackson Hole/CPI/Jobs for rates-sensitive; OPEC/EIA for Energy; notable FDA dates for Health Care) if the event timing is confirmed.

If uncertain, exclude (don’t guess).

Step 3 — Build the basket (must return 3 per sector)

For each sector, rank tickers by NHSU (highest first). Use only NHSU ≥ 1000 for news picks.

If a sector has fewer than 3 qualified news picks, fill the remainder with fallback tickers from that sector’s CSV using ETF weight as a proxy (highest weights first).

Tie-breakers: higher ETF weight → larger market cap → alphabetical.

Safety filter: Exclude any ticker with a confirmed trading halt, delisting, or bankruptcy in the last 24h; keep filling with the next eligible name to maintain 3.

Output (table only — no links, no extra columns)
Sector | Ticker | News Heat (NHSU)


Exactly three rows per sector (27 total).

In the News Heat cell, write one of:

Catalyst: M&A (4000[+500 if IV])

Catalyst: Product/Regulatory (3500[+500 if IV])

Catalyst: Upgrade/Downgrade (1500[+500 if IV])

Catalyst: Guidance (1500[+500 if IV])

Catalyst: Lawsuit/Strike (1200[+500 if IV])

Fallback: No news (0)

Fallback: Low heat (<1000)

Constraints (hard)

No PoP, ROI, IV rank, liquidity, quotes, or option legs.

No rumors or “likely” language. Only what you can pull now.

Always return 3 per sector using the fallback rule if needed.
```  

---
# 🛠 Configure TastyTrade

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

Run `individual steps` or use the `master pipeline`

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

