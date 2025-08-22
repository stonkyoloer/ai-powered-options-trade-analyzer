# 🚀 News & Event Heat 🔥 Credit Spread Screener

Work in Progress... The script is pulling live market data from tastytrade server. Need a tool or automation for your project or idea? Hit me up, and I’ll build it from scratch!  

---

# 🛠 Set Tastytrade Credentials

**`config.py`** Stores API URL and login credentials, imported and used by other scripts.

---

# 🪐 Define ETF Universe

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

# 🏆 Screen Tickers for Catalysts

## ▪️ Prompt for 3 tickers per sector using news/events.


### GROK 4
```python
# Foundation

1. **Lock universe:** Sector CSV tickers only; uppercase, dedupe; common stock; prioritize large-cap/index for liquidity/tight spreads (alphaarchitect.com).
2. **Fresh news:** ≤7d credible coverage required; prioritize PR/EDGAR/IR/Govt; economic news > social (mdpi.com); skip without.
3. **Prime window:** Today/yesterday after close preferred; backtests show 15-20% win boost (arxiv.org).
4. **Tradable heat:** Steady follow-through > halts/gaps/whipsaws; avoid ±10% gaps (83% 0DTE loss, tradestation.com).
5. **Source tiers:** PR/EDGAR/IR/Govt > Tier-1 (Reuters/Bloomberg/WSJ); X semantic verify for real-time sentiment; multi-source +10% edge (mdpi.com).
6. **Earnings guard:** Exclude ≤33d; 94% win drop post-volatility (tradestation.com).
7. **Binaries:** FDA/votes/courts/product dates ≤33d → exclude; 70% short DTE failure; satellite alt-data for retail prediction (haas.berkeley.edu).
8. **Imminent events:** ≤24h scheduled → skip; gamma 2x spike (arxiv.org).
9. **Sector balance:** ≤3/sector; high IVR (50%+) for premium; don't force; balance bull/bear with macro context (e.g., CPI/yields).

# Edge Engine

1. **Catalyst hunt:** ≤72h; M&A/guidance/FDA/deals/multi-analyst; durable > recency (6% ROC, arxiv.org).
2. **Rank:** Durability (multi-confirm) > Recency > Quality; boost S/R breakout hints via X semantic.
3. **Bias:** Bullish → bull put; Bearish → bear call; unclear → pass; align with 83-95% wins; LLMs predictive (arxiv.org).
4. **Tone:** Orderly > hot; theta in 7-21 DTE (85% QQQ 0DTE, tradestation.com).
5. **Score:** High/Med/Low + why/citation; tiebreak: IV tailwind (50%+) or alt-data (satellite parking, haas.berkeley.edu).
6. **Quant filter:** Large-cap/index; 91% win vs 74% (alphaarchitect.com); contrarian check (priced-in?).

# Execution

1. **Pick:** Top ≤3/sector clearing guards; focus 0-33 DTE low delta; AI as assistant (alphaarchitect.com).
2. **Flip: Open** spread; +10% TP; headline stop; time stop (EOD); verify code sim.
3. **Table:** AI Bot | Sector | Ticker | Bias | Catalyst | Flip Plan | Edge | Citation(s).
```

### ▪️ ChatGPT 5
```
# Prompt

## Foundation

1. Universe Lock: Only sector CSV tickers; uppercase, dedupe; exclude ETFs/indices.
2. News Recency: Must have ≤7-day credible news; ≤72h preferred; backtests show recency boosts spread win rates +15–20%.
3. Prime Window: Favor catalysts posted today or yesterday after close; aligns with strongest next-session drift.
4. Source Tiers: PR/EDGAR/IR/Govt > Tier-1 (Reuters/Bloomberg/WSJ) > social (verify only). Multi-source confirm = +10% edge.
5. Earnings Guard: Exclude if earnings ≤33 days; backtests show 94% win-rate drop post-earnings volatility.
6. Other Binaries: FDA/votes/courts/product approvals ≤33 days → exclude; 70% fail rate in short DTE trades.
7. Imminent Events: Skip tickers with scheduled material events in ≤24h; gamma spikes ≈2× in 0DTE windows.
8. Technical Check: Favor trades near support/resistance; e.g. bull put at support. Studies show S/R improves credit spread outcomes .
9. Sector Balance: ≤3 tickers/sector; don’t force fills. High IVR (≥50%) names prioritized for richer premium.

## Edge Engine

1. Sentiment Classify: GPT labels catalysts bullish/bearish; align spread type (bull put vs bear call).
2. Multi-Source Confirmation: Require at least 2 credible confirmations; single-source news skipped.
3. Durability > Recency: Prefer catalysts with structural impact (guidance raise, buybacks, contracts) vs one-off hype.
4. Tone Analysis: Favor “orderly follow-through”; reject “halted/gapped/whipsaw” language.
5. Alt-Signal Boost: GPT cross-checks for supporting cues (Google Trends, analyst revisions, institutional flow). Durable + alt confirm = edge.
6. Scoring: High/Med/Low rating + 1-liner rationale + citation. Tie-break to more durable/sector-aligned catalyst.

##Execution

1. Select: Pick ≤3 per sector clearing all guards.
2. Flip Plan: Open aligned spread; +10% TP, headline stop, time stop (EOD/next).
3. Output: Markdown table → Bot | Sector | Ticker | Bias | Catalyst | Flip Plan | Edge | Citation(s).


# Instructions
......

```






### GPT 5
```python
# 🤖 Analyze Credit Spreads via Pipeline

## ▪️ How to Execute 

Run `individual steps` or use the `master pipeline`

```python

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

## ▪️ Definitions:


**`sectors.py`** Sets tickers for querying.

