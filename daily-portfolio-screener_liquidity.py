**Create:** `touch liquidity.py`
**Query:** `open -e liquidity.py`

```bash
# liquidity.py - Dual Basket System (GPT + Grok) 
"""
Enhanced liquidity scanner that creates TWO trading baskets:
- GPT Basket: Best ticker from each sector in GPT universe
- Grok Basket: Best ticker from each sector in Grok universe

Output: 9 tickers per basket (1 per sector) = 18 total trading candidates
"""
import asyncio, json, statistics, argparse, signal, sys
from datetime import datetime, timezone
from collections import defaultdict, deque
from pathlib import Path

from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote, Summary, Greeks
from tastytrade.instruments import get_option_chain
from tastytrade.utils import TastytradeError
from config import USERNAME, PASSWORD

# Import sectors to get the universe definitions
try:
    from sectors import get_sectors
except ImportError:
    print("❌ Error: Cannot import sectors.py")
    print("Make sure sectors.py exists with get_sectors() function")
    sys.exit(1)

# ---------------- Configuration ----------------
DEFAULT_SAMPLE_SEC = 20.0
DEFAULT_CONCURRENCY = 1

# Reference thresholds for scoring
REF_INSIDE_RATIO = 0.70
REF_NBBO_AGE_MS = 1500
REF_TPM = 25
REF_SPREAD_ABS = 0.05
REF_OI_MIN = 1000

# Tier thresholds
T1_ABS, T1_REL, T1_OI = 0.10, 0.20, 10000
T2_ABS, T2_REL, T2_OI = 0.20, 0.40, 500

# Universe settings
MAX_OPT_SYMBOLS_PER_SIDE = 50
MONEYNESS_WIDTH = 0.50
HEARTBEAT_SEC = 2.0

# Global shutdown flag
shutdown_requested = False

def signal_handler(signum, frame):
    global shutdown_requested
    print(f"\n⚠️  Shutdown requested...")
    shutdown_requested = True

signal.signal(signal.SIGINT, signal_handler)

def med(a): return statistics.median(a) if a else 0.0
def now_iso(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def classify_tier(spread_med, mid_med, oi_avg):
    """Classify liquidity tier."""
    if spread_med<=T1_ABS and mid_med>0 and (spread_med/mid_med)<=T1_REL and oi_avg>=T1_OI: return "T1"
    if spread_med<=T2_ABS and mid_med>0 and (spread_med/mid_med)<=T2_REL and oi_avg>=T2_OI: return "T2"
    return "T3"

def calculate_liquidity_score(metrics, ivr=0):
    """Calculate composite liquidity score (0-100)."""
    spread_med = metrics.get("spread_med_Δ30", 999)
    inside_ratio = metrics.get("inside_threshold_ratio_Δ30", 0)
    ticks_pm = metrics.get("ticks_per_min", 0)
    nbbo_age_ms = metrics.get("nbbo_age_ms_med", 99999)
    oi_min = metrics.get("oi_min_Δ30", 0)
    
    # Component scores (0-100 each)
    spread_score = max(0, min(100, 100 * (1 - spread_med / max(REF_SPREAD_ABS * 10, 0.01))))
    inside_score = min(100, 100 * inside_ratio / REF_INSIDE_RATIO)
    tick_score = min(100, 100 * ticks_pm / REF_TPM)
    freshness_score = max(0, min(100, 100 * (1 - nbbo_age_ms / (REF_NBBO_AGE_MS * 10))))
    oi_score = min(100, 100 * oi_min / REF_OI_MIN)
    ivr_score = min(100, ivr)
    
    # Weighted composite
    composite_score = (
        spread_score * 0.25 +
        inside_score * 0.20 +
        tick_score * 0.20 +
        freshness_score * 0.15 +
        oi_score * 0.15 +
        ivr_score * 0.05
    )
    
    return {
        "composite_score": round(composite_score, 1),
        "component_scores": {
            "spread": round(spread_score, 1),
            "inside_ratio": round(inside_score, 1),
            "tick_flow": round(tick_score, 1),
            "freshness": round(freshness_score, 1),
            "open_interest": round(oi_score, 1),
            "iv_rank": round(ivr_score, 1)
        }
    }

def get_quality_rating(score):
    """Convert score to quality rating."""
    if score >= 80: return "🟢 EXCELLENT"
    elif score >= 65: return "🟡 GOOD"
    elif score >= 45: return "🟠 FAIR"
    elif score >= 25: return "🔴 POOR"
    else: return "⚫ TERRIBLE"

def choose_subset(opts, spot):
    """Choose options near the money."""
    calls, puts = [], []
    lo, hi = spot*(1.0 - MONEYNESS_WIDTH), spot*(1.0 + MONEYNESS_WIDTH)
    
    for o in opts:
        k = float(o.strike_price)
        if lo <= k <= hi:
            (calls if o.option_type.value == "C" else puts).append(o)
    
    calls.sort(key=lambda x: abs(float(x.strike_price) - spot))
    puts.sort(key=lambda x: abs(float(x.strike_price) - spot))
    
    return calls[:MAX_OPT_SYMBOLS_PER_SIDE] + puts[:MAX_OPT_SYMBOLS_PER_SIDE]

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

def stats_for_leg(sym, quotes_deque, sample_sec):
    pts = list(quotes_deque.get(sym, []))
    if not pts: return None
    spreads = [a-b for (b,a) in pts if a>=b>0]
    mids = [(a+b)/2 for (b,a) in pts if a>=b>0]
    if not spreads or not mids: return None
    spread_med, mid_med = med(spreads), med(mids)
    allowed_tmp = min(T2_ABS, T2_REL*max(mid_med,1e-9))
    inside_ratio = sum(1 for s in spreads if s<=allowed_tmp)/max(len(spreads),1)
    ticks_pm = 60*len(pts)/max(sample_sec,1)
    nbbo_age_ms = 1000*(sample_sec/max(len(pts),1))
    return dict(
        spread_med=spread_med, mid_med=mid_med, inside_ratio=inside_ratio,
        ticks_pm=ticks_pm, nbbo_age_ms=nbbo_age_ms, n_ticks=len(pts)
    )

def is_market_hours():
    """Check if markets are open."""
    now = datetime.now(timezone.utc)
    hour_utc = now.hour
    weekday = now.weekday()
    return weekday < 5 and 14 <= hour_utc <= 21

async def scan_one_ticker(sess, rec, sample_sec):
    """Scan one ticker and return metrics + score."""
    global shutdown_requested
    
    tkr = rec["ticker"]
    spot = rec["spot"]
    exp_iso = rec["target_expiry"]
    ivr = rec.get("ivr", 0)
    
    if shutdown_requested:
        return {"ticker": tkr, "status": "shutdown"}
    
    try:
        async with DXLinkStreamer(sess) as streamer:
            # Load chain
            try:
                chain = get_option_chain(sess, tkr)
            except Exception as e:
                return {"ticker": tkr, "status": f"chain_error", "error": str(e)}

            # Find expiry
            exp = None
            for d in chain.keys():
                if d.isoformat() == exp_iso:
                    exp = d
                    break
            
            if not exp:
                return {"ticker": tkr, "status": "no_expiry"}

            # Get options
            opts = choose_subset(chain[exp], spot)
            if not opts:
                return {"ticker": tkr, "status": "no_options"}

            symbols = [o.streamer_symbol for o in opts]
            meta = {o.streamer_symbol: {"strike": float(o.strike_price), "type": o.option_type.value} for o in opts}

            # Subscribe
            await streamer.subscribe(Quote, symbols)
            await asyncio.sleep(0.8)
            await streamer.subscribe(Greeks, symbols)
            await asyncio.sleep(0.8)
            await streamer.subscribe(Summary, symbols)
            await asyncio.sleep(0.8)

            # Collect data
            quotes = defaultdict(list)
            greeks = {}
            summary = {}
            
            start_time = asyncio.get_event_loop().time()
            
            while True:
                if shutdown_requested:
                    break
                    
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= sample_sec:
                    break

                timeout = 0.3
                
                # Quotes
                try:
                    q = await asyncio.wait_for(streamer.get_event(Quote), timeout=timeout)
                    if q and q.event_symbol in meta:
                        bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
                        if bid > 0 and ask > 0 and ask >= bid:
                            quotes[q.event_symbol].append((bid, ask))
                except asyncio.TimeoutError:
                    pass

                # Greeks
                try:
                    g = await asyncio.wait_for(streamer.get_event(Greeks), timeout=timeout)
                    if g and g.event_symbol in meta:
                        greeks[g.event_symbol] = {
                            "delta": float(g.delta or 0),
                            "iv": float(g.volatility or 0)
                        }
                except asyncio.TimeoutError:
                    pass

                # Summary
                try:
                    s = await asyncio.wait_for(streamer.get_event(Summary), timeout=timeout)
                    if s and s.event_symbol in meta:
                        summary[s.event_symbol] = {"oi": int(s.open_interest or 0)}
                except asyncio.TimeoutError:
                    pass

            # Cleanup
            try:
                await streamer.unsubscribe(Quote, symbols)
                await streamer.unsubscribe(Greeks, symbols)
                await streamer.unsubscribe(Summary, symbols)
            except:
                pass

            # Find delta-30
            call30 = nearest_delta(+1, 0.30, greeks, meta)
            put30 = nearest_delta(-1, 0.30, greeks, meta)

            if not call30 or not put30:
                return {"ticker": tkr, "status": "no_delta30"}

            # Calculate stats
            quotes_deque = {}
            for sym, quote_list in quotes.items():
                quotes_deque[sym] = deque(quote_list, maxlen=500)

            cs = stats_for_leg(call30, quotes_deque, elapsed)
            ps = stats_for_leg(put30, quotes_deque, elapsed)

            if not cs or not ps:
                return {"ticker": tkr, "status": "insufficient_quotes"}

            # Metrics
            spread_med_30 = max(cs["spread_med"], ps["spread_med"])
            mid_med_30 = med([cs["mid_med"], ps["mid_med"]])
            inside_ratio = (cs["inside_ratio"] + ps["inside_ratio"]) / 2
            ticks_pm = (cs["ticks_pm"] + ps["ticks_pm"]) / 2
            nbbo_age_ms = med([cs["nbbo_age_ms"], ps["nbbo_age_ms"]])
            oi_min = min(summary.get(call30, {}).get("oi", 0), summary.get(put30, {}).get("oi", 0))

            tier = classify_tier(spread_med_30, mid_med_30, (summary.get(call30, {}).get("oi", 0) + summary.get(put30, {}).get("oi", 0)) / 2)

            metrics = {
                "spread_med_Δ30": round(spread_med_30, 4),
                "mid_med_Δ30": round(mid_med_30, 4),
                "inside_threshold_ratio_Δ30": round(inside_ratio, 3),
                "ticks_per_min": round(ticks_pm, 2),
                "nbbo_age_ms_med": round(nbbo_age_ms, 0),
                "oi_min_Δ30": int(oi_min)
            }

            # Score
            score_breakdown = calculate_liquidity_score(metrics, ivr)
            composite_score = score_breakdown["composite_score"]

            return {
                "ticker": tkr,
                "status": "analyzed",
                "tier": tier,
                "liquidity_score": composite_score,
                "quality_rating": get_quality_rating(composite_score).split(" ", 1)[1],
                "score_breakdown": score_breakdown,
                "metrics": metrics
            }

    except Exception as e:
        return {"ticker": tkr, "status": "error", "error": str(e)}

def load_inputs_with_sectors():
    """Load data and organize by universe and sector."""
    try:
        with open("step3_atm_iv.json") as f:
            iv_data = json.load(f)
        
        # Filter for successful IV calculations
        valid_tickers = {r["ticker"]: r for r in iv_data if r.get("status") == "ok"}
        
        print(f"📋 Loaded {len(valid_tickers)} valid tickers from step3_atm_iv.json")
        
        # Get sector definitions for both universes
        gpt_sectors = get_sectors("gpt")
        grok_sectors = get_sectors("grok")
        
        # Organize tickers by universe and sector
        universes = {
            "gpt": {},
            "grok": {}
        }
        
        # GPT universe
        for sector_name, sector_data in gpt_sectors.items():
            universes["gpt"][sector_name] = []
            for ticker in sector_data["tickers"]:
                if ticker in valid_tickers:
                    ticker_data = valid_tickers[ticker].copy()
                    ticker_data["sector"] = sector_name
                    ticker_data["universe"] = "gpt"
                    universes["gpt"][sector_name].append(ticker_data)
        
        # Grok universe
        for sector_name, sector_data in grok_sectors.items():
            universes["grok"][sector_name] = []
            for ticker in sector_data["tickers"]:
                if ticker in valid_tickers:
                    ticker_data = valid_tickers[ticker].copy()
                    ticker_data["sector"] = sector_name
                    ticker_data["universe"] = "grok"
                    universes["grok"][sector_name].append(ticker_data)
        
        return universes
        
    except FileNotFoundError:
        print("❌ step3_atm_iv.json not found. Run atm_iv.py first.")
        return None
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

async def run_dual_basket_analysis(args):
    """Run analysis for both GPT and Grok universes."""
    global shutdown_requested
    
    print("🏆 DUAL BASKET LIQUIDITY SYSTEM")
    print("=" * 70)
    print("📊 Creating GPT and Grok trading baskets (1 ticker per sector)")
    
    # Market status
    market_open = is_market_hours()
    print(f"🕒 Market: {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
    
    # Load organized data
    universes = load_inputs_with_sectors()
    if not universes:
        return

    # Test connection
    sess = Session(USERNAME, PASSWORD)
    
    # Results storage
    all_results = {}
    final_baskets = {"gpt": {}, "grok": {}}
    
    # Process both universes
    for universe_name in ["gpt", "grok"]:
        universe_data = universes[universe_name]
        
        print(f"\n🚀 ANALYZING {universe_name.upper()} UNIVERSE:")
        print("=" * 50)
        
        universe_results = {}
        total_tickers = sum(len(tickers) for tickers in universe_data.values())
        processed = 0
        
        # Process each sector
        for sector_name, sector_tickers in universe_data.items():
            if not sector_tickers:
                print(f"⚠️  {sector_name}: No valid tickers")
                continue
                
            print(f"\n📂 {sector_name} ({len(sector_tickers)} tickers):")
            
            sector_results = []
            
            # Analyze each ticker in this sector
            for ticker_data in sector_tickers:
                if shutdown_requested:
                    break
                    
                processed += 1
                tkr = ticker_data["ticker"]
                
                print(f"  [{processed}/{total_tickers}] Analyzing {tkr}...", end=" ")
                
                result = await scan_one_ticker(sess, ticker_data, args.sample_sec)
                
                # Add context
                result.update({
                    "spot": ticker_data["spot"],
                    "target_expiry": ticker_data["target_expiry"],
                    "dte": ticker_data["dte"],
                    "atm_iv": ticker_data["atm_iv"],
                    "ivr": ticker_data["ivr"],
                    "sector": sector_name,
                    "universe": universe_name
                })
                
                universe_results[tkr] = result
                
                if result["status"] == "analyzed":
                    score = result.get("liquidity_score", 0)
                    rating = result.get("quality_rating", "UNKNOWN")
                    print(f"Score: {score:.1f} ({rating})")
                    sector_results.append((tkr, result))
                else:
                    print(f"❌ {result['status']}")
                
                await asyncio.sleep(0.1)  # Brief pause
            
            # Select best ticker from this sector
            if sector_results:
                sector_results.sort(key=lambda x: x[1].get("liquidity_score", 0), reverse=True)
                best_ticker, best_result = sector_results[0]
                final_baskets[universe_name][sector_name] = {
                    "ticker": best_ticker,
                    "score": best_result.get("liquidity_score", 0),
                    "rating": best_result.get("quality_rating", "UNKNOWN"),
                    "ivr": best_result.get("ivr", 0),
                    "tier": best_result.get("tier", "T3"),
                    "full_data": best_result
                }
                print(f"  🏆 Sector winner: {best_ticker} (Score: {best_result.get('liquidity_score', 0):.1f})")
            else:
                print(f"  ❌ No analyzable tickers in {sector_name}")
        
        all_results[universe_name] = universe_results

    # Save detailed results
    with open("step4_liquidity_detailed.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    # Save basket results
    with open("trading_baskets.json", "w") as f:
        json.dump(final_baskets, f, indent=2)

    # Display final baskets
    print(f"\n🎯 FINAL TRADING BASKETS:")
    print("=" * 70)
    
    for universe_name in ["gpt", "grok"]:
        basket = final_baskets[universe_name]
        
        print(f"\n🔥 {universe_name.upper()} BASKET (9 sectors):")
        print("-" * 50)
        
        if basket:
            basket_list = [(sector, data) for sector, data in basket.items()]
            basket_list.sort(key=lambda x: x[1]["score"], reverse=True)
            
            print(f"{'Sector':<25} {'Ticker':<6} {'Score':<8} {'Rating':<10} {'IVR':<6} {'Tier'}")
            print("-" * 70)
            
            for sector, data in basket_list:
                ticker = data["ticker"]
                score = data["score"]
                rating = data["rating"]
                ivr = data["ivr"]
                tier = data["tier"]
                
                print(f"{sector:<25} {ticker:<6} {score:<8.1f} {rating:<10} {ivr:<6.1f} {tier}")
            
            # Show top 3 from this basket
            print(f"\n🏆 Top 3 from {universe_name.upper()} basket:")
            for i, (sector, data) in enumerate(basket_list[:3], 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                print(f"   {emoji} {data['ticker']} ({sector}): Score {data['score']:.1f} | IVR {data['ivr']:.1f}%")
        else:
            print("   ❌ No valid tickers in basket")

    # Summary
    total_analyzed = sum(len(results) for results in all_results.values())
    gpt_basket_size = len(final_baskets["gpt"])
    grok_basket_size = len(final_baskets["grok"])
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   📈 Total tickers analyzed: {total_analyzed}")
    print(f"   🎯 GPT basket: {gpt_basket_size}/9 sectors")
    print(f"   🎯 Grok basket: {grok_basket_size}/9 sectors")
    print(f"   💾 Detailed results: step4_liquidity_detailed.json")
    print(f"   🏆 Trading baskets: trading_baskets.json")
    
    print(f"\n▶️  Next: Review trading_baskets.json for your 2 portfolios!")

def parse_args():
    parser = argparse.ArgumentParser(description="Dual Basket Liquidity System")
    parser.add_argument("--sample-sec", type=float, default=DEFAULT_SAMPLE_SEC, help="Collection time per ticker")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(run_dual_basket_analysis(args))
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
```
**Run:** `python3 liquidity.py`
