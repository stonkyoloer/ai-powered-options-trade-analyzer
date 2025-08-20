# 🚀 


---
# 🛠 Configure TastyTrade

# 1️⃣ Prompt: News Heat Ticker Picker

## ▪️ Download the Trading Universe

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

## ▪️ Prompt for News Heat Ticker Picker

```text
Edge Prompt (Real-Time, No Guessing)

Date: [enter date & time]

Universe (must use): Only tickers in the attached CSVs: XLK, XLC, XLY, XLP, XLV, XLF, XLI, XLE, XLU.
Goal (must do): Pick exactly 3 tickers per sector (9 sectors = 27 total) for 0–33 DTE credit spreads today.
Output: Table only — Sector | Ticker | News Heat (NHSU) — exactly 3 rows per sector.

What I will fetch now (real-time, verifiable):
1. Company primary: IR/press releases/8-K (≤72h).
2. Regulators/courts: SEC/DOJ/FTC/ITC/FDA/CPSC/court dockets (≤72h).
3. Index providers: S&P/MSCI/FTSE inclusion/exclusion notices.
4. Macro calendars (official): Fed/Jackson Hole/FOMC; BLS CPI/Jobs; OPEC/EIA; notable FDA dates.
5. Tier-1 analysts: Upgrades/downgrades/target changes (firm named).
6. Credit agencies: S&P/Moody’s/Fitch rating/outlook changes.
7. Legal/labor/security: Lawsuits, class certs, investigations/subpoenas, strikes/ratifications, company-confirmed breaches.
8. Corporate actions: Buybacks/dividends (auths/raises), ex-div dates.
9. Market hygiene: Trading halts/delistings/bankruptcies; avoid unconfirmed big premarket gaps.

Hard rules (binary, pass/fail)

1. Live, timestamped, named-publisher source that names the ticker.
2. If not confirmed now by a primary or two majors (≤72h), treat as no news.
3. ≤24h preferred; allow ≤72h only if still active/relevant; drop >72h.
4. No IV inference — no estimates/history/options-flow anecdotes.
5. Use IV only when a credible source quantifies it and ties it to a dated event.
6. De-dup events: many links about the same event count as one catalyst.

Action steps (score, gate, build)

Step 1 — Score News (≤24h preferred; fallback ≤72h).
Assign one NHSU per ticker from its strongest verified catalyst:
4000 — M&A (definitive/signed/acknowledged).
3500 — Product launch/major dated event or final regulatory/litigation decision.
1500 — Analyst (tier-1) or guidance/pre-announcement (PR/8-K) or CEO/CFO change or buyback/dividend or major contract/partnership or index change or recall/safety or data breach or IP update (non-final).
1200 — Lawsuit/strike or investigation/subpoena or tier-1 short-seller report (picked up by majors).
500 — Minor update (fallback-only).
0 — No verifiable ≤72h news.
Boost: If a reputable source explicitly quantifies event-linked IV, add +500.
Threshold: NHSU ≥ 1000 required for a news pick.

Step 2 — Event Gate (avoid landmines).
1. Exclude tickers with earnings inside 0–33 DTE.
2. Exclude tickers directly hit by dated macro/regulatory within ~5 trading days (Fed/CPI/Jobs for rates; OPEC/EIA for Energy; notable FDA for Health Care) if timing is confirmed.

Step 3 — Build the basket (must return 3 per sector).
1. Rank by NHSU (3s first, then 2s). Use only NHSU ≥ 1000 for news picks.
2. If <3, fallback to top ETF weights from that sector’s CSV (no catalyst text).
3. Tie-breakers: higher ETF weight → larger market cap → alphabetical.

Allowed “News Heat” cell values:
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

## ▪️ How to use 

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

## ▪️ Prompt

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

