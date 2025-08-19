# 🚀 Daily Portfolio and Credit Spread Screeners

"I am now AI, start with $400, ChatGPT vs Grok, I will do whatever they say.  I am not responsible for my actions.  No DD.  No Brains.  JUST VIBES!"  

---
# 🛠 Configure TastyTrade

## `Configure TastyTrade`


# 1️⃣ Select a 72 ticker trading universe

## Download the Trading Universe

`XLK` https://www.sectorspdrs.com/mainfund/XLK

`XLC` https://www.sectorspdrs.com/mainfund/XLC

`XLY` https://www.sectorspdrs.com/mainfund/XLY

`XLP` https://www.sectorspdrs.com/mainfund/XLP

`XLV` https://www.sectorspdrs.com/mainfund/XLV

'XLF` https://www.sectorspdrs.com/mainfund/XLF

`XLI` https://www.sectorspdrs.com/mainfund/XLI

`XLE` https://www.sectorspdrs.com/mainfund/XLE

`XLU` https://www.sectorspdrs.com/mainfund/XLU


## Prompt [gpt5|grok4]
```
Use the attached ticker basket files as the universe.
Select the top 4 tickers per sector/theme for trading 0–45 DTE credit spreads today.
Apply this strict filter framework (real-time only):
  1. Earnings & Macro Events (Scheduled) – Must verify in today’s/week’s earnings calendars or official macro event schedules (Fed, CPI, jobs, OPEC, regulatory). Exclude if unverified.
  2. Headline & News Drivers – Must be sourced from live headlines (upgrades/downgrades, strikes, lawsuits, product launches, sector disruptions). Rank by strength of catalyst.
  3. Implied Volatility Context (Event-Driven) – Only flag if real-time news or analyst notes explicitly cite elevated IV or “fear premium.” Ignore historical averages.
  4. Directional Tilt – Classify bias as bullish, bearish, or neutral only if justified by current event/news flow. If unclear, mark as “Neutral.”
  5. Shock Disconnection / Factor Buckets  – Ensure coverage across growth (Tech/Discretionary), rates (Financials/Utilities), commodities (Energy/Industrials), and defensives (Staples/Healthcare). Avoid clustering.

Output_1 format (table):
  Sector | Ticker | Event/News Driver (1 short sentence, real-time) | Tilt (Bullish/Bearish/Neutral)

Output_2 format (portfolio):

A) PYTHON_PATCH
```python
SECTORS_GPT = {
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Communication Services": {
        "etf": "XLC",
        "description": "ads, platforms, media",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Consumer Staples": {
        "etf": "XLP",
        "description": "defensive cashflows, low vol",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Financials": {
        "etf": "XLF",
        "description": "rate curve/credit sensitivity",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Industrials": {
        "etf": "XLI",
        "description": "capex, global trade, PMIs",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge",
        "tickers": ["T1","T2","T3","T4"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity",
        "tickers": ["T1","T2","T3","T4"],
    },
}


Rules:
  1. Use only real-time, verifiable data.
  2. Exclude any ticker where data cannot be confirmed.
  3. Look ahead for scheduled events today/this week.
```
---

# 2️⃣ Daily Portfolio Screener

## `sectors.py`

```python
open sectors.py
```

## `build_universe.py`


## `spot.py`


## `atm_iv.py`


## `liquidity.py`


## `run_pipeline.py`

```python
python3 runpipeline.py
```

---

# 3️⃣ Daily Credit Spread Screener


## `stock_prices.py`


## `options_chains.py`


## `iv_data.py`


## `market_prices.py`


## `risk_analysis.py`


## `iv_liquidity.py`


## `find_tendies.py`

---

## 📁 Step 7: The Master Script

**Create:** `touch master.py`

**Query:** `open -e master.py`


```bash
import asyncio
import subprocess
import os
from datetime import datetime

