**Create:** `touch liquidity.py`
**Query:** `open -e liquidity.py`

```bash
# liquidity.py - Enhanced with built-in data flow visualization
"""
Enhanced Δ30 liquidity scanner with detailed data flow analysis built-in.
Shows exactly what data is flowing and why gates pass/fail.
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

# Production gates
PROD_INSIDE_RATIO_MIN = 0.50
PROD_NBBO_AGE_MS_MAX = 3000
PROD_TPM_MIN = 8

# Loose gates
LOOSE_INSIDE_RATIO_MIN = 0.30
LOOSE_NBBO_AGE_MS_MAX = 8000
LOOSE_TPM_MIN = 2

# Thresholds
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

def classify(spread_med, mid_med, oi_avg):
    if spread_med<=T1_ABS and mid_med>0 and (spread_med/mid_med)<=T1_REL and oi_avg>=T1_OI: return "T1"
    if spread_med<=T2_ABS and mid_med>0 and (spread_med/mid_med)<=T2_REL and oi_avg>=T2_OI: return "T2"
    return "T3"

def allowed(tier, mid):
    if tier=="T1": return min(T1_ABS, T1_REL*max(mid,1e-9))
    if tier=="T2": return min(T2_ABS, T2_REL*max(mid,1e-9))
    return 0.0

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

def show_data_flow_summary(ticker, counts, quotes, greeks, summary, elapsed):
    """Show detailed data flow analysis."""
    print(f"\n📊 [{ticker}] DATA FLOW ANALYSIS:")
    print(f"   Collection Time: {elapsed:.1f}s")
    print(f"   📡 Events Received:")
    print(f"      • Quotes: {counts['quotes']:,} events")
    print(f"      • Greeks: {counts['greeks']:,} events") 
    print(f"      • Summary: {counts['summary']:,} events")
    
    # Analyze quote distribution
    active_symbols = len([s for s in quotes if quotes[s]])
    total_quotes = sum(len(q) for q in quotes.values())
    avg_quotes_per_symbol = total_quotes / max(active_symbols, 1)
    
    print(f"   📈 Quote Analysis:")
    print(f"      • Active symbols: {active_symbols}")
    print(f"      • Total quotes collected: {total_quotes:,}")
    print(f"      • Avg quotes/symbol: {avg_quotes_per_symbol:.1f}")
    
    # Show sample quotes for top symbols
    quote_counts = [(sym, len(q)) for sym, q in quotes.items() if q]
    quote_counts.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   🔥 Most Active Options:")
    for sym, count in quote_counts[:3]:
        if count > 0:
            latest_quote = quotes[sym][-1] if quotes[sym] else (0, 0)
            spread = latest_quote[1] - latest_quote[0] if latest_quote[1] >= latest_quote[0] else 0
            print(f"      • {sym}: {count} quotes, latest spread: ${spread:.3f}")
    
    # Greeks analysis
    deltas = [(sym, g.get('delta', 0)) for sym, g in greeks.items()]
    calls_with_greeks = sum(1 for sym, delta in deltas if delta > 0)
    puts_with_greeks = sum(1 for sym, delta in deltas if delta < 0)
    
    print(f"   🎯 Greeks Analysis:")
    print(f"      • Calls with Greeks: {calls_with_greeks}")
    print(f"      • Puts with Greeks: {puts_with_greeks}")
    
    # Show delta range
    if deltas:
        delta_values = [abs(d) for _, d in deltas if d != 0]
        if delta_values:
            min_delta, max_delta = min(delta_values), max(delta_values)
            print(f"      • Delta range: {min_delta:.3f} to {max_delta:.3f}")

def analyze_gate_failures(ticker, gates_eval, metrics, gates, tier):
    """Show detailed gate failure analysis."""
    print(f"\n🚨 [{ticker}] GATE FAILURE ANALYSIS:")
    
    spread = metrics.get("spread_med_Δ30", 0)
    inside_ratio = metrics.get("inside_threshold_ratio_Δ30", 0)
    ticks_pm = metrics.get("ticks_per_min", 0)
    nbbo_age = metrics.get("nbbo_age_ms_med", 0)
    oi_min = metrics.get("oi_min_Δ30", 0)
    
    print(f"   📋 GATE REQUIREMENTS vs ACTUAL:")
    
    # Inside ratio gate
    status = "✅ PASS" if gates_eval["inside_ratio_ok"] else "❌ FAIL"
    print(f"   1. Inside Ratio: {status}")
    print(f"      Required: ≥{gates['inside_ratio_min']:.2f} ({gates['inside_ratio_min']*100:.0f}%)")
    print(f"      Actual: {inside_ratio:.3f} ({inside_ratio*100:.1f}%)")
    if not gates_eval["inside_ratio_ok"]:
        print(f"      💡 Only {inside_ratio*100:.1f}% of spreads were tight (need {gates['inside_ratio_min']*100:.0f}%+)")
    
    # NBBO freshness gate
    status = "✅ PASS" if gates_eval["nbbo_fresh_ok"] else "❌ FAIL"
    print(f"   2. NBBO Freshness: {status}")
    print(f"      Required: ≤{gates['nbbo_age_ms_max']:.0f}ms")
    print(f"      Actual: {nbbo_age:.0f}ms ({nbbo_age/1000:.1f}s)")
    if not gates_eval["nbbo_fresh_ok"]:
        print(f"      💡 Quotes are {nbbo_age/1000:.1f}s old (need <{gates['nbbo_age_ms_max']/1000:.1f}s)")
    
    # Tick rate gate
    status = "✅ PASS" if gates_eval["ticks_ok"] else "❌ FAIL"
    print(f"   3. Tick Rate: {status}")
    print(f"      Required: ≥{gates['tpm_min']:.0f} ticks/min")
    print(f"      Actual: {ticks_pm:.1f} ticks/min")
    if not gates_eval["ticks_ok"]:
        print(f"      💡 Only {ticks_pm:.1f} quote updates/min (need {gates['tpm_min']:.0f}+ for liquidity)")
    
    # Spread gate
    status = "✅ PASS" if gates_eval["spread_ok"] else "❌ FAIL"
    print(f"   4. Spread Quality: {status}")
    print(f"      Tier: {tier}")
    print(f"      Actual spread: ${spread:.4f}")
    if not gates_eval["spread_ok"]:
        if tier == "T1":
            print(f"      💡 T1 needs spreads ≤$0.10 or ≤20% of mid price")
        elif tier == "T2":
            print(f"      💡 T2 needs spreads ≤$0.20 or ≤40% of mid price")
        else:
            print(f"      💡 T3 = poor liquidity (spreads too wide)")
    
    # OI gate
    status = "✅ PASS" if gates_eval["oi_ok"] else "❌ FAIL"
    required_oi = T1_OI if tier == "T1" else T2_OI
    print(f"   5. Open Interest: {status}")
    print(f"      Required: ≥{required_oi:,} for {tier}")
    print(f"      Actual: {oi_min:,}")
    if not gates_eval["oi_ok"]:
        print(f"      💡 Not enough contracts outstanding for institutional flow")

def show_market_hours_prediction(metrics, ticker):
    """Show what this ticker might look like during market hours."""
    spread = metrics.get("spread_med_Δ30", 0)
    ticks_pm = metrics.get("ticks_per_min", 0)
    nbbo_age = metrics.get("nbbo_age_ms_med", 0)
    
    print(f"\n🔮 [{ticker}] MARKET HOURS PREDICTION:")
    if nbbo_age > 5000 or ticks_pm < 5:  # Very after-hours conditions
        predicted_spread = max(0.05, spread * 0.1)  # 10x improvement
        predicted_ticks = max(ticks_pm * 8, 25)     # 8x improvement
        predicted_nbbo = min(nbbo_age * 0.2, 1500)  # 5x improvement
        
        print(f"   📈 Expected improvements:")
        print(f"      • Spread: ${spread:.4f} → ~${predicted_spread:.3f} ({spread/predicted_spread:.0f}x tighter)")
        print(f"      • Ticks/min: {ticks_pm:.1f} → ~{predicted_ticks:.0f} ({predicted_ticks/max(ticks_pm,1):.0f}x faster)")
        print(f"      • NBBO age: {nbbo_age:.0f}ms → ~{predicted_nbbo:.0f}ms ({nbbo_age/max(predicted_nbbo,1):.0f}x fresher)")
        print(f"   🎯 Likely result: ✅ PASS most/all gates")
    else:
        print(f"   💭 Conditions already decent - should improve further during market hours")

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

async def scan_one_ticker(sess, rec, sample_sec, gates):
    """Scan one ticker with enhanced data flow visualization."""
    global shutdown_requested
    
    tkr = rec["ticker"]
    spot = rec["spot"]
    exp_iso = rec["target_expiry"]
    
    if shutdown_requested:
        return {"ticker": tkr, "status": "shutdown"}
    
    try:
        async with DXLinkStreamer(sess) as streamer:
            # Load options chain
            try:
                chain = get_option_chain(sess, tkr)
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

            n_calls = sum(1 for o in opts if o.option_type.value == "C")
            n_puts = len(opts) - n_calls
            print(f"📡 [{tkr}] Subscribing to {len(symbols)} options (C:{n_calls}/P:{n_puts})")
            print(f"    Sample symbols: {symbols[0]}, {symbols[len(symbols)//2] if len(symbols) > 1 else 'N/A'}")

            # Subscribe with delays
            await streamer.subscribe(Quote, symbols)
            await asyncio.sleep(1.0)
            await streamer.subscribe(Greeks, symbols)
            await asyncio.sleep(1.0)
            await streamer.subscribe(Summary, symbols)
            await asyncio.sleep(1.0)

            # Collection phase with enhanced monitoring
            quotes = defaultdict(list)
            greeks = {}
            summary = {}
            counts = {"quotes": 0, "greeks": 0, "summary": 0}
            
            start_time = asyncio.get_event_loop().time()
            last_report = start_time
            
            print(f"⏱️  [{tkr}] Starting {sample_sec}s data collection...")

            while True:
                if shutdown_requested:
                    break
                    
                now_time = asyncio.get_event_loop().time()
                elapsed = now_time - start_time
                
                if elapsed >= sample_sec:
                    break

                # Enhanced progress report
                if now_time - last_report >= HEARTBEAT_SEC:
                    last_report = now_time
                    active_quotes = len([s for s in quotes if quotes[s]])
                    rate_q = counts['quotes'] / max(elapsed, 1) * 60
                    rate_g = counts['greeks'] / max(elapsed, 1) * 60
                    print(f"  📊 [{tkr}] {elapsed:.1f}s | Q:{counts['quotes']} ({rate_q:.0f}/min) G:{counts['greeks']} ({rate_g:.0f}/min) S:{counts['summary']} | Active:{active_quotes}")

                timeout = 0.5
                
                # Collect quotes
                try:
                    q = await asyncio.wait_for(streamer.get_event(Quote), timeout=timeout)
                    if q and q.event_symbol in meta:
                        bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
                        if bid > 0 and ask > 0 and ask >= bid:
                            quotes[q.event_symbol].append((bid, ask))
                            counts["quotes"] += 1
                            
                            # Show first few quotes
                            if counts["quotes"] <= 3:
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
                        
                        # Show first few greeks
                        if counts["greeks"] <= 3:
                            print(f"    📐 Greeks: {g.event_symbol} δ={g.delta:.3f} IV={g.volatility:.3f}")
                except asyncio.TimeoutError:
                    pass

                # Collect summary
                try:
                    s = await asyncio.wait_for(streamer.get_event(Summary), timeout=timeout)
                    if s and s.event_symbol in meta:
                        summary[s.event_symbol] = {"oi": int(s.open_interest or 0)}
                        counts["summary"] += 1
                        
                        # Show first few summaries
                        if counts["summary"] <= 3:
                            print(f"    📋 Summary: {s.event_symbol} OI={s.open_interest:,}")
                except asyncio.TimeoutError:
                    pass

            # Cleanup
            try:
                await streamer.unsubscribe(Quote, symbols)
                await streamer.unsubscribe(Greeks, symbols)
                await streamer.unsubscribe(Summary, symbols)
            except:
                pass

            # Show detailed data flow analysis
            show_data_flow_summary(tkr, counts, quotes, greeks, summary, elapsed)

            # Find delta-30 options
            call30 = nearest_delta(+1, 0.30, greeks, meta)
            put30 = nearest_delta(-1, 0.30, greeks, meta)

            if not call30 or not put30:
                print(f"\n❌ [{tkr}] Could not find Δ30 options")
                print(f"    Greeks received: {len(greeks)} symbols")
                return {"ticker": tkr, "status": "no_delta30"}

            # Show delta-30 selection
            c_strike = meta[call30]["strike"]
            p_strike = meta[put30]["strike"]
            c_delta = greeks.get(call30, {}).get("delta", 0)
            p_delta = greeks.get(put30, {}).get("delta", 0)
            print(f"\n🎯 [{tkr}] DELTA-30 SELECTION:")
            print(f"    Call: {call30} (K=${c_strike}, δ={c_delta:.3f})")
            print(f"    Put: {put30} (K=${p_strike}, δ={p_delta:.3f})")

            # Convert quotes and calculate stats
            quotes_deque = {}
            for sym, quote_list in quotes.items():
                quotes_deque[sym] = deque(quote_list, maxlen=500)

            cs = stats_for_leg(call30, quotes_deque, elapsed)
            ps = stats_for_leg(put30, quotes_deque, elapsed)

            if not cs or not ps:
                print(f"\n❌ [{tkr}] Insufficient quote data for analysis")
                return {"ticker": tkr, "status": "insufficient_quotes"}

            # Calculate final metrics
            spread_med_30 = max(cs["spread_med"], ps["spread_med"])
            mid_med_30 = med([cs["mid_med"], ps["mid_med"]])
            inside_ratio = (cs["inside_ratio"] + ps["inside_ratio"]) / 2
            ticks_pm = (cs["ticks_pm"] + ps["ticks_pm"]) / 2
            nbbo_age_ms = med([cs["nbbo_age_ms"], ps["nbbo_age_ms"]])
            oi_min = min(summary.get(call30, {}).get("oi", 0), summary.get(put30, {}).get("oi", 0))

            tier = classify(spread_med_30, mid_med_30, (summary.get(call30, {}).get("oi", 0) + summary.get(put30, {}).get("oi", 0)) / 2)
            spread_ok = spread_med_30 <= allowed(tier, mid_med_30)
            oi_ok = oi_min >= (T1_OI if tier == "T1" else T2_OI)

            # Evaluate gates
            gates_eval = {
                "inside_ratio_ok": inside_ratio >= gates["inside_ratio_min"],
                "nbbo_fresh_ok": nbbo_age_ms <= gates["nbbo_age_ms_max"],
                "ticks_ok": ticks_pm >= gates["tpm_min"],
                "spread_ok": spread_ok,
                "oi_ok": oi_ok
            }
            passed = all(gates_eval.values())

            # Show results
            status_emoji = "✅" if passed else "❌"
            print(f"\n{status_emoji} [{tkr}] FINAL RESULT: {'PASS' if passed else 'FAIL'} | Tier: {tier}")

            # Show detailed metrics
            metrics = {
                "spread_med_Δ30": round(spread_med_30, 4),
                "mid_med_Δ30": round(mid_med_30, 4),
                "inside_threshold_ratio_Δ30": round(inside_ratio, 3),
                "ticks_per_min": round(ticks_pm, 2),
                "nbbo_age_ms_med": round(nbbo_age_ms, 0),
                "oi_min_Δ30": int(oi_min)
            }

            if not passed:
                analyze_gate_failures(tkr, gates_eval, metrics, gates, tier)
                show_market_hours_prediction(metrics, tkr)

            return {
                "ticker": tkr,
                "status": "ok" if passed else "failed_gates",
                "tier": tier,
                "metrics": metrics,
                "failure_reasons": [k for k, v in gates_eval.items() if not v]
            }

    except Exception as e:
        print(f"\n❌ [{tkr}] Error: {e}")
        return {"ticker": tkr, "status": "error", "error": str(e)}

def load_inputs(ticker_filter=None, max_tickers=None):
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
        
        print(f"📋 Loaded {len(filtered)} valid tickers from step3_atm_iv.json")
        return filtered
        
    except FileNotFoundError:
        print("❌ step3_atm_iv.json not found. Run atm_iv.py first.")
        return []

async def run_sequential(args):
    """Run enhanced sequential analysis."""
    global shutdown_requested
    
    print("🔥 Liquidity Scanner v2.5 - Enhanced Data Flow")
    print("=" * 60)
    
    # Setup gates
    gates = {
        "inside_ratio_min": LOOSE_INSIDE_RATIO_MIN if args.loose else PROD_INSIDE_RATIO_MIN,
        "nbbo_age_ms_max": LOOSE_NBBO_AGE_MS_MAX if args.loose else PROD_NBBO_AGE_MS_MAX,
        "tpm_min": LOOSE_TPM_MIN if args.loose else PROD_TPM_MIN
    }
    
    gate_mode = "LOOSE" if args.loose else "PRODUCTION"
    print(f"📊 GATE THRESHOLDS ({gate_mode}):")
    print(f"   • Inside Ratio: ≥{gates['inside_ratio_min']:.2f} ({gates['inside_ratio_min']*100:.0f}%)")
    print(f"   • NBBO Age: ≤{gates['nbbo_age_ms_max']:.0f}ms")
    print(f"   • Tick Rate: ≥{gates['tpm_min']:.0f}/min")
    
    # Market status
    market_open = is_market_hours()
    print(f"\n🕒 MARKET STATUS: {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
    if not market_open:
        print("💡 Running after-hours - expect wide spreads and slow updates")

    # Load data
    ticker_filter = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] or None
    tickers = load_inputs(ticker_filter, args.max_tickers)
    
    if not tickers:
        return

    # Test connection
    sess = Session(USERNAME, PASSWORD)
    print(f"\n🔌 TESTING CONNECTION:")
    conn_ok = await test_simple_connection(sess, True)
    print(f"   Status: {'✅ CONNECTED' if conn_ok else '❌ FAILED'}")

    # Process tickers
    results = {}
    completed = 0
    
    print(f"\n🚀 PROCESSING {len(tickers)} TICKERS:")
    print("=" * 60)
    
    for rec in tickers:
        if shutdown_requested:
            break
            
        completed += 1
        result = await scan_one_ticker(sess, rec, args.sample_sec, gates)
        
        # Add context
        result.update({
            "spot": rec["spot"],
            "target_expiry": rec["target_expiry"],
            "dte": rec["dte"],
            "atm_iv": rec["atm_iv"],
            "ivr": rec["ivr"]
        })
        
        results[rec["ticker"]] = result
        
        # Brief pause
        await asyncio.sleep(0.5)
        
        print("=" * 60)

    # Save and summarize
    with open("step4_liquidity.json", "w") as f:
        json.dump(results, f, indent=2)

    # Final summary
    total = len(results)
    ok_count = sum(1 for r in results.values() if r["status"] == "ok")
    high_ivr = sum(1 for r in results.values() if r["status"] == "ok" and r.get("ivr", 0) >= 30)
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"✅ Liquid tickers: {ok_count}/{total} ({ok_count/total*100:.1f}%)")
    print(f"🔥 High IV + Liquid: {high_ivr}")
    print(f"💾 Results saved: step4_liquidity.json")

def parse_args():
    parser = argparse.ArgumentParser(description="Enhanced Liquidity Scanner with Data Flow")
    parser.add_argument("--sample-sec", type=float, default=DEFAULT_SAMPLE_SEC, help="Collection time per ticker")
    parser.add_argument("--max-tickers", type=int, help="Limit number of tickers")
    parser.add_argument("--tickers", type=str, default="", help="Specific tickers (comma-separated)")
    parser.add_argument("--loose", action="store_true", help="Use loose gates")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(run_sequential(args))
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
```
**Run:** `python3 liquidity.py`
