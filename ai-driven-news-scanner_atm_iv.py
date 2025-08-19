**Create:** `touch atm_iv.py`

**Query:** `open -e atm_iv.py`

```bash
# atm_iv.py
import asyncio, json
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD

WIN_MIN, WIN_MAX = 30, 45

HIGH_VOL = {"TSLA","NVDA","AMD","ROKU","SNAP","GME","AMC"}
MED_VOL  = {"AAPL","MSFT","AMZN","META","GOOGL","NFLX"}

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def pick_exp(chain):
    today = datetime.now(timezone.utc).date()
    best, bestdiff = None, 1e9
    for d in chain.keys():
        dte = (d - today).days
        if WIN_MIN <= dte <= WIN_MAX:
            diff = abs(dte - (WIN_MIN + WIN_MAX) // 2)
            if diff < bestdiff:
                best, bestdiff = (d, dte), diff
    return best if best else (None, None)

def heuristic_ivr(t, iv):
    if not iv or iv <= 0:
        return 0.0, "none"
    if t in HIGH_VOL:
        lo, hi, m = 0.40, 1.20, "heur_high"
    elif t in MED_VOL:
        lo, hi, m = 0.20, 0.60, "heur_med"
    else:
        lo, hi, m = 0.15, 0.50, "heur_def"
    if iv <= lo:
        return 0.0, m
    if iv >= hi:
        return 100.0, m
    return 100 * (iv - lo) / (hi - lo), m

async def main():
    with open("universe_active.json") as f:
        U = [r for r in json.load(f) if r["status"] == "ok"]
    with open("step2_spot.json") as f:
        SP = json.load(f)

    sess = Session(USERNAME, PASSWORD)
    out = []

    async with DXLinkStreamer(sess) as s:
        for rec in U:
            t = rec["ticker"]
            spot = SP.get(t, {}).get("mid")
            if not spot:
                out.append({"ticker": t, "status": "no_spot"})
                continue
            try:
                chain = get_option_chain(sess, t)
            except Exception as e:
                out.append({"ticker": t, "status": f"chain_err:{e}"})
                continue
            if not chain:
                out.append({"ticker": t, "status": "no_chain"})
                continue
            exp, dte = pick_exp(chain)
            if not exp:
                out.append({"ticker": t, "status": "no_target_expiry"})
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
                "ticker": t,
                "status": "ok" if iv else "no_iv",
                "spot": spot,
                "target_expiry": exp.isoformat(),
                "dte": dte,
                "atm_iv": iv,
                "ivr": ivr,
                "ivr_method": method
            })

    with open("step3_atm_iv.json", "w") as f:
        json.dump(out, f, indent=2)
    ok = sum(1 for r in out if r["status"] == "ok")
    print(f"✅ ATM IVs: {ok} / {len(out)}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `python3 atm_iv.py`
