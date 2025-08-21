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

```python
open 

## ▪️ Prompt for News Heat Ticker Picker

```text
# Ticker Selection Prompt

**Date**: 2025-08-20 18:17 PDT

## 1. Universe & Selection (9 points)
1. **Pick Stocks**: Select 3 stocks/sector (27 total) from CSVs (xlc, xle, xlf, xli, xlp, xlk, xlv, xlu) for 0–33 DTE credit spreads.
2. **Show Table**: Build table: Sector | Ticker | News Heat | IV % | Open Interest. Sort by sector (A–Z), News Heat (high-low).
3. **Set Rules**: Include pin=[...] if safe, exclude ban=[...]. Pick U.S. stocks, skip ADRs <500K volume.
4. **Grab Data**: Use IR, SEC, DOJ/FTC/FDA, Reuters, Bloomberg, WSJ, Nasdaq, Yahoo, Tastytrade (IV, OI). Skip unverified rumors.
5. **Vary Picks**: Mix sector themes (e.g., XLE: major, service, renewable) and sizes (large, mid, small cap).
6. **Plan B**: If <3 stocks with News Heat ≥1000, use CSV weights, then market cap, alphabetical.
7. **Dodge Volatility**: Skip >8% daily moves unless News Heat ≥3500.
8. **Aim Big**: Favor >$2B market cap stocks unless pinned.
9. **Track Picks**: Log skips (e.g., “AAPL: earnings soon”), headline, timestamp, source, News Heat.

## 2. News & Scoring (6 points)
1. **Hunt News**: Fetch data (≤72h, best ≤24h): filings, launches, mergers, CEO shifts, buybacks, regulators, Fed/CPI, analyst notes, lawsuits.
2. **Score Heat**: Set top score: 4000 (merger), 3500 (product, regulatory), 1500 (analyst, buyback, contract), 1200 (lawsuit, strike), 500 (minor), 0 (none). Cut 200 for >24h. Need ≥1000 for news.
3. **Block Risks**: Skip earnings in 0–33 DTE, macro ≤5 days (Fed/CPI/OPEC/FDA), dividends ≤5 days.
4. **Tastytrade Check**: Filter IV % 50–80, OI >500/strike (Tastytrade, 0–33 DTE options).
5. **Stay Tight**: Use live, timestamped sources. Merge same-event links. Clash = no news. Max 2 same-news/sector.
6. **Max Edge**: Favor high IV, News Heat for premium, catalyst-driven trades.

## 3. Execution & Output (3 points)
1. **Move Quick**: Spend ~60s/sector. Timeout → backups (“timeout”). Check halts, bankruptcies (24h).
2. **Make Table**: Show table: Sector | Ticker | News Heat | IV % | Open Interest. Sort sector (A–Z), News Heat (high-low).
3. **Log It**: Save skips, headlines, timestamps, sources, News Heat.
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

