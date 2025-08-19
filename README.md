# 🚀 Daily Portfolio and Credit Spread Screeners

"I am now AI, start with $400, ChatGPT vs Grok, I will do whatever they say.  I am not responsible for my actions.  No DD.  No Brains.  JUST VIBES!"  

---
# 🛠 Configure TastyTrade

Steps located in `Configure TastyTrade`


# 💡 Build Sector Baskets

## Download the Trading Universe CSV

`XLK` https://www.sectorspdrs.com/mainfund/XLK

`XLC` https://www.sectorspdrs.com/mainfund/XLC

`XLY` https://www.sectorspdrs.com/mainfund/XLY

`XLP` https://www.sectorspdrs.com/mainfund/XLP

`XLV` https://www.sectorspdrs.com/mainfund/XLV

'XLF` https://www.sectorspdrs.com/mainfund/XLF

`XLI` https://www.sectorspdrs.com/mainfund/XLI

`XLE` https://www.sectorspdrs.com/mainfund/XLE

`XLU` https://www.sectorspdrs.com/mainfund/XLU


## Enter Prompt (CSV's attached)
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

# 🪛 Build Daily Screener

## `sectors.py` can be found in this projects files.  copy and past the python output from prompt directly above, open the saved script file and replace the grok and gpt trading universes with the fresh outputs  
---

## `build_universe.py` 

---

## 📂 Bid, Ask, Mid, TS Snapshot

**Create:** `touch spot.py`

**Query:** `open -e spot.py`

```bash
import asyncio, json
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

async def main():
    with open("universe_raw.json") as f:
        names = [r["ticker"] for r in json.load(f) if r["status"]=="ok"]
    sess = Session(USERNAME, PASSWORD)
    out = {}
    async with DXLinkStreamer(sess) as s:
        await s.subscribe(Quote, names)
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time()-start) < 12 and len(out) < len(names):
            try:
                q = await asyncio.wait_for(s.get_event(Quote), timeout=1.5)
            except asyncio.TimeoutError:
                continue
            if not q or q.event_symbol not in names: continue
            bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
            if bid>0 and ask>0 and ask>=bid:
                out[q.event_symbol] = {"bid":bid, "ask":ask, "mid":(bid+ask)/2, "ts":now()}
    with open("step2_spot.json","w") as f: json.dump(out, f, indent=2)
    print("✅ spot quotes:", len(out), "/", len(names))

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `python3 spot.py`

## 📂 Filter for DTE, ATM IV, IVR

**Create:** `touch atm_iv.py`

**Query:** `open -e atm_iv.py`

```bash
import asyncio, json, math
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

WIN_MIN, WIN_MAX = 30, 45

