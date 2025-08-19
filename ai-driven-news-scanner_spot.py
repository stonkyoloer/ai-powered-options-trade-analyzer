**Create:** `touch spot.py`

**Query:** `open -e spot.py`

```bash
# spot.py
import asyncio, json
from datetime import datetime, timezone
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote
from config import USERNAME, PASSWORD

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

async def main():
    with open("universe_active.json") as f:
        names = sorted({r["ticker"] for r in json.load(f) if r["status"] == "ok"})
    sess = Session(USERNAME, PASSWORD)
    out = {}
    async with DXLinkStreamer(sess) as s:
        await s.subscribe(Quote, names)
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < 12 and len(out) < len(names):
            try:
                q = await asyncio.wait_for(s.get_event(Quote), timeout=1.5)
            except asyncio.TimeoutError:
                continue
            if not q or q.event_symbol not in names:
                continue
            bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
            if bid > 0 and ask > 0 and ask >= bid:
                out[q.event_symbol] = {"bid": bid, "ask": ask, "mid": (bid + ask) / 2, "ts": now()}
    with open("step2_spot.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"✅ spot quotes: {len(out)} / {len(names)}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `python3 spot.py`