```text
Date: [enter date & time]

Universe (must use): Only credit spreads from final_credit_spread_comparison.json (has AI = GPT/Grok).
Include all spreads with 0–45 DTE; exclude any over 45 DTE, missing strikes/premiums/probabilities, or invalid data like negative values or mismatched types.
Goal (must do): Validate each 0–45 DTE spread against current market reality.
Check for risks that could blow up the trade; base on real-time facts only, no guesses or assumptions.
Output: Table only — AI Bot Name | Ticker | Type | Legs| DTE | PoP | ROI | Current Risk | Final Status — one row per spread | heat score 
Sort by ticker alphabetically; use bold for Critical/High risks.


What to fetch now (real-time, verifiable):
1. Earnings collision: Company IR pages, earnings calendars from Nasdaq/Yahoo Finance/Seeking Alpha/Zacks, analyst calls/transcripts, quiet period ends (next 45 days; include guidance updates, pre-announcements, post-earnings drifts).
2. Major news catalysts: Press releases, 8-K/6-K filings, conference presentations/speeches, product launches/recalls, mergers/acquisitions/deals, executive changes/hirings/firings, dividend announcements/changes, stock splits/buybacks (≤ 72h).
3. Regulatory/court: SEC filings/enforcements/investigations, DOJ antitrust suits/probes, FDA approvals/denials/recalls/warnings, ITC patent rulings/injunctions, FTC merger blocks/probes, CPSC safety alerts/recalls, EPA violations/fines, IRS tax disputes (≤ 72h).
4. Macro conflicts: Fed speeches/Jackson Hole/FOMC minutes/decisions/rate cuts, BLS CPI/PPI/Jobs reports/unemployment claims/retail sales, Treasury auctions/yields, GDP revisions/estimates, ECB/BOE/BOJ policy shifts/announcements, OPEC meetings/oil quotas (next 10 trading days).
5. Trading anomalies: Exchange halts/suspensions/delists, circuit breakers triggered, unusual volume (top 1% today or >300% avg), short squeezes/float data, options expiration effects/pin risks (today or next session), dark pool activity spikes.
6. Technical red flags: >8% price move today without confirmed catalyst, gap opens/closes >5%, 52-week high/low breaks, volatility spikes (VIX >30 or stock IV >50% or >2x avg), analyst downgrades/upgrades/ratings changes (today), RSI overbought/oversold extremes.
7. Sector impacts: Industry-specific events like oil inventory reports (EIA/API), semiconductor tariffs/chip shortages, crypto regulations/bans/halvings, airline safety probes/incidents (FAA), banking stress tests (Fed), real estate data (housing starts/mortgages) (≤ 72h).
8. Global risks: Geopolitical tensions (wars/conflicts, sanctions/trade wars, elections/results), natural disasters affecting ops (hurricanes/floods, earthquakes/volcanoes), supply chain disruptions (strikes/labor issues, port closures/congestion, chip/fuel shortages).
9. Corporate finance: Debt offerings/refinancings, credit rating changes (Moody's/S&P), insider trading filings (Form 4), activist investor letters/positions (13D/G), proxy fights/board battles (≤ 72h).

Hard rules (binary, pass/fail):

1. Live, named, timestamped source that names the ticker explicitly; no generic, aggregated, or unnamed data.
2. ≤72h max age for news/catalysts; older = no conflict, treat as clean; ignore archived or historical items.
3. Earnings inside DTE = automatic fail (skip entire spread); include any related events like calls or guidance.
4. No speculation; confirmed/documented events only; ignore rumors, unverified tweets/social media, forward-looking opinions, or analyst predictions without facts.
5. Primary > secondary: Company IR/SEC filings → Fed/BLS/regulator sites → Reuters/Bloomberg/WSJ/AP/CNBC → exchange sites (NYSE/Nasdaq) → Yahoo Finance/Investing.com/MarketWatch.
6. Verify with multiple sources if conflicting; default to primary if tie; if no data after thorough check, assume low risk but note "clean scan."

Action steps (risk → status → build): Step 1 — Current Risk (pick highest applicable; list all factors briefly in cell):
1. Critical (auto-skip): Earnings in DTE; trading halt/suspension/delisting; bankruptcy filing; fraud probe/SEC halt; CEO arrest/resignation under duress; major lawsuit loss.
2. High: Major catalyst ≤24h (e.g., merger vote/close, verdict/settlement); Fed event ≤5 days; Price spike >8% today; volume surge >500% avg without cause; IV explosion >100% baseline; short squeeze in play.
3. Medium: Minor catalyst ≤72h (e.g., analyst note, small deal, exec change); Macro event 5–10 days (e.g., jobs/CPI report); Price move 3–8% today; moderate volume bump 200–500%; sector news spillover; mild IV rise.
4. Low: Clean news flow; no scheduled events in horizon; normal tape activity; price stable <3% today; standard volume/IV; no flags.

Step 2 — Final Status:

1. PROCEED: Low only (safe to enter full size; no issues).
2. MONITOR: Medium (consider smaller size, tighter stops, or hedge; watch closely).
3. SKIP: High or any Critical (avoid entirely; too risky now).
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
