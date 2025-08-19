**Create:** `touch liquidity.py`
**Query:** `open -e liquidity.py`

```bash
# liquidity.py - Enhanced ranking system (always returns best options)
"""
Enhanced Δ30 liquidity scanner with RANKING SYSTEM instead of hard gates.
Always returns the best available options ranked by composite liquidity score.
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

# ---------------- Configuration ----------------
DEFAULT_SAMPLE_SEC = 20.0
DEFAULT_CONCURRENCY = 1
DEFAULT_MAX_TICKERS = None

# Reference thresholds for scoring (not hard gates)
REF_INSIDE_RATIO = 0.70      # Target: 70% tight spreads
REF_NBBO_AGE_MS = 1500       # Target: <1.5s quote age
REF_TPM = 25                 # Target: 25+ ticks/min
REF_SPREAD_ABS = 0.05        # Target: 5¢ spreads
REF_OI_MIN = 1000           # Target: 1000+ OI

# Spread/Depth thresholds for tier classification
T1_ABS, T1_REL, T1_OI = 0.10, 0.20, 10000
T2_ABS, T2_REL, T2_OI = 0.20, 0.40, 500

# Universe settings
MAX_OPT_SYMBOLS_PER_SIDE = 50
MONEYNESS_WIDTH = 0.50
MIN_TICKS_PER_LEG = 5
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
    """Classify liquidity tier (for reference only)."""
    if spread_med<=T1_ABS and mid_med>0 and (spread_med/mid_med)<=T1_REL and oi_avg>=T1_OI: return "T1"
    if spread_med<=T2_ABS and mid_med>0 and (spread_med/mid_med)<=T2_REL and oi_avg>=T2_OI: return "T2"
    return "T3"

def calculate_liquidity_score(metrics, ivr=0):
    """
    Calculate composite liquidity score (0-100, higher = better).
    Combines multiple factors with different weights.
    """
    spread_med = metrics.get("spread_med_Δ30", 999)
    mid_med = metrics.get("mid_med_Δ30", 1)
    inside_ratio = metrics.get("inside_threshold_ratio_Δ30", 0)
    ticks_pm = metrics.get("ticks_per_min", 0)
    nbbo_age_ms = metrics.get("nbbo_age_ms_med", 99999)
    oi_min = metrics.get("oi_min_Δ30", 0)
    
    # Individual component scores (0-100 each)
    
    # 1. Spread Score (25% weight) - lower spreads = higher score
    spread_score = max(0, min(100, 100 * (1 - spread_med / max(REF_SPREAD_ABS * 10, 0.01))))
    
    # 2. Inside Ratio Score (20% weight) - higher ratio = higher score  
    inside_score = min(100, 100 * inside_ratio / REF_INSIDE_RATIO)
    
    # 3. Tick Flow Score (20% weight) - more ticks = higher score
    tick_score = min(100, 100 * ticks_pm / REF_TPM)
    
    # 4. Quote Freshness Score (15% weight) - fresher = higher score
    freshness_score = max(0, min(100, 100 * (1 - nbbo_age_ms / (REF_NBBO_AGE_MS * 10))))
    
    # 5. Open Interest Score (15% weight) - more OI = higher score
    oi_score = min(100, 100 * oi_min / REF_OI_MIN)
    
    # 6. IV Rank Bonus (5% weight) - higher IV rank = higher score
    ivr_score = min(100, ivr)
    
    # Weighted composite score
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
    """Convert numeric score to quality rating."""
    if score >= 80: return "🟢 EXCELLENT"
    elif score >= 65: return "🟡 GOOD" 
    elif score >= 45: return "🟠 FAIR"
    elif score >= 25: return "🔴 POOR"
    else: return "⚫ TERRIBLE"

def choose_subset(opts, spot):
    """Choose options near the money for analysis."""
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
    """Check if markets are likely open."""
    now = datetime.now(timezone.utc)
    hour_utc = now.hour
    weekday = now.weekday()
    return weekday < 5 and 14 <= hour_utc <= 21

async def test_simple_connection(sess, show_details=True):
    """Test connection with detailed output."""
    try:
        async with DXLinkStreamer(sess) as streamer:
            await streamer.subscribe(Quote, ["SPY"])
            
            for i in range(10):
                try:
                    q = await asyncio.wait_for(streamer.get_event(Quote), timeout=1.0)
                    if q and q.event_symbol == "SPY":
                        if show_details:
                            spread = float(q.ask_price) - float(q.bid_price)
                            print(f"    📊 SPY: ${q.bid_price} x ${q.ask_price} (spread: ${spread:.3f})")
                        await streamer.unsubscribe(Quote, ["SPY"])
                        return True
                except asyncio.TimeoutError:
                    continue
            
            await streamer.unsubscribe(Quote, ["SPY"])
            return False
    except Exception as e:
        if show_details:
            print(f"    ❌ Connection error: {e}")
        return False

def show_detailed_scoring(ticker, metrics, ivr, score_breakdown):
    """Show detailed scoring breakdown."""
    print(f"\n📊 [{ticker}] LIQUIDITY SCORING BREAKDOWN:")
    print("-" * 50)
    
    # Show raw metrics
    spread = metrics.get("spread_med_Δ30", 0)
    inside_ratio = metrics.get("inside_threshold_ratio_Δ30", 0)
    ticks_pm = metrics.get("ticks_per_min", 0)
    nbbo_age = metrics.get("nbbo_age_ms_med", 0)
    oi_min = metrics.get("oi_min_Δ30", 0)
    
    print(f"   📈 Raw Metrics:")
    print(f"      • Spread: ${spread:.4f}")
    print(f"      • Inside Ratio: {inside_ratio:.3f} ({inside_ratio*100:.1f}%)")
    print(f"      • Ticks/Min: {ticks_pm:.1f}")
    print(f"      • NBBO Age: {nbbo_age:.0f}ms ({nbbo_age/1000:.1f}s)")
    print(f"      • Min OI: {oi_min:,}")
    print(f"      • IV Rank: {ivr:.1f}%")
    
    # Show component scores
    components = score_breakdown["component_scores"]
    composite = score_breakdown["composite_score"]
    
    print(f"\n   🎯 Component Scores (0-100):")
    print(f"      • Spread Quality: {components['spread']:.1f}/100 (25% weight)")
    print(f"      • Inside Ratio: {components['inside_ratio']:.1f}/100 (20% weight)")
    print(f"      • Tick Flow: {components['tick_flow']:.1f}/100 (20% weight)")
    print(f"      • Quote Freshness: {components['freshness']:.1f}/100 (15% weight)")
    print(f"      • Open Interest: {components['open_interest']:.1f}/100 (15% weight)")
    print(f"      • IV Rank Bonus: {components['iv_rank']:.1f}/100 (5% weight)")
    
    quality = get_quality_rating(composite)
    print(f"\n   🏆 COMPOSITE SCORE: {composite:.1f}/100 {quality}")

async def scan_one_ticker(sess, rec, sample_sec, verbose=False):
    """Scan one ticker and return liquidity metrics + score."""
    global shutdown_requested
    
    tkr = rec["ticker"]
    spot = rec["spot"]
    exp_iso = rec["target_expiry"]
    ivr = rec.get("ivr", 0)
    
    if shutdown_requested:
        return {"ticker": tkr, "status": "shutdown"}
    
    try:
        async with DXLinkStreamer(sess) as streamer:
            # Load options chain
            try:
                chain = get_option_chain(sess, tkr)
                if verbose:
                    print(f"\n🔗 [{tkr}] Loaded options chain: {len(chain)} expiries")
            except Exception as e:
                return {"ticker": tkr, "status": f"chain_error", "error": str(e)}

            # Find target expiry
            exp = None
            for d in chain.keys():
                if d.isoformat() == exp_iso:
                    exp = d
                    break
            
            if not exp:
                return {"ticker": tkr, "status": "no_expiry"}

            # Get options subset
            opts = choose_subset(chain[exp], spot)
            if not opts:
                return {"ticker": tkr, "status": "no_options"}

            symbols = [o.streamer_symbol for o in opts]
            meta = {o.streamer_symbol: {"strike": float(o.strike_price), "type": o.option_type.value} for o in opts}

            if verbose:
                n_calls = sum(1 for o in opts if o.option_type.value == "C")
                n_puts = len(opts) - n_calls
                print(f"📡 [{tkr}] Subscribing to {len(symbols)} options (C:{n_calls}/P:{n_puts})")

            # Subscribe with delays
            await streamer.subscribe(Quote, symbols)
            await asyncio.sleep(1.0)
            await streamer.subscribe(Greeks, symbols)
            await asyncio.sleep(1.0)
            await streamer.subscribe(Summary, symbols)
            await asyncio.sleep(1.0)

            # Collection phase
            quotes = defaultdict(list)
            greeks = {}
            summary = {}
            counts = {"quotes": 0, "greeks": 0, "summary": 0}
            
            start_time = asyncio.get_event_loop().time()
            last_report = start_time
            
            if verbose:
                print(f"⏱️  [{tkr}] Starting {sample_sec}s collection...")

            while True:
                if shutdown_requested:
                    break
                    
                now_time = asyncio.get_event_loop().time()
                elapsed = now_time - start_time
                
                if elapsed >= sample_sec:
                    break

                # Progress report
                if verbose and now_time - last_report >= HEARTBEAT_SEC:
                    last_report = now_time
                    active_quotes = len([s for s in quotes if quotes[s]])
                    rate_q = counts['quotes'] / max(elapsed, 1) * 60
                    print(f"  📊 [{tkr}] {elapsed:.1f}s | Q:{counts['quotes']} ({rate_q:.0f}/min) G:{counts['greeks']} S:{counts['summary']} | Active:{active_quotes}")

                timeout = 0.5
                
                # Collect quotes
                try:
                    q = await asyncio.wait_for(streamer.get_event(Quote), timeout=timeout)
                    if q and q.event_symbol in meta:
                        bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
                        if bid > 0 and ask > 0 and ask >= bid:
                            quotes[q.event_symbol].append((bid, ask))
                            counts["quotes"] += 1
                            
                            # Show first few quotes in verbose mode
                            if verbose and counts["quotes"] <= 2:
                                spread = ask - bid
                                print(f"    💰 Quote: {q.event_symbol} ${bid:.3f}x${ask:.3f} (spread: ${spread:.3f})")
                except asyncio.TimeoutError:
                    pass

                # Collect greeks
                try:
                    g = await asyncio.wait_for(streamer.get_event(Greeks), timeout=timeout)
                    if g and g.event_symbol in meta:
                        greeks[g.event_symbol] = {
                            "delta": float(g.delta or 0),
                            "iv": float(g.volatility or 0)
                        }
                        counts["greeks"] += 1
                        
                        # Show first few greeks in verbose mode
                        if verbose and counts["greeks"] <= 2:
                            print(f"    📐 Greeks: {g.event_symbol} δ={g.delta:.3f} IV={g.volatility:.3f}")
                except asyncio.TimeoutError:
                    pass

                # Collect summary
                try:
                    s = await asyncio.wait_for(streamer.get_event(Summary), timeout=timeout)
                    if s and s.event_symbol in meta:
                        summary[s.event_symbol] = {"oi": int(s.open_interest or 0)}
                        counts["summary"] += 1
                        
                        # Show first few summaries in verbose mode
                        if verbose and counts["summary"] <= 2:
                            print(f"    📋 Summary: {s.event_symbol} OI={s.open_interest:,}")
                except asyncio.TimeoutError:
                    pass

            # Cleanup subscriptions
            try:
                await streamer.unsubscribe(Quote, symbols)
                await streamer.unsubscribe(Greeks, symbols)
                await streamer.unsubscribe(Summary, symbols)
            except:
                pass

            if verbose:
                print(f"📊 [{tkr}] Collection complete: {elapsed:.1f}s | Events: {counts}")

            # Analysis phase
            call30 = nearest_delta(+1, 0.30, greeks, meta)
            put30 = nearest_delta(-1, 0.30, greeks, meta)

            if not call30 or not put30:
                if verbose:
                    print(f"❌ [{tkr}] Could not find Δ30 options")
                return {"ticker": tkr, "status": "no_delta30", "debug": {"greeks_count": len(greeks)}}

            if verbose:
                c_strike = meta[call30]["strike"]
                p_strike = meta[put30]["strike"]
                c_delta = greeks.get(call30, {}).get("delta", 0)
                p_delta = greeks.get(put30, {}).get("delta", 0)
                print(f"🎯 [{tkr}] Delta-30 selection:")
                print(f"    Call: {call30} (K=${c_strike}, δ={c_delta:.3f})")
                print(f"    Put: {put30} (K=${p_strike}, δ={p_delta:.3f})")

            # Convert quotes and calculate stats
            quotes_deque = {}
            for sym, quote_list in quotes.items():
                quotes_deque[sym] = deque(quote_list, maxlen=500)

            cs = stats_for_leg(call30, quotes_deque, elapsed)
            ps = stats_for_leg(put30, quotes_deque, elapsed)

            if not cs or not ps:
                if verbose:
                    print(f"❌ [{tkr}] Insufficient quote data for analysis")
                return {"ticker": tkr, "status": "insufficient_quotes"}

            # Calculate final metrics
            spread_med_30 = max(cs["spread_med"], ps["spread_med"])
            mid_med_30 = med([cs["mid_med"], ps["mid_med"]])
            inside_ratio = (cs["inside_ratio"] + ps["inside_ratio"]) / 2
            ticks_pm = (cs["ticks_pm"] + ps["ticks_pm"]) / 2
            nbbo_age_ms = med([cs["nbbo_age_ms"], ps["nbbo_age_ms"]])
            oi_min = min(summary.get(call30, {}).get("oi", 0), summary.get(put30, {}).get("oi", 0))

            tier = classify_tier(spread_med_30, mid_med_30, (summary.get(call30, {}).get("oi", 0) + summary.get(put30, {}).get("oi", 0)) / 2)

            # Create metrics dict
            metrics = {
                "spread_med_Δ30": round(spread_med_30, 4),
                "mid_med_Δ30": round(mid_med_30, 4),
                "inside_threshold_ratio_Δ30": round(inside_ratio, 3),
                "ticks_per_min": round(ticks_pm, 2),
                "nbbo_age_ms_med": round(nbbo_age_ms, 0),
                "oi_min_Δ30": int(oi_min)
            }

            # Calculate liquidity score
            score_breakdown = calculate_liquidity_score(metrics, ivr)
            composite_score = score_breakdown["composite_score"]

            if verbose:
                show_detailed_scoring(tkr, metrics, ivr, score_breakdown)

            quality_rating = get_quality_rating(composite_score)
            if verbose:
                print(f"\n🏆 [{tkr}] FINAL RATING: {quality_rating} (Score: {composite_score:.1f}/100)")

            return {
                "ticker": tkr,
                "status": "analyzed",  # Always "analyzed" now - no hard pass/fail
                "tier": tier,
                "liquidity_score": composite_score,
                "quality_rating": quality_rating.split(" ", 1)[1],  # Remove emoji for JSON
                "score_breakdown": score_breakdown,
                "metrics": metrics
            }

    except Exception as e:
        if verbose:
            print(f"❌ [{tkr}] Error: {e}")
        return {"ticker": tkr, "status": "error", "error": str(e)}

def load_inputs(ticker_filter=None, max_tickers=None, verbose=False):
    """Load input data."""
    try:
        with open("step3_atm_iv.json") as f:
            data = json.load(f)
        
        filtered = []
        for r in data:
            if r.get("status") != "ok":
                continue
            if ticker_filter and r["ticker"] not in ticker_filter:
                continue
            filtered.append(r)
        
        if max_tickers:
            filtered = filtered[:max_tickers]
        
        if verbose:
            print(f"📋 Loaded {len(filtered)} valid tickers from step3_atm_iv.json")
        
        return filtered
        
    except FileNotFoundError:
        print("❌ step3_atm_iv.json not found. Run atm_iv.py first.")
        return []

async def run_ranking_analysis(args):
    """Run ranking-based liquidity analysis."""
    global shutdown_requested
    
    print("🏆 Liquidity Ranking System v3.0")
    print("=" * 60)
    print("📊 RANKING MODE: Always returns best available options")
    
    # Market status
    market_open = is_market_hours()
    print(f"🕒 Market: {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
    if not market_open:
        print("💡 After-hours: Expect lower scores, but still get rankings!")

    # Load data
    ticker_filter = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] or None
    tickers = load_inputs(ticker_filter, args.max_tickers, args.verbose)
    
    if not tickers:
        return

    # Test connection
    sess = Session(USERNAME, PASSWORD)
    if args.verbose:
        print(f"\n🔌 Testing connection...")
        conn_ok = await test_simple_connection(sess, args.verbose)
        print(f"   Status: {'✅ CONNECTED' if conn_ok else '❌ FAILED'}")

    # Process tickers
    results = {}
    completed = 0
    
    print(f"\n🚀 ANALYZING {len(tickers)} TICKERS:")
    print("=" * 60)
    
    for rec in tickers:
        if shutdown_requested:
            break
            
        completed += 1
        tkr = rec["ticker"]
        
        if not args.verbose:
            print(f"[{completed}/{len(tickers)}] Analyzing {tkr}...")
        
        result = await scan_one_ticker(sess, rec, args.sample_sec, args.verbose)
        
        # Add context
        result.update({
            "spot": rec["spot"],
            "target_expiry": rec["target_expiry"],
            "dte": rec["dte"],
            "atm_iv": rec["atm_iv"],
            "ivr": rec["ivr"]
        })
        
        results[tkr] = result
        
        # Show progress
        if result["status"] == "analyzed":
            score = result.get("liquidity_score", 0)
            rating = result.get("quality_rating", "UNKNOWN")
            if not args.verbose:
                print(f"   Score: {score:.1f}/100 ({rating})")
        else:
            if not args.verbose:
                print(f"   ❌ {result['status']}")
        
        # Brief pause
        await asyncio.sleep(0.2)

    # Save results
    with open("step4_liquidity.json", "w") as f:
        json.dump(results, f, indent=2)

    # Create rankings
    analyzed_results = [(tkr, data) for tkr, data in results.items() if data["status"] == "analyzed"]
    analyzed_results.sort(key=lambda x: x[1].get("liquidity_score", 0), reverse=True)

    print(f"\n🏆 LIQUIDITY RANKINGS:")
    print("=" * 70)
    
    if analyzed_results:
        print(f"{'Rank':<4} {'Ticker':<6} {'Score':<8} {'Rating':<10} {'IVR':<6} {'Tier':<4} {'Spread':<8} {'TPM':<6}")
        print("-" * 70)
        
        for i, (tkr, data) in enumerate(analyzed_results, 1):
            score = data.get("liquidity_score", 0)
            rating = data.get("quality_rating", "UNKNOWN")
            ivr = data.get("ivr", 0)
            tier = data.get("tier", "T3")
            metrics = data.get("metrics", {})
            spread = metrics.get("spread_med_Δ30", 0)
            tpm = metrics.get("ticks_per_min", 0)
            
            print(f"{i:<4} {tkr:<6} {score:<8.1f} {rating:<10} {ivr:<6.1f} {tier:<4} ${spread:<7.3f} {tpm:<6.1f}")
        
        # Show top candidates
        top_n = min(10, len(analyzed_results))
        print(f"\n🎯 TOP {top_n} TRADE CANDIDATES:")
        print("-" * 50)
        
        for i, (tkr, data) in enumerate(analyzed_results[:top_n], 1):
            score = data.get("liquidity_score", 0)
            rating = data.get("quality_rating", "UNKNOWN")
            ivr = data.get("ivr", 0)
            dte = data.get("dte", 0)
            tier = data.get("tier", "T3")
            
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:2d}."
            print(f"   {emoji} {tkr}: Score {score:.1f} | {rating} | IVR {ivr:.1f}% | {tier} {dte}DTE")
    
    else:
        print("❌ No tickers could be analyzed")

    # Summary
    total = len(results)
    analyzed = len(analyzed_results)
    high_score = sum(1 for _, data in analyzed_results if data.get("liquidity_score", 0) >= 65)
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   📈 Total tickers: {total}")
    print(f"   ✅ Successfully analyzed: {analyzed}")
    print(f"   🟢 Good+ quality (≥65 score): {high_score}")
    print(f"   💾 Results: step4_liquidity.json")
    
    if market_open:
        print(f"\n💡 During market hours - these rankings reflect current conditions")
    else:
        print(f"\n💡 After hours - top-ranked tickers will likely improve during market hours")

def parse_args():
    parser = argparse.ArgumentParser(description="Liquidity Ranking System")
    parser.add_argument("--sample-sec", type=float, default=DEFAULT_SAMPLE_SEC, help="Collection time per ticker")
    parser.add_argument("--max-tickers", type=int, help="Limit number of tickers")
    parser.add_argument("--tickers", type=str, default="", help="Specific tickers (comma-separated)")
    parser.add_argument("--verbose", action="store_true", help="Detailed output per ticker")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(run_ranking_analysis(args))
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
```
**Run:** `python3 liquidity.py`
