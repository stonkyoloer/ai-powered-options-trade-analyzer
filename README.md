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

Hard rules (binary, pass/fail):
1. Live, timestamped, named-publisher source that names the ticker.
2. If not confirmed now by a primary or two majors (≤72h), treat as no news.
3. ≤24h preferred; allow ≤72h only if still active/relevant; drop >72h.
4. No IV inference — no estimates/history/options-flow anecdotes.
5. Use IV only when a credible source quantifies it and ties it to a dated event.
6. De-dup events: many links about the same event count as one catalyst.

Action steps (score, gate, build):
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

## ▪️ Instructions and Rules  

```text
Run & order:
1. Print the exact PDT date/time at the top.
2. pend up to ~60 seconds per sector; if time’s up, fill with ETF-weight fallbacks.
3. Sort output: Sector (A→Z) → NHSU (high→low) → ETF weight → alphabetical.

Universe controls
1. You can pass pin=[...] (must include unless hard-stopped) and ban=[...] (never include).
2. Use primary U.S. listings; skip thin ADRs.

Sources (quality filter)
1. Prefer company IR/SEC/regulators/courts/index providers → then major wires (Reuters/AP/Bloomberg/WSJ/FT) → then big finance sites.
2. Auto-exclude rumor words (“reportedly/may/could/considering”) unless later confirmed.
3. If two reputable sources conflict, treat as no news.
4. Count multiple links about the same event as one catalyst.

Heat scoring tweaks
1. Freshness decay: news >24h to ≤72h = –200 NHSU (still needs ≥1000 to qualify).
2. IV boost (+500) only if a credible source quantifies IV and the event is ≤5 trading days away; remove after it passes.
3. Per sector, max 2 picks with the same catalyst type (don’t pick three upgrades).

Events & macro (gates)
1. Earnings inside 0–33 DTE = exclude.
2. Confirmed dated macro inside ~5 trading days (Fed/CPI/Jobs, OPEC/EIA, notable FDA) that directly hits the name = exclude or deprioritize.
3. Ex-div within 5 trading days = exclude.

Price-action sanity
1. If today’s move is > ±8%, skip unless Heat is 3500/4000.
2. Avoid unconfirmed premarket gaps >3% (when premarket data is visible).

Safety checks
1. Re-check for trading halts, bankruptcies, delistings in the last 24h before finalizing.
2. If there’s an active agency probe with unknown timing inside DTE, deprioritize unless a date is set.

Diversity
1. Mix sub-themes within each sector (e.g., Energy = 1 major, 1 services, 1 pipeline/renewable) when choices exist.
2. Don’t stack highly correlated mega-caps across sectors if viable alternatives exist.

Fallback discipline
1. When using fallback, don’t add catalyst text; pick by ETF weight (then market cap, then alpha).
2. If a pinned name hits a hard stop, skip it (don’t force it).
3. Light audit (for your logs, not the table)
4. Keep a tiny note per pick: headline, timestamp, source, NHSU, IV boost yes/no.
5. Note why top-weight names were skipped (e.g., earnings in window, rumor-only, >72h).
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
python3 sector_selection.py
python3 options_chains.py
python3 greeks.py
python3 spread_analyzer.py

# OR run everything at once:

python3 master.py
```

---

**Step 1:** `build_universe.py`  

**What:** Tests if stocks have options chains  

**Why:** No options = no credit spreads possible

---

**Step 2:** `spot.py`  

**What:** Gets current stock prices  

**Why:** Need prices for strike selection

---


**Step 3:** `ticker_ranker.py`  

**What:** Ranks stocks by options liquidity  

**Why:** Liquid options = better fills

---

**Step** `options_chains.py`  

**What:** Downloads all option contracts  

**Why:** Need contracts to build spreads

---

**Step 5:** `greeks.py`  

**What:** Gets option prices + Greeks  

**Why:** Need real data for PoP/ROI

---

**Step 6:** `spread_analyzer.py`  

**What:** Builds spreads, calculates PoP/ROI, picks best  

**Why:** This creates your final table

---



# 4️⃣ AI Driven News Screener 

## ▪️ Prompt for Credit Spread Results vs Market Reality

```text
Date: [enter date & time]


Universe (must use): Only credit spreads from final_credit_spread_comparison.json (has AI = GPT/Grok).
Goal (must do): Validate each 0–45 DTE spread against current market reality.
Output: Table only — Ticker | AI | Spread Type | Current Risk | Final Status — one row per spread.


What to will fetch now (real-time, verifiable):
1. Earnings collision: Company IR & earnings calendars (next 45 days).
2. Major news catalysts: Press releases / 8-K (≤ 72h).
3. Regulatory/court: SEC/DOJ/FDA/ITC/FTC/CPSC actions (≤ 72h).
4. Macro conflicts: Fed/Jackson Hole/FOMC, BLS CPI/Jobs (next 10 trading days).
5. Trading anomalies: Exchange halts/suspensions; unusual volume today.
6. Technical red flags: >8% move today without a confirmed catalyst.


Hard rules (binary, pass/fail):
1. Live, named, timestamped source that names the ticker.
2. ≤72h max age; older = no conflict.
3. Earnings inside DTE = automatic fail (skip).
4. No speculation; confirmed/documented events only.
5. Primary > secondary: Company IR/SEC → Fed/BLS/regulators → Reuters/Bloomberg/WSJ → exchange sites.


Action steps (risk → status → build):
Step 1 — Current Risk (pick highest applicable):
1. Critical (auto-skip): Earnings in DTE; trading halt; bankruptcy filing
2. High: Major catalyst ≤24h; Fed ≤5 days; Price Spike >8% (today)
3. Medium: Minor catalyst ≤72h; Macro 5–10 days; Price Move 3–8% (today)
4. Low: Clean news; no scheduled events; normal tape


Step 2 — Final Status:
1. PROCEED: Low only
2. MONITOR: Medium (consider smaller size)
3. SKIP: High or any Critical


``` 

