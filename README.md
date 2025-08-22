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
#Prompt

## Foundation

1. **Lock universe:** Sector CSV tickers only; uppercase, dedupe; common stock; prioritize large-cap/index for liquidity/tight spreads (alphaarchitect.com).
2. **Fresh news:** ≤7d credible coverage required; prioritize PR/EDGAR/IR/Govt; economic news > social (mdpi.com); skip without.
3. **Prime window:** Today/yesterday after close preferred; backtests show 15-20% win boost (arxiv.org).
4. **Tradable heat:** Steady follow-through > halts/gaps/whipsaws; avoid ±10% gaps (83% 0DTE loss, tradestation.com).
5. **Source tiers:** PR/EDGAR/IR/Govt > Tier-1 (Reuters/Bloomberg/WSJ); X semantic verify for real-time sentiment; multi-source +10% edge (mdpi.com).
6. **Earnings guard:** Exclude ≤33d; 94% win drop post-volatility (tradestation.com).
7. **Binaries:** FDA/votes/courts/product dates ≤33d → exclude; 70% short DTE failure; satellite alt-data for retail prediction (haas.berkeley.edu).
8. **Imminent events:** ≤24h scheduled → skip; gamma 2x spike (arxiv.org).
9. **Sector balance:** ≤3/sector; high IVR (50%+) for premium; don't force; balance bull/bear with macro context (e.g., CPI/yields).

## Edge Engine

1. **Catalyst hunt:** ≤72h; M&A/guidance/FDA/deals/multi-analyst; durable > recency (6% ROC, arxiv.org).
2. **Rank:** Durability (multi-confirm) > Recency > Quality; boost S/R breakout hints via X semantic.
3. **Bias:** Bullish → bull put; Bearish → bear call; unclear → pass; align with 83-95% wins; LLMs predictive (arxiv.org).
4. **Tone:** Orderly > hot; theta in 7-21 DTE (85% QQQ 0DTE, tradestation.com).
5. **Score:** High/Med/Low + why/citation; tiebreak: IV tailwind (50%+) or alt-data (satellite parking, haas.berkeley.edu).
6. **Quant filter:** Large-cap/index; 91% win vs 74% (alphaarchitect.com); contrarian check (priced-in?).

## Execution

1. **Pick:** Top ≤3/sector clearing guards; focus 0-33 DTE low delta; AI as assistant (alphaarchitect.com).
2. **Flip: Open** spread; +10% TP; headline stop; time stop (EOD); verify code sim.
3. **Table:** AI Bot | Sector | Ticker | Bias | Catalyst | Flip Plan | Edge | Citation(s).

------

#Instructions

## Foundation

**Free data:** CSV tickers; Google/EDGAR/IR; no APIs/paywalls; X semantic for verification (mdpi.com).
**Confirmation:** Multi-source > solo; X as alert, confirm Tier-1; economic > social (mdpi.com).
**Liquidity:** Large-cap/index; proxy <1% ATM spread (tradestation.com).
**Themes:** Catalyst + sector tailwind/macro; e.g., XLE deals + oil rally (durability +15% ROC, arxiv.org).
**PR:** Guidance/buybacks/contracts > rumors; +15% ROC (alphaarchitect.com).
**Reaction:** Follow-through > pop; S/R wins via article/X context.
**Guards:** Earnings/binaries → drop; scheduled ≤24h → skip.
**Miss:** Uncertain → exclude; public only; add alt-data hints (satellite, haas.berkeley.edu).
**Advisory:** Sizing/fills managed; delta 5-10 edge (83-95% wins, arxiv.org); AI assistant (alphaarchitect.com).

## Edge Engine

**Recency:** ≤72h > old; +20% conviction (mdpi.com).
**Themes:** Backtested wins e.g., 94% SPX 0DTE (tradestation.com).
**IV:** High relative >20%; premium edge.
**Heat:** Tradable > chaos; gamma <7 DTE.
**Bias:** Match spread; bull put +ve news; sentiment via X semantic.
**Score:** Transparent; win rate data; what-if risks (arxiv.org).

Execution

**Output:** Table; sort score.
**Plan:** +10% TP; headline/time stops.
**Limit:** 3/sector; data exclusions; contrarian filters.
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


### GROK 4

```python
# Prompt 

## Foundation

**Parse:** JSON fields; %/$ → floats; guard NaN/negatives.
**Derive:** Width = |long-short|; credit = Net_Credit; max_loss = width-credit; R:R = credit/max_loss >0.33.
**Sanity:** Order legs bull put/bear call; de-dupe Ticker+Type+Legs+DTE.
**Scope:** 0-33 DTE; tag 7-21 optimal (6% ROC, tradestation.com), 22-33 acceptable, <7 gamma-hot.
**Buffer:** Distance_From_Current; <0.5% thin; +8% edge ≥0.5% (tradestation.com).
**Catalyst:** ≤72h confirm; PR/8-K > media; multi-source via X semantic (mdpi.com).
**Direction:** Bullish → bull put; Bearish → bear call; mismatch → skip.
**Guards:** Earnings/binaries ≤33d → drop; ≤24h event → skip; chaos/gaps → too hot.
**Score:** ROI_cap=200, w_ROI=0.35, w_DIST=8; bonuses +6 (7-21), +3 (22-33), -5 (<7); POP ≥65%.

## Edge Engine

**Width:** -4 (<$1), +2 ($3-5), -4 (>$10); $3-5 sweet (tradestation.com).
**Formula:** Score = POP + 0.35ROI_cap + 8buffer% + DTE_bonus + Width_adj.
**Enter:** Bias match + high score + buffer ≥0.5% + not hot.
**Hold:** Aligned but thin/aging → watchlist.
**Skip:** Mismatch/binaries/chaos/no confirm.
**Quant:** Delta 5-10 equiv (83-95% wins, alphaarchitect.com); alt-data boost (satellite, haas.berkeley.edu); LLM predictive (arxiv.org).

## Execution

**Table:** AI Bot | Sector | Ticker | Type | Legs | DTE | PoP | ROI | R:R | Buffer% | Score | Bias | Catalyst | Action | Flip Plan | Citation(s).
**Sort:** Score ↓; top 1/ticker post de-dupe.
**Plan:** Open spread; +10% TP; headline stop; time stop (EOD/next).

------

# Instructions 

## Foundation

**JSON:** Math/filters/score from fields; no live IV/Greeks.
**News:** PR/EDGAR/IR/Tier-1; earnings via IR/web; economic > social (mdpi.com).
**No chains:** Algo strikes/premiums.
**Outlook:** Match spread to catalyst; ≤72h recency.
**Heat:** Follow-through > halts; theta 7-21 DTE (94% wins, tradestation.com).
**IV:** Proxy high via news; drop <20%.
**Guards:** Binaries/earnings → drop; mismatch → skip.
**Width:** $3-5 practical; avoid extremes.
**Score:** Transparent; ROI cap >120% diminishing; macro/alt context (haas.berkeley.edu).

Edge Engine

**POP:** Base 70-95% (backtests SPY/QQQ, arxiv.org).
**ROI:** Payout/risk; +theta short DTE.
**Buffer:** ≥0.5% safety; gamma <7 DTE.
**DTE:** 7-21 sweet (94% wins); 22-33 ok.
**Catalyst:** Multi-source > stale; tailwind durability; X sentiment.
**Action:** Enter high + aligned; watch thin; what-if risks (alphaarchitect.com).

Execution

**Table:** Specified columns; dedupe.
**Plan:** +10% TP; headline/time stops.
1. **Output:** Markdown; 1/ticker; AI as assistant (alphaarchitect.com).
```