**`build_universe.py`** Tests tickers for options chains.

**`spot.py`** Fetches current stock prices for strikes.

**`ticker_ranker.py`** Ranks stocks by options liquidity.

**`options_chains.py`** Downloads option contracts for spreads.

**`greeks.py`** Gets option prices and Greeks for PoP/ROI.

**`spread_analyzer.py`** Builds spreads, calculates PoP/ROI, picks best.

---



# 💯 Generate Strategy and Game Plan

## ▪️ Prompt for Report with Catalyst Heat, Bias, and Trade Plan.

```python
# Credit-Spread Optimizer — Ultra-Condensed Prompt (JSON End Step)

**Goal:** Rank & select **0–33 DTE** **credit** spreads from your JSON; align with **real catalysts**; output **trade suggestions**.  
**Inputs:** JSON fields only: `AI_bot_name, Sector, Ticker, Spread_Type, Legs, DTE, PoP, ROI, Net_Credit, Distance_From_Current`.  
**No:** live quotes/IV/Greeks.

## Parse & Derive
1. **Normalize:** Parse %/$ → floats; guard NaN/negatives.  
2. **Width/Credit:** `width = |long−short|`; `credit = Net_Credit`; `max_loss = width−credit`; `R:R = credit/max_loss`.  
3. **Leg sanity:** Ensure legs ordered correctly for **Bull Put**/**Bear Call**.  
4. **Scope:** Keep **0–33 DTE**; tag **7–21 Optimal**, **22–33 Acceptable**, **<7 Hot**.  
5. **Buffer:** `buffer% = Distance_From_Current`; **<0.5% = thin**.  
6. **De-dupe:** Same `Ticker+Spread_Type+Legs+DTE` → keep **highest Score**.

## Catalyst Alignment (≤72h)
7. **Confirm news:** **PR/IR/8-K/Govt** > **Tier-1 media**; **X** = heads-up only (must verify).  
8. **Direction map:** **Bullish → Bull Put OK**; **Bearish → Bear Call OK**; **No/unclear → Neutral**.  
9. **Guards:** **Earnings/binaries ≤33d → drop**; **scheduled event ≤24h → skip**; **halts/whipsaws/±>10% gaps → too hot**.

## Score (transparent)
10. **Weights:** `ROI_cap=200`, `w_ROI=0.35`, `w_DIST=8`.  
11. **Bonuses:** **+6** (7–21 DTE), **+3** (22–33), **−5** (<7).  
12. **Width adj:** **−4** (<$1), **+2** ($3–$5), **−4** (>$10).  
13. **Formula:** `Score = PoP + 0.35·ROI_cap + 8·buffer% + DTE_bonus + Width_adj`.

## Action Logic
14. **Enter:** Bias matches catalyst **AND** `Score` high **AND** buffer ≥0.5% **AND** not “too hot”.  
15. **Hold/Watch:** Bias matches but **thin buffer** or aging news (>72h) → watchlist.  
16. **Skip:** Bias mismatch, binaries/earnings flagged, chaos, or missing confirmation.

## Output (Markdown table)
**Columns:** `AI Bot | Sector | Ticker | Spread_Type | Legs | DTE | PoP | ROI | R:R | Buffer% | Score | Bias | Catalyst (1-liner) | Action | Flip Plan | Citation(s)`  
**Sort:** `Score ↓`. **Limit:** **top 1 per ticker** (post de-dupe).  
**Flip Plan template:** “Open credit spread; **+10% TP**, **headline stop**, **time stop (EOD/next session)**.”
```

## ▪️ Instructions for Prompt 

```python
# Optimized Edge Instructions — Ultra-Condensed (JSON End Step)

## 1) What You Can Use (free, repeatable)
- **JSON**: all math/filters/score from provided fields.  
- **News**: **PR/IR/8-K/Govt**, **Reuters/Bloomberg/WSJ/AP/CNBC/MarketWatch/Yahoo**.  
- **Earnings/binaries**: free web/IR mention; if **≤33d**, **drop**.  
- **No live chains/IV**: strikes/premiums handled by your algo.

## 2) Edge Levers
- **PoP** = base consistency.  
- **ROI (capped)** = payout per risk (diminishing >120%).  
- **Buffer%** = safety margin (≥0.5% preferred).  
- **DTE band** = 7–21 sweet spot; 22–33 okay; <7 gamma-hot.  
- **Width** = practicality: $3–$5 sweet; avoid <$1 or >$10.  
- **Catalyst fit** = spread direction must match news bias.  
- **Recency & confirm** = ≤72h and multi-source > stale/solo.  
- **Heat check** = tradable follow-through > halts/whipsaws.

## 3) Guardrails (drop/skip)
- **Earnings/FDA/votes/court ≤33d** → **drop**.  
- **Scheduled event ≤24h** → **skip**.  
- **Bias mismatch** (bear call on bullish news, etc.) → **skip**.  
- **Thin buffer <0.5%** or **too hot** tape → **skip**/**watch**.  
- **No confirmation** (X rumor only) → **skip**.

## 4) Action Map
- **Enter** = High Score + catalyst-aligned + buffer OK + not hot.  
- **Hold/Watch** = aligned but thin buffer/aging news.  
- **Skip** = any guardrail hit / unclear catalyst.

## 5) Output Shape (for your runbook)
- **Table:** `AI Bot | Sector | Ticker | Spread_Type | Legs | DTE | PoP | ROI | R:R | Buffer% | Score | Bias | Catalyst | Action | Flip Plan | Citation(s)`  
- **Sort:** Score ↓; **dedupe** structures; **1 per ticker**.  
- **Flip Plan:** **+10% TP**, **headline stop**, **time stop (EOD/next)**; your algo handles exact strikes.
```
