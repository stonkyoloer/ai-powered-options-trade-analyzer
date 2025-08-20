# 🚀 


---
# 🛠 Configure TastyTrade

# 1️⃣ Prompt: News Heat Ticker Picker

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

## Prompt for News Heat Ticker Picker

```text

Date: [enter date & time]


Universe (must use): Only tickers in the attached CSVs: XLK, XLC, XLY, XLP, XLV, XLF, XLI, XLE, XLU.
Goal (must do): Pick exactly 3 tickers per sector (9 sectors = 27 total) for 0–33 DTE credit spreads today.


Rules (real-time only, no guesses)
1. Live, timestamped, named-publisher sources that explicitly mention the ticker.
2. If not confirmed now by a primary or two majors (≤72h), treat as no news.
3. No IV inference—no estimates, no history, no options-flow anecdotes.
4. Use IV only when a credible source quantifies it and ties it to a dated event.


Step 1 — Score News (≤24h preferred; fallback ≤72h)
Assign each ticker one News Heat Score Unit (NHSU) from its single strongest, verified ≤72h catalyst:
4000 — M&A (Definitive) Definitive/signed deal or acknowledged offer posted on IR/SEC or confirmed by 2+ major wires (≤24h preferred).
3500 — Product / Regulatory (Final) Dated product launch/major event or final regulatory/litigation decision (SEC/FDA/court) with a clear effective date.
1500 — Analyst (Tier-1) Upgrade/downgrade or target change from a tier-1 broker.
1500 — Guidance / Pre-announcement Formal guidance change (press release/8-K) or quantified pre-earnings company commentary.
1500 — CEO/CFO Change Leadership change with effective date (IR/filing).
1500 — Buyback / Dividend New/expanded repurchase authorization, dividend initiation/raise, or special dividend.
1500 — Major Contract / Partnership Material customer win, government award, or exclusive strategic partnership with numbers/terms.
1500 — Index Change S&P/MSCI/FTSE inclusion/exclusion naming the company.
1500 — Recall / Safety Product recall or safety advisory with scope and remediation (company/regulator).
1500 — Data Breach / Cyber Company-confirmed breach/ransomware with operational or financial impact.
1500 — IP Update (Non-final) Patent grant/expiry, injunction filing, or notable docket move (not a final ruling).
1200 — Lawsuit / Strike Filed lawsuit, class certification, union strike/settlement confirmed by company/union/regulator.
1200 — Investigation / Subpoena Agency investigation opened or subpoena disclosed (regulator/company).
1200 — Short-Seller Report (Tier-1) Credible activist report with evidence and major-wire pickup.
500 — Minor Update (fallback-only) Awards, small pilots, non-material PR/blog chatter. Exclude unless used strictly as fallback.
0 — No News Nothing verifiable (≤72h). Use only for ETF-weight fallback.
Boost: If a reputable source explicitly states elevated/implied volatility due to a dated event, add +500 to that ticker’s NHSU.
Threshold: News picks require NHSU ≥ 1000.


Step 2 — Event Gate (avoid event landmines)
1. Exclude any ticker with a confirmed company earnings date inside 0–33 DTE.
2. Exclude tickers directly impacted by a dated macro/regulatory event within ~5 trading days relevant to their sector (e.g., Fed/Jackson Hole/CPI/Jobs for rates-sensitive; OPEC/EIA for Energy; notable FDA dates for Health Care) if the timing is confirmed.


Step 3 — Build the basket (must return 3 per sector)
1. For each sector, rank tickers by NHSU (highest first).
2. Use only NHSU ≥ 1000 for news picks.
3. If a sector has fewer than 3 qualified news picks, fill the remainder with fallback tickers from that sector’s CSV using ETF weight as a proxy (highest weights first).
4. Tie-breakers: higher ETF weight → larger market cap → alphabetical.


Results
Output (table only — no links, no extra columns):
Sector | Ticker | News Heat (NHSU)
Exactly three rows per sector (27 total)
In the News Heat cell, write one of:
Catalyst: M&A (4000 [+500 if IV])
Catalyst: Product/Regulatory (3500 [+500 if IV])
Catalyst: Upgrade/Downgrade (1500 [+500 if IV])
Catalyst: Guidance (1500 [+500 if IV])
Catalyst: CEO/CFO Change (1500 [+500 if IV])
Catalyst: Buyback/Dividend (1500 [+500 if IV])
Catalyst: Contract/Partnership (1500 [+500 if IV])
Catalyst: Index Change (1500 [+500 if IV])
Catalyst: Recall/Safety (1500 [+500 if IV])
Catalyst: Data Breach (1500 [+500 if IV])
Catalyst: IP Update (1500 [+500 if IV])
Catalyst: Lawsuit/Strike (1200 [+500 if IV])
Catalyst: Investigation/Subpoena (1200 [+500 if IV])
Catalyst: Short-Seller Report (1200 [+500 if IV])
Fallback: Low heat (<1000)
Fallback: No news (0)
```  



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

