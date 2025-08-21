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

## ▪️ Prompt for News & Events Heat

```python
# Optimized Prompt — Ultra-Condensed

**Goal:** +10% flips, **0–33 DTE** credit spreads.  
**Universe:** Only **your sector CSV** tickers.  
**Method:** **News/events = edge** (no quotes/IV/Greeks).

## Foundation
1. **Lock universe:** CSV tickers only; uppercase, dedupe; **common stock**.  
2. **Fresh news:** **≤7d** credible coverage required; else **skip**.  
3. **Prime window:** **Today** or **yesterday after close** preferred.  
4. **Tradable heat:** Steady follow-through > halts/gaps/whipsaws.  
5. **Source tiers:** **PR/EDGAR/IR/Govt** > Tier-1 media > **X** (verify).  
6. **Earnings guard:** If **earnings ≤33d**, **exclude**.  
7. **Other binaries:** FDA/votes/courts/product dates **≤33d** → **exclude**.  
8. **Imminent events:** If **≤24h** scheduled event, **skip**.  
9. **Sector balance:** **≤3** tickers per sector; don’t force.

## Edge Engine
1. **Catalyst hunt:** Last **≤72h**; M&A, guidance, FDA, big deals, multi-analyst.  
2. **Rank order:** **Durability > Recency > Source quality**; multi-confirm = boost.  
3. **Bias map:** Bullish → **bull put**; Bearish → **bear call**; unclear → **pass**.  
4. **Tone check:** “Orderly follow-through” **in**; “too hot” **out**.  
5. **Score:** **High/Med/Low** + 1-liner **why** + **citation**.  
6. **Tiebreak:** More durable catalyst; article-hinted S/R/breakout wins.

## Execution
1. **Pick list:** Top **≤3** per sector that clear all guards.  
2. **Flip plan:** Open spread; **+10% TP**; **headline stop**; **time stop**.  
3. **Output table:** **AI Bot | Sector | Ticker | Bias | Catalyst | Flip Plan | Edge | Citation(s)**.
```

## ▪️ Instructions for Edge 

```python
# Optimized Edge Instructions — Ultra-Condensed

## 1) Free Data You Can Trust
- **CSV lists:** Your sector tickers = **only universe**.  
- **News search:** Google News / web; **link sources**.  
- **Company IR/PR:** Official feeds; **primary proof**.  
- **SEC EDGAR:** **8-K/10-Q/10-K** for material events.  
- **Tier-1 media:** **Reuters/Bloomberg/WSJ/AP/CNBC/MarketWatch/Yahoo**.  
- **Earnings check:** Free web/IR mention; exclude **≤33d**.  
- **Social/X:** **Heads-up only** → must **confirm** elsewhere.

## 2) Repeatable Edge Signals
- **Recency drive:** **≤72h** beats old headlines.  
- **Confirmation:** Multiple credible sources = **conviction**.  
- **Liquidity proxy:** Large-cap, index constituents, household names.  
- **Sector themes:** Catalyst + sector tailwind = **durability**.  
- **PR quality:** Guidance raises, buybacks, contracts > rumors.  
- **Reaction tells:** Articles noting follow-through > one-off pop.

## 3) Hard Limits / Guardrails
- **No live quotes/IV/Greeks:** **News-only** edge.  
- **No chain checks:** Your algo picks strikes/premiums.  
- **No charts:** Use article context (e.g., “52-week high”).  
- **Public info only:** Paywalled/API data **excluded**.  
- **Miss risk:** If **uncertain on earnings/events**, **exclude**.  
- **Advisory:** You manage sizing, fills, and execution.
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

> **Mission fit:** Rank only the 0–33 DTE **credit** spreads already produced by your algo (the JSON). Use **only fields present or derivable** from that JSON.

---

## JSON Analysis (edge-focused)
- **Robust parse (guaranteed fields):** Read each spread’s `AI_bot_name`, `Sector`, `Ticker`, `Spread_Type`, `Legs` (e.g., `$200/$202`), `DTE` (int), `PoP` (e.g., `52.5%`), `ROI` (e.g., `108.3%`), `Net_Credit` (e.g., `$1.30`), `Distance_From_Current` (e.g., `0.6%`).
- **Derive risk math (from Legs + credit):** Compute **width** = |long − short|, **credit** (float), **max_loss** = width − credit, **R:R** = credit / max_loss. (No external prices needed.)
- **Normalize metrics (for scoring):** Convert PoP/ROI/Distance strings → floats; cap ROI for stability (e.g., at 200%) and guard negatives/NaNs.
- **Bias & type sanity:** Map `Spread_Type` → bias label (**Bear Call → Call-Credit**, **Bull Put → Put-Credit**) and ensure Legs are ordered correctly (short vs long leg direction).
- **DTE banding for flips:** Tag **optimal** (7–21 DTE), **acceptable** (22–33), **out-of-scope** (>33 should not appear, but if it does → drop).
- **Distance buffer use:** Read `Distance_From_Current` (%) as the **price buffer** to the short strike; treat <0.5% as **thin buffer** (riskier), ≥0.5% as **acceptable** for flips.
- **Optional Stage-1 filter:** If a Stage-1 ticker list is supplied, **keep intersection**; if not, **use all** JSON tickers (fully doable both ways).
- **De-duplication & variants:** Collapse **duplicate structures** (same ticker/type/legs/DTE) across bots; keep the best (higher score) to avoid double counting.
- **Audit trail:** Persist the parsed/derived fields per spread so the score and rank are **explainable** (no black boxes).

---

## Basic Scoring (transparent, calculable)
- **PoP weight (win-rate core):** Base = **PoP** (0–100). Higher PoP = higher base score. (Rationale: consistent flips prefer high probability.)
- **ROI weight (payout per risk):** Add **w_ROI × ROI%**, with ROI% **capped** (e.g., 200) and **diminishing** beyond 120%. Suggested **w_ROI = 0.35**.
- **Distance boost (safety):** Add **w_DIST × Distance%** with a **floor** at 0.5% (thin buffers get less). Suggested **w_DIST = 8** (so +0.6% ≈ +4.8 pts).
- **DTE shape (flip-friendly):** Add **+6 pts** if 7–21 DTE, **+3 pts** if 22–33, **−5 pts** if <7 (too gamma-hot). (JSON is pre-filtered ≤33; we still reward the sweet spot.)
- **Width sanity (risk realism):** Penalize extremes: **−4 pts** if width < $1.00 (often too tight/slow), **−4 pts** if width > $10 (capital heavy). Mild +2 for $3–$5 widths (practical sweet spot).
- **Final score (linear, explainable):**  
  `Score = PoP + 0.35·ROI_capped + 8·Distance% + DTE_bonus + Width_adj`  
  (All inputs come from JSON or are derivable; weights are editable constants in your code.)

---

## Selection & Output (simple, repeatable)
- **Rank & diversify:** Sort by **Score (desc)**. Enforce **sector balance** if desired (e.g., max 1–2 per ticker / evenly across sectors).
- **Keep what you can trade:** If two rows are near-identical, keep the **higher Score** and drop the twin; prefer the **optimal DTE band** when tied.
- **Final output (columns you already use):**  
  **AI Bot | Sector | Ticker | Spread_Type | Legs | DTE | PoP | ROI | Score**
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
