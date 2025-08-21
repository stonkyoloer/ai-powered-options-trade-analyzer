# 🚀 

Work in Progress... The script is pulling live market data from tastytrade server. Need a tool or automation for your project or idea? Hit me up, and I’ll build it from scratch!  

---

**Script_1:** `config.py`

**What:** Centralizes Tastytrade creds + API base URL (or reads from env vars) so other scripts just import config.

**Why:** Single source of truth for auth/settings—no copy-paste, easy rotation, safer via env vars + .gitignore.

---

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

## ▪️ Attach the Trading Universe



## ▪️ Prompt for News Heat Ticker Picker

```python
# Ticker Selection Prompt

**Date**: 2025-08-20 18:17 PDT

## 1. Universe & Selection
1. **Pick Stocks**: Grab 3 stocks/sector from CSVs.
2. **Show Table**: Build table: Sector | Ticker | News Heat | Volume.
3. **Set Rules**: Pin/ban via CSV/string, skip ADRs <1M volume.
4. **Grab Data**: Use IR, SEC, Reuters, Nasdaq, Yahoo.
5. **Vary Picks**: Mix high-volume themes, sizes.
6. **Plan B**: Use weights, volume >5M, market cap.
7. **Dodge Volatility**: Skip >10% moves or News Heat <500.
8. **Aim Liquid**: Favor volume >5M unless pinned.
9. **Track Risks**: Log critical skips with reason.

## 2. News & Scoring
1. **Hunt News**: Fetch ≤72h news: filings, launches, mergers.
2. **Score Heat**: Set top score: 4000 (merger), 3500 (product), 1500 (analyst), 1200 (lawsuit), 500 (minor). Cut 200 for >24h.
3. **Block Risks**: Skip earnings, macro, dividends ≤33 DTE.
4. **Check Liquidity**: Filter volume >5M for tradability.
5. **Stay Tight**: Use timestamped sources, limit 1 news/sector.
6. **Max Edge**: Favor News Heat ≥500, volume >5M.

## 3. Execution & Output
1. **Move Quick**: Run ~60s/sector, check halts, news freshness.
2. **Make Table**: Show table: Sector | Ticker | News Heat | Volume.
3. **Log It**: Log critical skips, reasons, timestamps only.
```  

## ▪️ Instructions  

```text
Run & order:
1. Print the exact PDT date/time at the top.
2. pend up to ~60 seconds per sector; if time’s up, fill with ETF-weight fallbacks.
3. Sort output: Sector (A→Z) → NHSU (high→low) → ETF weight → alphabetical.

Universe controls
1. You can pass pin=[...] (must include unless hard-stopped) and ban=[...] (never include).
2. Use primary U.S. listings; skip thin ADRs.
3. Prefer company IR/SEC/regulators/courts/index providers → then major wires (Reuters/AP/Bloomberg/WSJ/FT) → then big finance sites.
4. Auto-exclude rumor words (“reportedly/may/could/considering”) unless later confirmed.
5. If two reputable sources conflict, treat as no news.
6. Count multiple links about the same event as one catalyst.

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
3. Re-check for trading halts, bankruptcies, delistings in the last 24h before finalizing.
4. If there’s an active agency probe with unknown timing inside DTE, deprioritize unless a date is set.
5. Mix sub-themes within each sector (e.g., Energy = 1 major, 1 services, 1 pipeline/renewable) when choices exist.
6. Don’t stack highly correlated mega-caps across sectors if viable alternatives exist.

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



# 3️⃣ AI Driven News Screener 

## ▪️ Prompt for Credit Spread Results vs Market Reality

```python
## 1. Universe & Selection
1. **Select Spreads**: Pick one spread/ticker from JSON.
2. **Show Table**: Build table: AI | Ticker | Type | Legs | DTE | PoP | ROI | Risk | Status.
3. **Set Rules**: Pin/ban via JSON/string, skip ADRs <1M.
4. **Fetch Data**: Use IR, SEC, Reuters, Nasdaq, Yahoo.
5. **Diversify Spreads**: Mix high-volume themes, avoid correlation.
6. **Fallback Plan**: Use highest PoP, volume >5M, ROI.
7. **Avoid Volatility**: Skip >10% moves or News Heat <500.
8. **Stay Liquid**: Favor volume >5M unless pinned.
9. **Track Skips**: Log skips with reason, timestamp.

## 2. News & Scoring
1. **Seek News**: Fetch ≤72h news: filings, launches, mergers.
2. **Score Catalysts**: Set top score: 4000 (merger), 3500 (product).
3. **Block Risks**: Skip earnings, macro, dividends ≤45 DTE.
4. **Ensure Liquidity**: Filter volume >5M for tradability.
5. **Keep Strict**: Use timestamped sources, limit 1 news/ticker.
6. **Assign Risk**: Set Critical, High, Medium, Low levels.

## 3. Execution & Output
1. **Run Fast**: Run ~60s/ticker, check halts, news freshness.
2. **Build Table**: Show table: AI | Ticker | Type | Legs | DTE | PoP | ROI | Risk | Status.
3. **Log Skips**: Log critical skips, reasons, timestamps only.
``` 

## ▪️ Instructions and Rules

```text
Run & order:
1. Print PDT date/time at top; fetch live from NIST.
2. Spend ~60s/sector; timeout → ETF-weight fallbacks, note "timeout".
3. Sort: Sector (A→Z) → NHSU (high→low) → ETF weight → alpha.

Universe controls:
1. Allow pin=[...], ban=[...]; default none if empty.
2. Use U.S. listings; skip thin ADRs, <500K volume.
3. Target mid/large caps (> $2B); exclude micro unless pinned.

Sources (quality filter):
1. Prefer IR/SEC/regulators → Reuters/Bloomberg/WSJ → Yahoo/Seeking.
2. Exclude rumors (“may/could”); need primary confirmation.
3. Conflicting sources = no news; require two-source consensus.
4. Dedupe same-event links; discard >72h.

Heat scoring tweaks:
1. Decay: >24h–≤72h = –200 NHSU; ≥1000 to qualify.
2. IV boost (+500) if source confirms, event ≤5 days; cap +1000.
3. Max 2 same-catalyst/sector; vary (e.g., M&A, upgrade).

Events & macro (gates):
1. Earnings in 0–33 DTE = exclude; check guidance/calls.
2. Macro (Fed/CPI/OPEC) ≤5 days hitting name = exclude.
3. Ex-div ≤5 days = skip; include special dividend cuts.

Price-action sanity:
1. ±8% move today = skip unless NHSU ≥3500.
2. Unconfirmed premarket gap >3% = skip.
3. Postmarket spike >5% sans news = exclude.

Safety checks:
1. Re-check halts/bankruptcies/delistings last 24h; use exchanges.
2. Agency probe sans DTE date = deprioritize; –800 NHSU.
3. Verify no fraud/SEC halts via EDGAR.

Diversity:
1. Mix sub-themes/sector (e.g., Energy: major, services, renewable).
2. Avoid correlated mega-caps if alternatives exist.
3. Balance: 1 large, 1 mid, 1 small cap/sector.

Fallback discipline:
1. Fallback: no catalyst text; pick ETF weight, then cap, alpha.
2. Pinned name stopped = skip; audit "pinned skipped: [reason]".
3. Audit: log top 3 skips/sector, reasons; note per pick: headline, time, source, NHSU, IV boost.
```