HIGH_VOL = {"TSLA","NVDA","AMD","ROKU","SNAP","GME","AMC"}
MED_VOL  = {"AAPL","MSFT","AMZN","META","GOOGL","NFLX"}

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def pick_exp(chain):
    today = datetime.now(timezone.utc).date()
    best, bestdiff = None, 1e9
    for d in chain.keys():
        dte = (d - today).days
        if WIN_MIN <= dte <= WIN_MAX:
            diff = abs(dte - (WIN_MIN+WIN_MAX)//2)
            if diff < bestdiff: best, bestdiff = (d, dte), diff
    return best if best else (None, None)

def heuristic_ivr(t, iv):
    if not iv or iv<=0: return 0.0, "none"
    if t in HIGH_VOL: lo,hi, m = 0.40,1.20,"heur_high"
    elif t in MED_VOL: lo,hi, m = 0.20,0.60,"heur_med"
    else: lo,hi,m = 0.15,0.50,"heur_def"
    if iv<=lo: return 0.0,m
    if iv>=hi: return 100.0,m
    return 100*(iv-lo)/(hi-lo), m

async def main():
    with open("universe_raw.json") as f: U = [r for r in json.load(f) if r["status"]=="ok"]
    with open("step2_spot.json") as f: SP = json.load(f)

    sess = Session(USERNAME, PASSWORD)
    out = []

    async with DXLinkStreamer(sess) as s:
        for rec in U:
            t = rec["ticker"]
            spot = SP.get(t,{}).get("mid")
            if not spot: 
                out.append({"ticker":t,"status":"no_spot"}); 
                continue
            try:
                chain = get_option_chain(sess, t)
            except Exception as e:
                out.append({"ticker":t,"status":f"chain_err:{e}"}); 
                continue
            if not chain:
                out.append({"ticker":t,"status":"no_chain"}); 
                continue
            exp, dte = pick_exp(chain)
            if not exp:
                out.append({"ticker":t,"status":"no_target_expiry"}); 
                continue
            opts = chain[exp]
            # find ATM by nearest strike (either side)
            atm_sym, atm_diff = None, 1e9
            for o in opts:
                diff = abs(float(o.strike_price) - spot)
                if diff < atm_diff:
                    atm_diff, atm_sym = diff, o.streamer_symbol
            await s.subscribe(Greeks, [atm_sym])
            iv = None
            try:
                g = await asyncio.wait_for(s.get_event(Greeks), timeout=3.0)
                iv = float(g.volatility or 0)
            except Exception:
                pass
            await s.unsubscribe(Greeks, [atm_sym])
            ivr, method = heuristic_ivr(t, iv or 0.0)
            out.append({
                "ticker": t, "status": "ok" if iv else "no_iv",
                "spot": spot, "target_expiry": exp.isoformat(), "dte": dte,
                "atm_iv": iv, "ivr": ivr, "ivr_method": method
            })

    with open("step3_atm_iv.json","w") as f: json.dump(out, f, indent=2)
    ok = sum(1 for r in out if r["status"]=="ok")
    print("✅ ATM IVs:", ok, "/", len(out))

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `python3 atm_iv.py`

## 📂 Filter for Liquidity

**Create:** `touch liquidity.py`
**Query:** `open -e liquidity.py`

```bash
import asyncio, json, statistics
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote, Summary, Greeks
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

SAMPLE_SEC = 15.0
INSIDE_RATIO_MIN = 0.70
NBBO_AGE_MS_MAX  = 1500
TPM_MIN = 20

T1_ABS, T1_REL, T1_OI = 0.05, 0.10, 20000
T2_ABS, T2_REL, T2_OI = 0.10, 0.20, 1000

def med(a): return statistics.median(a) if a else 0.0
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def classify(spread_med, mid_med, oi_avg):
    if spread_med<=T1_ABS and mid_med>0 and (spread_med/mid_med)<=T1_REL and oi_avg>=T1_OI: return "T1"
    if spread_med<=T2_ABS and mid_med>0 and (spread_med/mid_med)<=T2_REL and oi_avg>=T2_OI: return "T2"
    return "T3"

def allowed(tier, mid):
    if tier=="T1": return min(T1_ABS, T1_REL*max(mid,1e-9))
    if tier=="T2": return min(T2_ABS, T2_REL*max(mid,1e-9))
    return 0.0

def nearest_delta(target_sign, target_abs, greeks, opt_meta):
    best, diff_best = None, 1e9
    for sym, g in greeks.items():
        d = float(g.get("delta") or 0)
        typ = opt_meta[sym]["type"]
        if target_sign>0 and typ!="C": continue
        if target_sign<0 and typ!="P": continue
        diff = abs(abs(d)-target_abs)
        if diff < diff_best: best, diff_best = sym, diff
    return best

async def analyze_one(sess, s, tkr, spot, exp_iso):
    # load chain & filter expiry
    chain = get_option_chain(sess, tkr)
    exp = None
    for d in chain.keys():
        if d.isoformat()==exp_iso: exp = d; break
    if not exp: return {"ticker":tkr,"status":"no_expiry"}
    opts = chain[exp]
    symbols = [o.streamer_symbol for o in opts]
    meta = {o.streamer_symbol: {"strike": float(o.strike_price), "type": o.option_type.value} for o in opts}

    greeks, summary, quotes = {}, {}, {}
    await s.subscribe(Greeks, symbols); await s.subscribe(Summary, symbols); await s.subscribe(Quote, symbols)
    start = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time()-start) < SAMPLE_SEC:
        try:
            g = await asyncio.wait_for(s.get_event(Greeks), timeout=0.5)
            if g and g.event_symbol in symbols:
                greeks[g.event_symbol] = {"delta": float(g.delta or 0), "iv": float(g.volatility or 0)}
        except asyncio.TimeoutError:
            pass
        try:
            q = await asyncio.wait_for(s.get_event(Quote), timeout=0.5)
            if q and q.event_symbol in symbols:
                bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
                if bid>0 and ask>0 and ask>=bid:
                    arr = quotes.setdefault(q.event_symbol, [])
                    arr.append((bid,ask))
        except asyncio.TimeoutError:
            pass
        try:
            sm = await asyncio.wait_for(s.get_event(Summary), timeout=0.5)
            if sm and sm.event_symbol in symbols:
                summary[sm.event_symbol] = {"oi": int(sm.open_interest or 0)}
        except asyncio.TimeoutError:
            pass
    await s.unsubscribe(Greeks, symbols); await s.unsubscribe(Summary, symbols); await s.unsubscribe(Quote, symbols)

    call30 = nearest_delta(+1, 0.30, greeks, meta)
    put30  = nearest_delta(-1, 0.30, greeks, meta)
    if not call30 or not put30:
        return {"ticker":tkr,"status":"no_delta30"}

    def stats(sym):
        pts = quotes.get(sym, [])
        if not pts: return None
        spreads = [a-b for (b,a) in pts if a>=b>0]
        mids    = [(a+b)/2 for (b,a) in pts if a>=b>0]
        if not spreads or not mids: return None
        spread_med, mid_med = med(spreads), med(mids)
        allowed_tmp = min(T2_ABS, T2_REL*max(mid_med,1e-9))
        inside_ratio = sum(1 for s in spreads if s<=allowed_tmp)/max(len(spreads),1)
        ticks_pm = 60*len(pts)/max(SAMPLE_SEC,1)
        nbbo_age_ms = 1000*(SAMPLE_SEC/max(len(pts),1))
        return dict(spread_med=spread_med, mid_med=mid_med, inside_ratio=inside_ratio, ticks_pm=ticks_pm, nbbo_age_ms=nbbo_age_ms)

    cs, ps = stats(call30), stats(put30)
    if not cs or not ps:
        return {"ticker":tkr,"status":"insufficient_quotes"}

    spread_med_30 = max(cs["spread_med"], ps["spread_med"])
    mid_med_30    = med([cs["mid_med"], ps["mid_med"]])
    inside_ratio  = (cs["inside_ratio"] + ps["inside_ratio"])/2
    ticks_pm      = (cs["ticks_pm"] + ps["ticks_pm"])/2
    nbbo_age_ms   = med([cs["nbbo_age_ms"], ps["nbbo_age_ms"]])
    oi_min        = min(summary.get(call30,{}).get("oi",0), summary.get(put30,{}).get("oi",0))
    tier          = classify(spread_med_30, mid_med_30, (summary.get(call30,{}).get("oi",0)+summary.get(put30,{}).get("oi",0))/2)
    spread_ok     = spread_med_30 <= allowed(tier, mid_med_30)
    oi_ok         = oi_min >= (T1_OI if tier=="T1" else T2_OI)

    gates = {
        "inside_ratio_ok": inside_ratio >= INSIDE_RATIO_MIN,
        "nbbo_fresh_ok": nbbo_age_ms <= NBBO_AGE_MS_MAX,
        "ticks_ok": ticks_pm >= TPM_MIN,
        "spread_ok": spread_ok,
        "oi_ok": oi_ok
    }
    passed = all(gates.values())

    return {
        "ticker": tkr, "status": "ok" if passed else "failed_gates",
        "tier": tier, "metrics": {
            "spread_med_Δ30": round(spread_med_30,4),
            "mid_med_Δ30": round(mid_med_30,4),
            "inside_threshold_ratio_Δ30": round(inside_ratio,3),
            "ticks_per_min": round(ticks_pm,2),
            "nbbo_age_ms_med": round(nbbo_age_ms,0),
            "oi_min_Δ30": int(oi_min)
        },
        "failure_reasons": [k for k,v in gates.items() if not v]
    }

async def main():
    with open("step3_atm_iv.json") as f: base = {r["ticker"]: r for r in json.load(f) if r["status"]=="ok"}
    sess = Session(USERNAME, PASSWORD)
    results = {}
    async with DXLinkStreamer(sess) as s:
        for tkr, r in base.items():
            res = await analyze_one(sess, s, tkr, r["spot"], r["target_expiry"])
            res.update({"sector": None, "spot": r["spot"], "target_expiry": r["target_expiry"], "dte": r["dte"], "atm_iv": r["atm_iv"], "ivr": r["ivr"]})
            results[tkr] = res
    with open("step4_liquidity.json","w") as f: json.dump(results, f, indent=2)
    ok = sum(1 for x in results.values() if x["status"]=="ok" and x.get("ivr",0)>=30)
    print("✅ liquid Δ30 names (ivr≥30):", ok, "/", len(results))

if __name__ == "__main__":
    asyncio.run(main())
```
**Run:** `python3 liquidity.py`

## 📂 Build Trading Basket 

**Create:** `touch basket.py`
**Query:** `open -e basket.py`

```bash
import json, math
from sectors import SECTORS
# weights (same idea as before)
W_IVR, W_SPREAD, W_DEPTH, W_ABSIV = 0.40, 0.25, 0.25, 0.10

def score(ivr, spread_med, oi_min, abs_iv):
    spread_score = max(0.0, 1.0 - min(spread_med, 0.30)/0.30)
    depth_score  = min((oi_min or 0)/20000.0, 1.0)
    absiv_score  = min((abs_iv or 0)/1.00, 1.0)
    return (W_IVR*(ivr/100.0) + W_SPREAD*spread_score + W_DEPTH*depth_score + W_ABSIV*absiv_score)*100.0

if __name__ == "__main__":
    with open("universe_raw.json") as f: U = json.load(f)
    with open("step4_liquidity.json") as f: LQ = json.load(f)
    with open("step3_atm_iv.json") as f: IVS = {r["ticker"]: r for r in json.load(f)}

    # map sector -> tickers
    sector_map = {}
    for r in U:
        if r["status"]!="ok": continue
        sector_map.setdefault(r["sector"], []).append(r["ticker"])

    portfolio = []
    for sector, meta in SECTORS.items():
        tickers = sector_map.get(sector, [])
        cands = []
        for t in tickers:
            liq = LQ.get(t)
            ivr = IVS.get(t,{}).get("ivr",0)
            atm_iv = IVS.get(t,{}).get("atm_iv",0)
            if not liq or liq["status"]!="ok" or ivr<30: continue
            m = liq["metrics"]
            s = round(score(ivr, m["spread_med_Δ30"], m["oi_min_Δ30"], atm_iv), 1)
            cands.append({"sector":sector,"ticker":t,"tier":liq.get("tier"),"ivr":ivr,"atm_iv":atm_iv,"score":s,"metrics":m})
        if cands:
            best = max(cands, key=lambda x:x["score"])
            best["status"]="ok"; best["reason_codes"]=["IVR≥30","Δ30_spread_ok","OI_ok"]
            portfolio.append(best)
        else:
            portfolio.append({"sector":sector,"ticker":f"NO PICK ({sector})","status":"no_qualifying_ticker"})

    out = {
        "scan_id": IVS[next(iter(IVS))]["target_expiry"] if IVS else "",
        "portfolio": portfolio,
        "qualified_tickers": [p["ticker"] for p in portfolio if p["status"]=="ok"],
        "universe_quality": {
            "sectors_qualified": sum(1 for p in portfolio if p["status"]=="ok"),
            "sectors_total": len(SECTORS)
        }
    }
    with open("portfolio_universe.json","w") as f: json.dump(out, f, indent=2)

    print(f"{'Sector':<22} {'Ticker':<8} {'Score':>6} {'Tier':>4} {'IVR':>6} {'SpreadΔ30':>10} {'OIminΔ30':>10} {'Status':>10}")
    for p in portfolio:
        if p["status"]=="ok":
            m=p["metrics"]
            print(f"{p['sector']:<22} {p['ticker']:<8} {p['score']:>6.1f} {p['tier']:>4} {p['ivr']:>6.1f} {m['spread_med_Δ30']:>10.3f} {m['oi_min_Δ30']:>10} {'OK':>10}")
        else:
            print(f"{p['sector']:<22} {p['ticker']:<8} {'-':>6} {'-':>4} {'-':>6} {'-':>10} {'-':>10} {p['status']:>10}")
    print("💾 Saved: portfolio_universe.json")
```

**Run:** `python3 basket.py`

# ✒️ Prompt for News, Earnings, Macro

```bash
You are my Portfolio News & Risk Sentinel.
Timezone: America/New_York. 
Use absolute dates in YYYY-MM-DD.
Be concise, structured. 
When you fetch news or events, include links and source names. 

INPUT (paste below EXACTLY as produced):
=== portfolio_universe.json ===
{PASTE_JSON_HERE}
=== end ===

TASKS
1) Parse the portfolio. For each sector, identify the chosen ticker (or “no pick”). Pull these fields per ticker if present: ivr, atm_iv, tier, spread_med_Δ30, oi_min_Δ30, dte, target_expiry.
2) News & Catalysts (last 72h + next 14d): 
   - Fetch top 2 materially relevant headlines per ticker (earnings, guidance, M&A, litigation, product, regulation, macro-sensitive items). 
   - Fetch the next earnings date and any known ex-dividend date if within the next 21 days.
   - Note sector-level macro events (e.g., FOMC/CPI for Financials; OPEC/EIA for Energy; FDA/AdCom for Health Care; durable goods/PMI for Industrials).
3) Heat & Flags:
   - Compute a simple NewsHeat 0-5 (0=quiet, 5=major/crowded headlines).
   - Flag “Earnings inside DTE window” if earnings date is ≤ target_expiry DTE. 
   - Flag liquidity concerns if spread_med_Δ30 > 0.10 or oi_min_Δ30 < 1,000.
4) Output as a compact table with these columns:
   Sector | Ticker | NewsHeat(0-5) | Next Event(s) | Risk Flags
5) Add a brief 3-bullet portfolio summary:
   - Diversification status (sectors filled/empty)
   - Top 2 risk clusters (e.g., multiple rate-sensitive names)
   - 1–2 hedge ideas (e.g., XLF/XLK/XLV ETF overlay or pair-trade)

CONSTRAINTS
- No financial advice; provide information and risk context only.
- Cite each headline/event with a link in-line.
- If info is unavailable, write “n/a” rather than guessing.
```

# ✒️ Build a Daily Options Screener


## 📁 Get Stock Prices

### Data: Bid, ask, mid-price, and timestamp for nine stocks.  
### Why useful: Gives a fresh “true price” for each underlying.

**Create:** `touch stock_prices.py`

**Query:** `open -e stock_prices.py`

```bash
# Step 1: Get Stock Prices - Like checking price tags!
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

# Our 9 favorite companies to trade
COMPANIES = [
    'NVDA',  # NVIDIA (makes computer chips)
    'TSLA',  # Tesla (electric cars)
    'AMZN',  # Amazon (online shopping)
    'ISRG',  # Intuitive Surgical (robot surgery)
    'PLTR',  # Palantir (data analysis)
    'ENPH',  # Enphase Energy (solar power)
    'XOM',   # Exxon Mobil (oil company)
    'DE',    # John Deere (farm equipment)
    'CAT'    # Caterpillar (construction equipment)
]

async def get_stock_prices():
    print("🏪 STEP 1: Getting Stock Prices")
    print("=" * 50)
    print("📋 Checking prices for our 9 favorite companies...")
    
    session = Session(USERNAME, PASSWORD)
    stock_prices = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to the stock market...")
        await streamer.subscribe(Quote, COMPANIES)
        print("✅ Connected! Now listening for prices...")
        
        collected = set()
        start_time = asyncio.get_event_loop().time()
        
        while len(collected) < len(COMPANIES) and (asyncio.get_event_loop().time() - start_time) < 30:
            try:
                quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=5.0)
                
                if quote and quote.event_symbol in COMPANIES and quote.event_symbol not in collected:
                    company = quote.event_symbol
                    price = float((quote.bid_price + quote.ask_price) / 2)
                    
                    stock_prices[company] = {
                        'company_name': company,
                        'current_price': price,
                        'buy_price': float(quote.bid_price),
                        'sell_price': float(quote.ask_price),
                        'when_checked': datetime.now().isoformat()
                    }
                    
                    collected.add(company)
                    print(f"   💰 {company}: ${price:.2f}")
                    
            except asyncio.TimeoutError:
                continue
    
    # Save our results
    result = {
        'step': 1,
        'what_we_did': 'Got current stock prices',
        'timestamp': datetime.now().isoformat(),
        'companies_checked': len(stock_prices),
        'stock_prices': stock_prices
    }
    
    filename = 'step1_stock_prices.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved stock prices to: {filename}")
    print(f"📊 Found prices for {len(stock_prices)} companies!")
    return result

if __name__ == "__main__":
    asyncio.run(get_stock_prices())
```

**Run:** `python3 stock_prices.py`


---


## 📁 Get All Options Contracts

### Data: Every call and put that expires within 45 days for each stock—strike price, expiry date, days left, and ticker symbol.  
### Why useful: It lays out all near-term bets you can place.

**Create:** `touch options_chains.py`

**Query:** `open -e options_chains.py`

```bash
import json
from datetime import datetime
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

def get_options_contracts():
    print("🎰 STEP 2: Finding Options Contracts")
    print("=" * 50)
    print("🔍 Looking for all the different bets we can make...")
    
    # Load our stock prices from Step 1
    with open('step1_stock_prices.json', 'r') as f:
        step1_data = json.load(f)
    
    companies = list(step1_data['stock_prices'].keys())
    session = Session(USERNAME, PASSWORD)
    
    all_options = {}
    total_contracts = 0
    
    for company in companies:
        print(f"\n🏢 Looking at {company} options...")
        
        try:
            # Get all the different expiration dates for this company
            option_chain = get_option_chain(session, company)
            
            if not option_chain:
                print(f"   ❌ No options found for {company}")
                continue
            
            print(f"   📅 Found {len(option_chain)} different expiration dates!")
            
            company_options = {
                'company': company,
                'current_stock_price': step1_data['stock_prices'][company]['current_price'],
                'expiration_dates': {},
                'total_contracts': 0
            }
            
            # Look at the first 4 expiration dates (nearest ones)
            exp_dates = sorted(option_chain.keys())[:4]
            
            for exp_date in exp_dates:
                options_list = option_chain[exp_date]
                exp_date_str = str(exp_date)
                
                print(f"   📋 {exp_date_str}: Found {len(options_list)} contracts")
                
                contracts = []
                calls = 0
                puts = 0
                
                for option in options_list:
                    if option.days_to_expiration <= 45:  # Only contracts expiring soon
                        contract_info = {
                            'contract_name': option.symbol,
                            'strike_price': float(option.strike_price),
                            'days_until_expires': option.days_to_expiration,
                            'contract_type': 'CALL' if option.option_type.value == 'C' else 'PUT',
                            'streamer_symbol': option.streamer_symbol
                        }
                        contracts.append(contract_info)
                        
                        if option.option_type.value == 'C':
                            calls += 1
                        else:
                            puts += 1
                
                company_options['expiration_dates'][exp_date_str] = {
                    'date': exp_date_str,
                    'total_contracts': len(contracts),
                    'calls': calls,
                    'puts': puts,
                    'contracts': contracts
                }
                
                company_options['total_contracts'] += len(contracts)
                total_contracts += len(contracts)
                
                print(f"      ✅ {calls} CALLS (bet stock goes UP)")
                print(f"      ✅ {puts} PUTS (bet stock goes DOWN)")
            
            all_options[company] = company_options
            print(f"   🎯 Total for {company}: {company_options['total_contracts']} contracts")
            
        except Exception as e:
            print(f"   ❌ Error with {company}: {e}")
    
    # Save our results
    result = {
        'step': 2,
        'what_we_did': 'Found all options contracts for each company',
        'timestamp': datetime.now().isoformat(),
        'companies_analyzed': len(all_options),
        'total_contracts_found': total_contracts,
        'options_by_company': all_options
    }
    
    filename = 'step2_options_contracts.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved options data to: {filename}")
    print(f"🎰 Found {total_contracts} total contracts to analyze!")
    return result

if __name__ == "__main__":
    get_options_contracts()
```

**Run:** `python3 options_chains.py`

---


## 📁 Get IV Data

### Data: Implied volatility (IV) value for every option contract we found.  
### Why: IV shows how much the market thinks the stock might swing. Bigger IV = juicier option prices and more risk.

**Create:** `touch iv_data.py`

**Query:**  `open -e iv_data.py`

```bash
# iv_data.py  — STEP 3: Grab Option-Level Implied Volatility Only
import asyncio, json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from config import USERNAME, PASSWORD

STEP2_FILE = "step2_options_contracts.json"
OUT_FILE   = "step3_iv_data.json"

async def get_iv():
    print("📈 STEP 3: Collecting IV data only")
    print("="*50)

    # 1️⃣ Load contracts discovered in Step 2
    with open(STEP2_FILE) as f:
        opt_data = json.load(f)
    symbols = [c["streamer_symbol"]
               for comp in opt_data["options_by_company"].values()
               for exp in comp["expiration_dates"].values()
               for c   in exp["contracts"]]
    print(f"🔍 Streaming IV for {len(symbols)} contracts…")

    session, iv_by_contract = Session(USERNAME, PASSWORD), {}

    async with DXLinkStreamer(session) as s:
        await s.subscribe(Greeks, symbols)
        start = asyncio.get_event_loop().time()

        # 90-second collection window
        while (asyncio.get_event_loop().time() - start) < 90:
            try:
                g = await asyncio.wait_for(s.get_event(Greeks), timeout=3)
                if g and g.event_symbol not in iv_by_contract:
                    iv_by_contract[g.event_symbol] = float(g.volatility)
                    if len(iv_by_contract) % 200 == 0:
                        print(f"   📥 IV points: {len(iv_by_contract)}")
            except asyncio.TimeoutError:
                continue

    # 2️⃣ Save to JSON
    out = {
        "step": 3,
        "what_we_did": "Collected implied volatility only",
        "timestamp": datetime.now().isoformat(),
        "contracts_with_iv": len(iv_by_contract),
        "iv_by_contract": iv_by_contract
    }
    with open(OUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n✅ Saved IV data → {OUT_FILE}")

if __name__ == "__main__":
    asyncio.run(get_iv())
```

**Run:** `python3 iv_data.py`

---

## 📁 Get Buy/Sell Prices (Bid/Ask)

### Data: bid, ask, midpoint, size, and spread for every option contract.  
### Why useful: reveals real trading price and liquidity.

**Create:** `touch market_prices.py`

**Query:** `open -e market_prices.py`

```bash
import asyncio
import json
from datetime import datetime
from decimal import Decimal
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def safe_float_convert(value):
    """Safely convert any numeric value to float"""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

async def get_market_prices():
    print("💰 STEP 4: Getting Market Prices")
    print("=" * 50)
    print("🏪 Finding out what people will actually pay vs. sell for...")
    
    # Load our contracts from Step 2
    with open('step2_options_contracts.json', 'r') as f:
        step2_data = json.load(f)
    
    # Collect all contract symbols
    all_contracts = []
    for company_data in step2_data['options_by_company'].values():
        for exp_data in company_data['expiration_dates'].values():
            for contract in exp_data['contracts']:
                all_contracts.append(contract['streamer_symbol'])
    
    print(f"🎯 Getting prices for {len(all_contracts)} contracts...")
    
    session = Session(USERNAME, PASSWORD)
    market_prices = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to get market prices...")
        await streamer.subscribe(Quote, all_contracts)
        print("✅ Connected! Getting buy/sell prices...")
        
        collected_quotes = []
        start_time = asyncio.get_event_loop().time()
        
        # Collect for 2 minutes
        while (asyncio.get_event_loop().time() - start_time) < 120:
            try:
                quote = await asyncio.wait_for(streamer.get_event(Quote), timeout=3.0)
                
                if quote:
                    collected_quotes.append(quote)
                    
                    # Show progress every 100 quotes
                    if len(collected_quotes) % 100 == 0:
                        print(f"   💰 Prices collected: {len(collected_quotes)}")
                        
            except asyncio.TimeoutError:
                continue
        
        print(f"✅ Collected {len(collected_quotes)} market prices!")
        
        # Process quotes with proper decimal handling
        for quote in collected_quotes:
            # Safely convert all numeric values to float
            buy_price = safe_float_convert(quote.bid_price)
            sell_price = safe_float_convert(quote.ask_price)
            bid_size = safe_float_convert(getattr(quote, 'bid_size', 0))
            ask_size = safe_float_convert(getattr(quote, 'ask_size', 0))
            
            if buy_price > 0 and sell_price > 0:
                market_prices[quote.event_symbol] = {
                    'contract_name': quote.event_symbol,
                    'what_buyers_pay': buy_price,      # Bid price
                    'what_sellers_want': sell_price,   # Ask price
                    'fair_price': (buy_price + sell_price) / 2,  # Middle price
                    'price_difference': sell_price - buy_price,  # Spread
                    'buyers_willing': bid_size,
                    'sellers_available': ask_size
                }
    
    # Organize by company
    companies = ['NVDA', 'TSLA', 'AMZN', 'ISRG', 'PLTR', 'ENPH', 'XOM', 'DE', 'CAT']
    prices_by_company = {}
    
    for company in companies:
        prices_by_company[company] = []
        
    for symbol, price_data in market_prices.items():
        for company in companies:
            if company in symbol:
                prices_by_company[company].append(price_data)
                break
    
    # Save our results with decimal handling
    result = {
        'step': 4,
        'what_we_did': 'Got buy/sell prices for all options',
        'timestamp': datetime.now().isoformat(),
        'total_prices_collected': len(market_prices),
        'companies_with_prices': len([c for c in prices_by_company.values() if c]),
        'prices_by_company': prices_by_company,
        'price_explanations': {
            'what_buyers_pay': 'The highest price someone will pay (BID)',
            'what_sellers_want': 'The lowest price someone will sell for (ASK)',
            'fair_price': 'The middle price between buy and sell',
            'price_difference': 'The gap between buy and sell prices (SPREAD)'
        }
    }
    
    filename = 'step4_market_prices.json'
    
    # Use custom JSON encoder to handle any remaining Decimal objects
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super(DecimalEncoder, self).default(obj)
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2, cls=DecimalEncoder)
    
    print(f"\n✅ Saved market prices to: {filename}")
    print(f"💰 Got prices for {len(market_prices)} contracts!")
    
    # Show some examples
    print(f"\n💰 PRICE EXAMPLES:")
    sample_prices = list(market_prices.items())[:5]
    for symbol, price_data in sample_prices:
        buy = price_data['what_buyers_pay']
        sell = price_data['what_sellers_want']
        diff = price_data['price_difference']
        print(f"   {symbol[-10:]:10}: Buy=${buy:.2f}, Sell=${sell:.2f}, Gap=${diff:.3f}")
    
    return result

if __name__ == "__main__":
    asyncio.run(get_market_prices())
```

**Run:** `python3 market_prices.py`

---

## 📁 Get the Greeks Data 

### Data: Delta, theta, gamma, vega, IV, and current option price for every contract.  
### Why useful: Greeks show how price, time, and volatility will hit your P/L.

**Create:** `touch risk_analysis.py`

**Query:** `open -e risk_analysis.py`

```bash
import asyncio
import json
from datetime import datetime
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from config import USERNAME, PASSWORD

async def analyze_risk():
    print("🧮 STEP 3: Risk Analysis (Greeks)")
    print("=" * 50)
    print("🔬 Using special math to check how risky each bet is...")
    
    # Load our options from Step 2
    with open('step2_options_contracts.json', 'r') as f:
        step2_data = json.load(f)
    
    # Collect all contract symbols we need to analyze
    all_contracts = []
    for company_data in step2_data['options_by_company'].values():
        for exp_data in company_data['expiration_dates'].values():
            for contract in exp_data['contracts']:
                all_contracts.append(contract['streamer_symbol'])
    
    print(f"🎯 Analyzing risk for {len(all_contracts)} contracts...")
    
    session = Session(USERNAME, PASSWORD)
    risk_data = {}
    
    async with DXLinkStreamer(session) as streamer:
        print("📡 Connecting to get risk calculations...")
        await streamer.subscribe(Greeks, all_contracts)
        print("✅ Connected! Getting risk data...")
        
        collected_greeks = []
        start_time = asyncio.get_event_loop().time()
        
        # Collect for 2 minutes to get all data
        while (asyncio.get_event_loop().time() - start_time) < 120:
            try:
                greek_data = await asyncio.wait_for(streamer.get_event(Greeks), timeout=3.0)
                
                if greek_data:
                    collected_greeks.append(greek_data)
                    
                    # Show progress every 100 items
                    if len(collected_greeks) % 100 == 0:
                        print(f"   📊 Risk calculations done: {len(collected_greeks)}")
                        
            except asyncio.TimeoutError:
                continue
        
        print(f"✅ Completed {len(collected_greeks)} risk calculations!")
        
        # Organize risk data by company
        companies = ['NVDA', 'TSLA', 'AMZN', 'ISRG', 'PLTR', 'ENPH', 'XOM', 'DE', 'CAT']
        
        for greek in collected_greeks:
            # Figure out which company this belongs to
            company = None
            for comp in companies:
                if comp in greek.event_symbol:
                    company = comp
                    break
            
            if company:
                if company not in risk_data:
                    risk_data[company] = []
                
                # Save the risk information in simple terms
                risk_info = {
                    'contract_name': greek.event_symbol,
                    'current_option_price': float(greek.price),
                    'delta': float(greek.delta),  # How much price changes when stock moves $1
                    'theta': float(greek.theta),  # How much we lose each day (time decay)
                    'gamma': float(greek.gamma),  # How much delta changes
                    'vega': float(greek.vega),   # How much price changes with volatility
                    'implied_volatility': float(greek.volatility)  # How "jumpy" people think stock will be
                }
                
                risk_data[company].append(risk_info)
    
    # Save our results
    result = {
        'step': 3,
        'what_we_did': 'Calculated risk for all options using Greeks',
        'timestamp': datetime.now().isoformat(),
        'total_risk_calculations': len(collected_greeks),
        'companies_analyzed': len(risk_data),
        'risk_by_company': risk_data,
        'greek_explanations': {
            'delta': 'How much option price changes when stock moves $1',
            'theta': 'How much money we lose each day (time decay)',
            'gamma': 'How much delta speeds up or slows down',
            'vega': 'How much price changes if volatility changes',
            'implied_volatility': 'How jumpy people think the stock will be'
        }
    }
    
    filename = 'step3_risk_analysis.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved risk analysis to: {filename}")
    print(f"🧮 Calculated risk for {len(collected_greeks)} contracts!")
    
    # Show some examples
    print(f"\n📊 RISK EXAMPLES:")
    for company, risks in list(risk_data.items())[:3]:
        if risks:
            example = risks[0]
            print(f"   {company}: Delta={example['delta']:.3f}, Theta={example['theta']:.3f}")
    
    return result

if __name__ == "__main__":
    asyncio.run(analyze_risk())
```

**Run:** `python3 risk_analysis.py`


---

# ✒️ IV and Liquidity Analysis 


## 📁 Find High IV and Liquidity

### Data: each option’s open interest, trading volume, bid-ask spread, and existing IV.  
### Why useful: These numbers show how busy the contract is and how cheap it is to trade.

**Create:** `touch iv_liquidity.py`

**Query:** `touch iv_liquidity.py`

```bash
# advanced_iv_liquidity.py - STEP 6: Fixed version with better data collection
import json
import numpy as np
from datetime import datetime
import asyncio
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Summary
from config import USERNAME, PASSWORD

async def analyze_iv_and_liquidity():
    print("📊 STEP 6: Advanced IV & Liquidity Analysis")
    print("=" * 70)
    print("🎯 Collecting comprehensive market data...")
    
    # Load previous data
    with open('step1_stock_prices.json', 'r') as f:
        stock_data = json.load(f)
    
    with open('step2_options_contracts.json', 'r') as f:
        options_data = json.load(f)
    
    with open('step3_iv_data.json', 'r') as f:
        iv_data = json.load(f)
    
    with open('step4_market_prices.json', 'r') as f:
        price_data = json.load(f)
    
    print(f"✅ Loaded data: {options_data['total_contracts_found']} contracts to analyze")
    
    session = Session(USERNAME, PASSWORD)
    
    # Create lookups
    price_lookup = {}
    for company, prices_list in price_data['prices_by_company'].items():
        for price in prices_list:
            price_lookup[price['contract_name']] = price
    
    companies = list(stock_data['stock_prices'].keys())
    enhanced_options = {}
    
    # Collect ALL contract symbols
    all_symbols = []
    symbol_to_company = {}
    
    for company, company_data in options_data['options_by_company'].items():
        for exp_data in company_data['expiration_dates'].values():
            for contract in exp_data['contracts']:
                symbol = contract['streamer_symbol']
                all_symbols.append(symbol)
                symbol_to_company[symbol] = company
    
    print(f"📡 Need to get Summary data for {len(all_symbols)} contracts...")
    
    # Process in batches to avoid overwhelming the connection
    batch_size = 500
    summary_data = {}
    
    async with DXLinkStreamer(session) as streamer:
        for batch_start in range(0, len(all_symbols), batch_size):
            batch_end = min(batch_start + batch_size, len(all_symbols))
            batch_symbols = all_symbols[batch_start:batch_end]
            
            print(f"\n   📊 Processing batch {batch_start//batch_size + 1}/{(len(all_symbols) + batch_size - 1)//batch_size}")
            print(f"      Symbols {batch_start + 1} to {batch_end} of {len(all_symbols)}")
            
            # Subscribe to this batch
            await streamer.subscribe(Summary, batch_symbols)
            
            # Collect data for this batch
            batch_collected = 0
            start_time = asyncio.get_event_loop().time()
            no_data_timeout = 0
            
            # Collect for up to 30 seconds per batch or until we stop getting new data
            while (asyncio.get_event_loop().time() - start_time) < 30 and no_data_timeout < 5:
                try:
                    summary = await asyncio.wait_for(streamer.get_event(Summary), timeout=1.0)
                    if summary and summary.event_symbol in batch_symbols:
                        summary_data[summary.event_symbol] = {
                            'open_interest': int(summary.open_interest) if summary.open_interest else 0,
                            'volume': int(summary.prev_day_volume) if summary.prev_day_volume else 0,
                            'day_high': float(summary.day_high_price) if summary.day_high_price else 0,
                            'day_low': float(summary.day_low_price) if summary.day_low_price else 0
                        }
                        batch_collected += 1
                        no_data_timeout = 0  # Reset timeout counter
                        
                        if batch_collected % 50 == 0:
                            print(f"      Collected: {batch_collected} summaries")
                        
                except asyncio.TimeoutError:
                    no_data_timeout += 1
                    continue
                except Exception as e:
                    continue
            
            print(f"      ✅ Batch complete: {batch_collected} summaries collected")
            
            # Unsubscribe from this batch before moving to next
            await streamer.unsubscribe(Summary, batch_symbols)
            
            # Small delay between batches
            await asyncio.sleep(0.5)
    
    print(f"\n✅ Total Summary data collected: {len(summary_data)} contracts")
    
    # Now analyze each company with all the data
    for company in companies:
        print(f"\n🏢 Analyzing {company}...")
        
        company_options = options_data['options_by_company'].get(company, {})
        if not company_options:
            continue
        
        current_price = company_options['current_stock_price']
        company_contracts = []
        
        # Stats tracking
        stats = {
            'total_analyzed': 0,
            'has_iv': 0,
            'has_price': 0,
            'has_summary': 0,
            'has_all_data': 0
        }
        
        for exp_data in company_options['expiration_dates'].values():
            for contract in exp_data['contracts']:
                symbol = contract['streamer_symbol']
                stats['total_analyzed'] += 1
                
                # Check data availability
                has_iv = symbol in iv_data['iv_by_contract']
                has_price = symbol in price_lookup
                has_summary = symbol in summary_data
                
                if has_iv:
                    stats['has_iv'] += 1
                if has_price:
                    stats['has_price'] += 1
                if has_summary:
                    stats['has_summary'] += 1
                
                # Only analyze if we have at least IV and price data
                if not (has_iv and has_price):
                    continue
                
                stats['has_all_data'] += 1
                
                # Get all data
                current_iv = iv_data['iv_by_contract'][symbol]
                price_info = price_lookup[symbol]
                
                # Get summary data or use defaults
                if has_summary:
                    liquidity = summary_data[symbol]
                else:
                    liquidity = {'open_interest': 0, 'volume': 0}
                
                # Calculate metrics
                bid = price_info['what_buyers_pay']
                ask = price_info['what_sellers_want']
                spread = ask - bid
                
                # Calculate liquidity score
                liquidity_score = calculate_liquidity_score(
                    liquidity['open_interest'],
                    liquidity['volume'],
                    spread,
                    company
                )
                
                contract_analysis = {
                    'symbol': symbol,
                    'strike': contract['strike_price'],
                    'type': contract['contract_type'],
                    'days_to_exp': contract['days_until_expires'],
                    'current_iv': current_iv,
                    'open_interest': liquidity['open_interest'],
                    'volume': liquidity['volume'],
                    'bid': bid,
                    'ask': ask,
                    'bid_ask_spread': spread,
                    'liquidity_score': liquidity_score,
                    'liquid': liquidity_score >= 70,
                    'has_summary_data': has_summary
                }
                
                company_contracts.append(contract_analysis)
        
        # Calculate company metrics
        if company_contracts:
            liquid_contracts = [c for c in company_contracts if c['liquid']]
            high_volume = [c for c in company_contracts if c['volume'] >= 100]
            high_oi = [c for c in company_contracts if c['open_interest'] >= 1000]
            tight_spreads = [c for c in company_contracts if c['bid_ask_spread'] <= 0.10]
            
            avg_iv = np.mean([c['current_iv'] for c in company_contracts])
            
            enhanced_options[company] = {
                'current_stock_price': current_price,
                'avg_implied_volatility': avg_iv,
                'data_coverage': stats,
                'metrics': {
                    'total_contracts_analyzed': len(company_contracts),
                    'liquid_contracts': len(liquid_contracts),
                    'high_volume_contracts': len(high_volume),
                    'high_oi_contracts': len(high_oi),
                    'tight_spread_contracts': len(tight_spreads),
                    'contracts_with_summary': sum(1 for c in company_contracts if c['has_summary_data'])
                },
                'top_liquid_contracts': sorted(
                    company_contracts, 
                    key=lambda x: (x['liquidity_score'], x['open_interest']), 
                    reverse=True
                )[:20]
            }
            
            print(f"   📊 Avg IV: {avg_iv:.3f}")
            print(f"   📈 Contracts analyzed: {len(company_contracts)}")
            print(f"   💧 Liquid contracts: {len(liquid_contracts)}")
            print(f"   📊 High OI (≥1000): {len(high_oi)}")
            print(f"   📊 Summary data coverage: {stats['has_summary']}/{stats['total_analyzed']} ({stats['has_summary']/stats['total_analyzed']*100:.1f}%)")
    
    # Find best opportunities
    all_liquid_contracts = []
    for company, data in enhanced_options.items():
        for contract in data['top_liquid_contracts']:
            if contract['liquid']:
                contract['company'] = company
                all_liquid_contracts.append(contract)
    
    # Sort by liquidity score
    all_liquid_contracts.sort(key=lambda x: (x['liquidity_score'], x['open_interest']), reverse=True)
    
    # Save results
    result = {
        'step': 6,
        'what_we_did': 'Comprehensive IV & Liquidity Analysis',
        'timestamp': datetime.now().isoformat(),
        'data_summary': {
            'total_contracts': options_data['total_contracts_found'],
            'contracts_with_iv': len(iv_data['iv_by_contract']),
            'contracts_with_prices': price_data['total_prices_collected'],
            'contracts_with_summary': len(summary_data)
        },
        'companies_analyzed': len(enhanced_options),
        'enhanced_options': enhanced_options,
        'top_liquid_contracts': all_liquid_contracts[:50],
        'liquidity_criteria': {
            'score_threshold': 70,
            'oi_threshold': 1000,
            'volume_threshold': 100,
            'spread_thresholds': {
                'top_names': 0.05,
                'others': 0.10
            }
        }
    }
    
    filename = 'step6_advanced_iv_liquidity.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Summary data coverage: {len(summary_data)}/{len(all_symbols)} contracts ({len(summary_data)/len(all_symbols)*100:.1f}%)")
    print(f"💧 Total liquid contracts found: {len(all_liquid_contracts)}")
    print(f"📁 Results saved to: {filename}")
    
    return result

def calculate_liquidity_score(open_interest, volume, spread, company):
    """Calculate 0-100 liquidity score"""
    score = 0
    
    # Open interest component (40 points)
    if open_interest >= 1000:
        score += 40
    elif open_interest >= 500:
        score += 30
    elif open_interest >= 100:
        score += 20
    elif open_interest > 0:
        score += min(20, (open_interest / 100) * 20)
    
    # Volume component (30 points)
    if volume >= 1000:
        score += 30
    elif volume >= 500:
        score += 20
    elif volume >= 100:
        score += 10
    elif volume > 0:
        score += min(10, (volume / 100) * 10)
    
    # Spread component (30 points)
    if spread >= 0:
        if company in ['NVDA', 'TSLA', 'AMZN']:
            if spread <= 0.05:
                score += 30
            elif spread <= 0.10:
                score += 20
            elif spread <= 0.20:
                score += 10
        else:
            if spread <= 0.10:
                score += 30
            elif spread <= 0.20:
                score += 20
            elif spread <= 0.50:
                score += 10
    
    return min(100, score)

if __name__ == "__main__":
    asyncio.run(analyze_iv_and_liquidity())
```
**Run:** `python3 iv_liquidity.py`

# ✒️ Black Scholes Analysis


## 📁 Find the Best Deals

### Data: liquid call + put pairs with bid/ask, IV, open interest, strike width, days to expire.  
### Why useful: calculates credit, max loss, ROI, and probability to profit.

**Create:** `touch find_tendies.py`

**Query:** `open -e find_tendies.py`

```bash
# enhanced_find_tendies.py - STEP 7: Both Call and Put Credit Spreads
import json
import numpy as np
from datetime import datetime
from scipy.stats import norm

class EliteCreditSpreadScanner:
    """Advanced credit spread scanner for BOTH calls and puts"""
    
    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate
    
    def black_scholes_probability(self, S, K, T, sigma, option_type='call'):
        """Calculate probability of staying OTM for calls or puts"""
        if T <= 0 or sigma <= 0:
            return 0
        
        d2 = (np.log(S / K) + (self.risk_free_rate - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        if option_type == 'call':
            # Probability call stays OTM (stock stays below K)
            return norm.cdf(-d2) * 100
        else:
            # Probability put stays OTM (stock stays above K)  
            return norm.cdf(d2) * 100
    
    def scan_call_spreads(self, liquid_contracts, current_price, company, price_lookup, avg_iv):
        """Scan for bear call credit spreads (calls above current price)"""
        call_spreads = []
        
        # Get calls above current price
        calls_above = []
        for contract in liquid_contracts:
            if (contract['type'] == 'CALL' and 
                contract['strike'] > current_price and
                contract['liquid'] and
                contract['symbol'] in price_lookup):
                calls_above.append(contract)
        
        calls_above.sort(key=lambda x: x['strike'])
        
        # Create call spreads
        for i in range(len(calls_above) - 1):
            short_call = calls_above[i]
            long_call = calls_above[i + 1]
            
            spread = self.analyze_credit_spread(
                short_call, long_call, current_price, company, 
                price_lookup, avg_iv, 'BEAR_CALL'
            )
            if spread:
                call_spreads.append(spread)
        
        return call_spreads
    
    def scan_put_spreads(self, liquid_contracts, current_price, company, price_lookup, avg_iv):
        """Scan for bull put credit spreads (puts below current price)"""
        put_spreads = []
        
        # Get puts below current price
        puts_below = []
        for contract in liquid_contracts:
            if (contract['type'] == 'PUT' and 
                contract['strike'] < current_price and
                contract['liquid'] and
                contract['symbol'] in price_lookup):
                puts_below.append(contract)
        
        puts_below.sort(key=lambda x: x['strike'], reverse=True)  # Highest to lowest
        
        # Create put spreads
        for i in range(len(puts_below) - 1):
            short_put = puts_below[i]      # Higher strike (short)
            long_put = puts_below[i + 1]   # Lower strike (long)
            
            spread = self.analyze_credit_spread(
                short_put, long_put, current_price, company, 
                price_lookup, avg_iv, 'BULL_PUT'
            )
            if spread:
                put_spreads.append(spread)
        
        return put_spreads
    
    def analyze_credit_spread(self, short_option, long_option, current_price, 
                            company, price_lookup, avg_iv, spread_type):
        """Analyze a credit spread (works for both calls and puts)"""
        
        strike_width = abs(long_option['strike'] - short_option['strike'])
        if strike_width > 10:
            return None
        
        short_symbol = short_option['symbol']
        long_symbol = long_option['symbol']
        
        # Get price data
        short_price = price_lookup[short_symbol]
        long_price = price_lookup[long_symbol]
        
        # Calculate credit (what we collect)
        credit = short_price['what_buyers_pay'] - long_price['what_sellers_want']
        if credit <= 0:
            return None
        
        max_risk = strike_width - credit
        roi = (credit / max_risk * 100) if max_risk > 0 else 0
        
        # Skip low ROI
        if roi < 10:
            return None
        
        # Get IV for probability calculation
        short_iv = short_option.get('current_iv', avg_iv)
        time_to_exp = short_option['days_to_exp'] / 365
        
        # Calculate probability based on spread type
        if spread_type == 'BEAR_CALL':
            # For bear call: want stock to stay BELOW short strike
            prob_profit = self.black_scholes_probability(
                current_price, short_option['strike'], time_to_exp, short_iv, 'call'
            )
            distance_from_money = ((short_option['strike'] - current_price) / current_price) * 100
        else:  # BULL_PUT
            # For bull put: want stock to stay ABOVE short strike  
            prob_profit = self.black_scholes_probability(
                current_price, short_option['strike'], time_to_exp, short_iv, 'put'
            )
            distance_from_money = ((current_price - short_option['strike']) / current_price) * 100
        
        # Skip low probability
        if prob_profit < 65:
            return None
        
        # Check minimum liquidity
        min_oi = min(short_option['open_interest'], long_option['open_interest'])
        if min_oi < 500:
            return None
        
        return {
            'company': company,
            'spread_type': spread_type,
            'short_strike': short_option['strike'],
            'long_strike': long_option['strike'],
            'strike_width': strike_width,
            'days_to_expiration': short_option['days_to_exp'],
            'credit': credit,
            'max_risk': max_risk,
            'roi_percent': roi,
            'probability_of_profit': prob_profit,
            'current_stock_price': current_price,
            'distance_from_money': distance_from_money,
            'short_iv': short_iv,
            'min_open_interest': min_oi,
            'short_symbol': short_symbol,
            'long_symbol': long_symbol,
            'strategy_explanation': self.get_strategy_explanation(spread_type, short_option['strike'], long_option['strike'])
        }
    
    def get_strategy_explanation(self, spread_type, short_strike, long_strike):
        """Explain the strategy"""
        if spread_type == 'BEAR_CALL':
            return f"Sell ${short_strike} call, buy ${long_strike} call. Profit if stock stays below ${short_strike}"
        else:
            return f"Sell ${short_strike} put, buy ${long_strike} put. Profit if stock stays above ${short_strike}"

def scan_all_credit_spreads():
    print("🏆 STEP 7: Complete Credit Spread Scanner")
    print("=" * 70)
    print("🎯 Scanning BOTH Call and Put Credit Spreads...")
    print("📈 Bear Call Spreads: Profit when stock doesn't go UP")
    print("📉 Bull Put Spreads: Profit when stock doesn't go DOWN")
    
    # Load all data
    with open('step1_stock_prices.json', 'r') as f:
        stock_data = json.load(f)
    
    with open('step2_options_contracts.json', 'r') as f:
        options_data = json.load(f)
    
    with open('step3_iv_data.json', 'r') as f:
        iv_data = json.load(f)
    
    with open('step4_market_prices.json', 'r') as f:
        price_data = json.load(f)
    
    with open('step6_advanced_iv_liquidity.json', 'r') as f:
        iv_liquidity_data = json.load(f)
    
    scanner = EliteCreditSpreadScanner()
    
    # Create price lookup
    price_lookup = {}
    for company, prices_list in price_data['prices_by_company'].items():
        for price in prices_list:
            price_lookup[price['contract_name']] = price
    
    all_spreads = []
    call_spreads_total = 0
    put_spreads_total = 0
    
    # Scan each company
    for company, company_options in options_data['options_by_company'].items():
        current_price = company_options['current_stock_price']
        company_iv_data = iv_liquidity_data['enhanced_options'].get(company, {})
        avg_iv = company_iv_data.get('avg_implied_volatility', 0.3)
        
        print(f"\n🏢 Scanning {company} (Price: ${current_price:.2f}, Avg IV: {avg_iv:.3f})...")
        
        # Skip if IV too low
        if avg_iv < 0.25:
            print(f"   ⚠️ IV too low ({avg_iv:.3f}), skipping...")
            continue
        
        liquid_contracts = company_iv_data.get('top_liquid_contracts', [])
        
        # Scan call credit spreads (bear call spreads)
        call_spreads = scanner.scan_call_spreads(
            liquid_contracts, current_price, company, price_lookup, avg_iv
        )
        call_spreads_total += len(call_spreads)
        
        # Scan put credit spreads (bull put spreads)  
        put_spreads = scanner.scan_put_spreads(
            liquid_contracts, current_price, company, price_lookup, avg_iv
        )
        put_spreads_total += len(put_spreads)
        
        all_spreads.extend(call_spreads)
        all_spreads.extend(put_spreads)
        
        print(f"   📈 Bear Call Spreads: {len(call_spreads)}")
        print(f"   📉 Bull Put Spreads: {len(put_spreads)}")
        print(f"   🎯 Total for {company}: {len(call_spreads) + len(put_spreads)}")
    
    # Sort by ROI * Probability score
    for spread in all_spreads:
        spread['combined_score'] = spread['roi_percent'] * (spread['probability_of_profit'] / 100)
    
    all_spreads.sort(key=lambda x: x['combined_score'], reverse=True)
    
    print(f"\n💎 TOTAL CREDIT SPREADS FOUND: {len(all_spreads)}")
    print(f"📈 Bear Call Spreads: {call_spreads_total}")
    print(f"📉 Bull Put Spreads: {put_spreads_total}")
    print("=" * 70)
    
    # Show top 15 - mixed calls and puts
    print(f"\n🏆 TOP 15 CREDIT SPREADS (Both Types):")
    print("-" * 120)
    
    for i, spread in enumerate(all_spreads[:15]):
        spread_icon = "📈" if spread['spread_type'] == 'BEAR_CALL' else "📉"
        spread_name = "Bear Call" if spread['spread_type'] == 'BEAR_CALL' else "Bull Put"
        
        print(f"{i+1:2}. {spread_icon} {spread['company']:4} {spread_name:9} | "
              f"${spread['short_strike']:.0f}/{spread['long_strike']:.0f} | "
              f"Score: {spread['combined_score']:.1f} | "
              f"PoP: {spread['probability_of_profit']:.1f}% | "
              f"ROI: {spread['roi_percent']:.1f}% | "
              f"Credit: ${spread['credit']:.2f} | "
              f"DTE: {spread['days_to_expiration']}")
        print(f"     📝 {spread['strategy_explanation']}")
    
    # Save results
    result = {
        'step': 7,
        'what_we_did': 'Complete Credit Spread Analysis - Both Calls and Puts',
        'timestamp': datetime.now().isoformat(),
        'total_spreads_found': len(all_spreads),
        'bear_call_spreads': call_spreads_total,
        'bull_put_spreads': put_spreads_total,
        'all_spreads': all_spreads[:100],  # Top 100
        'summary_stats': {
            'avg_roi': np.mean([s['roi_percent'] for s in all_spreads]) if all_spreads else 0,
            'avg_probability': np.mean([s['probability_of_profit'] for s in all_spreads]) if all_spreads else 0,
            'avg_combined_score': np.mean([s['combined_score'] for s in all_spreads]) if all_spreads else 0
        }
    }
    
    filename = 'step7_complete_credit_spreads.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Saved complete analysis to: {filename}")
    
    # Show strategy breakdown
    if all_spreads:
        best_call = next((s for s in all_spreads if s['spread_type'] == 'BEAR_CALL'), None)
        best_put = next((s for s in all_spreads if s['spread_type'] == 'BULL_PUT'), None)
        
        print(f"\n💎 STRATEGY COMPARISON:")
        if best_call:
            print(f"   📈 Best Bear Call: {best_call['company']} ${best_call['short_strike']:.0f}/{best_call['long_strike']:.0f}")
            print(f"      ROI: {best_call['roi_percent']:.1f}%, PoP: {best_call['probability_of_profit']:.1f}%")
        
        if best_put:
            print(f"   📉 Best Bull Put: {best_put['company']} ${best_put['short_strike']:.0f}/{best_put['long_strike']:.0f}")
            print(f"      ROI: {best_put['roi_percent']:.1f}%, PoP: {best_put['probability_of_profit']:.1f}%")
    
    return result

if __name__ == "__main__":
    scan_all_credit_spreads()
```

**Run:** `python3 find_tendies.py`

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


# ✒️ Prompt

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