async def run_complete_analysis():
    print("🤖 MASTER TRADING ROBOT - COMPLETE CREDIT SPREAD SYSTEM")
    print("=" * 80)
    print("🚀 Running complete credit spread analysis in 7 steps...")
    print("📈 Finding BOTH Bear Call and Bull Put Credit Spreads")
    print("⏰ This will take about 8-10 minutes total")
    print("🧮 Using Black-Scholes with real market data")
    print("=" * 80)
    
    steps = [
        ("stock_prices.py", "Getting current stock prices"),
        ("options_chains.py", "Finding all options contracts"), 
        ("iv_data.py", "Collecting implied volatility data"),
        ("market_prices.py", "Getting real-time bid/ask prices"),
        ("risk_analysis.py", "Analyzing Greeks and risk metrics"),
        ("iv_liquidity.py", "Advanced IV & liquidity analysis"),
        ("find_tendies.py", "Elite credit spread scanner")
    ]
    
    start_time = datetime.now()
    
    for i, (script, description) in enumerate(steps, 1):
        print(f"\n🎯 STEP {i}/7: {description}")
        print(f"🏃‍♂️ Running {script}...")
        
        try:
            # Run the script and wait for it to finish
            result = subprocess.run(['python3', script], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                print(f"   ✅ Step {i} completed successfully!")
                # Print some of the output so we can see progress
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    # Show last few meaningful lines
                    meaningful_lines = [line for line in lines[-6:] if line.strip() and not line.startswith('   ')]
                    for line in meaningful_lines[-3:]:  # Show last 3 meaningful lines
                        if '✅' in line or '💎' in line or '🏆' in line or 'Found' in line:
                            print(f"      {line}")
            else:
                print(f"   ❌ Step {i} failed!")
                print(f"   Error: {result.stderr}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Step {i} took too long (over 5 minutes)")
            return False
        except Exception as e:
            print(f"   ❌ Error running step {i}: {e}")
            return False
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print(f"\n🎉 ALL STEPS COMPLETED!")
    print("=" * 80)
    print(f"⏰ Total time: {total_time/60:.1f} minutes")
    print(f"📁 Files created:")
    print(f"   📊 step1_stock_prices.json")
    print(f"   🎰 step2_options_contracts.json") 
    print(f"   📈 step3_iv_data.json")
    print(f"   💰 step4_market_prices.json")
    print(f"   🧮 step5_risk_analysis.json")
    print(f"   📊 step6_advanced_iv_liquidity.json")
    print(f"   🏆 step7_elite_spreads.json")
    
    # Show final summary from the complete credit spread analysis
    try:
        import json
        with open('step7_elite_spreads.json', 'r') as f:
            final_data = json.load(f)
        
        print(f"\n🏆 COMPLETE CREDIT SPREAD RESULTS:")
        print(f"   🧮 Model: Black-Scholes with real market data")
        print(f"   📊 Total opportunities: {final_data['total_spreads_found']}")
        print(f"   📈 Bear Call Spreads: {final_data['bear_call_spreads']}")
        print(f"   📉 Bull Put Spreads: {final_data['bull_put_spreads']}")
        
        if final_data.get('elite_spreads') and len(final_data['elite_spreads']) > 0:
            best_spread = final_data['elite_spreads'][0]
            
            print(f"\n   🥇 BEST ELITE SPREAD:")
            print(f"      📈 {best_spread['company']} Bear Call ${best_spread['short_strike']:.0f}/{best_spread['long_strike']:.0f}")
            print(f"      💰 Credit: ${best_spread['credit']:.2f}")
            print(f"      📊 Probability: {best_spread['probability_of_profit']:.1f}%")
            print(f"      💎 ROI: {best_spread['roi_percent']:.1f}%")
            print(f"      🏆 Master Score: {best_spread['master_score']:.1f}/100")
            print(f"      📅 Days to expiration: {best_spread['days_to_expiration']}")
            
            # Show top 3 elite spreads
            top_spreads = final_data['elite_spreads'][:3]
            print(f"\n   🏆 TOP 3 ELITE SPREADS:")
            for i, spread in enumerate(top_spreads, 1):
                print(f"      {i}. {spread['company']} ${spread['short_strike']:.0f}/{spread['long_strike']:.0f}: Score {spread['master_score']:.1f}, {spread['probability_of_profit']:.1f}% PoP, {spread['roi_percent']:.1f}% ROI")
        
        # Show summary stats
        if 'summary_stats' in final_data:
            stats = final_data['summary_stats']
            print(f"\n   📊 SUMMARY STATISTICS:")
            print(f"      💰 Average ROI: {stats['avg_roi']:.1f}%")
            print(f"      📈 Average Probability: {stats['avg_probability']:.1f}%")
            print(f"      🏆 Average Master Score: {stats['avg_master_score']:.1f}/100")
            print(f"      🔥 Average IV: {stats['avg_iv']:.3f}")
    
    except Exception as e:
        print(f"   ⚠️ Could not load final summary: {e}")
        print(f"   📄 Check step7_elite_spreads.json for detailed results")
    
    print(f"\n🎯 COMPLETE TRADING SYSTEM SUMMARY:")
    print(f"   🔬 Mathematical Model: Black-Scholes option pricing")
    print(f"   📊 Data Sources: Real-time tastytrade market data")
    print(f"   📈 Strategies: Bear call spreads (profit when stock doesn't rise)")
    print(f"   🏆 Analysis: 5 legendary trader frameworks combined")
    print(f"   🛡️ Risk Management: Greeks analysis with full liquidity metrics")
    print(f"   💡 Probability: Log-normal distribution with real IV")
    print(f"   🎯 Filters: Master Score > 50, Probability > 65%, ROI > 10%")
    
    # Show which files to examine
    print(f"\n📂 NEXT STEPS:")
    print(f"   1. 🔍 Examine: step7_elite_spreads.json")
    print(f"   2. 📈 Look for: High master score + probability spreads")
    print(f"   3. 🛡️ Check: Liquidity and Greeks data")
    print(f"   4. 🏆 Focus on: Spreads with multiple trader signals")
    
    return True

if __name__ == "__main__":
    # Run the complete analysis system
    asyncio.run(run_complete_analysis())
```

**Run:** `python3 master.py`

---


# [GPT/GROK] Prompt

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

