**Create:** `touch universe.py`

**Query:** `open -e universe.py`

```bash
# build_universe.py
import json
import collections
from pathlib import Path
from tastytrade import Session
from tastytrade.instruments import get_option_chain
from config import USERNAME, PASSWORD
from sectors import get_sectors, alias_candidates, PORTFOLIO_MODE

# Which universes to build in one go
BUILD_MODES = ["gpt", "grok", "merged"]  # edit to ["gpt","grok"] if you don't want merged

def has_chain(sess, sym):
    """Return the first alias that has an options chain, else None."""
    for c in alias_candidates(sym):
        try:
            oc = get_option_chain(sess, c)
            if oc:
                return c
        except Exception:
            pass
    return None

def build_for_mode(sess, mode):
    sectors = get_sectors(mode)
    cleaned = []
    seen = set()
    dedup_global = (mode == "merged")  # only dedup across sectors for the merged universe

    for sector, meta in sectors.items():
        for t in meta.get("tickers", []):
            if dedup_global and t in seen:
                continue
            seen.add(t)
            resolved = has_chain(sess, t)
            cleaned.append({
                "sector": sector,
                "ticker": resolved or t,
                "requested": t,
                "status": "ok" if resolved else "no_chain",
            })
    return cleaned

def main():
    Path(".").mkdir(exist_ok=True)
    sess = Session(USERNAME, PASSWORD)
    index = {}

    for mode in BUILD_MODES:
        cleaned = build_for_mode(sess, mode)
        out_path = f"universe_{mode}.json"
        with open(out_path, "w") as f:
            json.dump(cleaned, f, indent=2)

        ok = [x for x in cleaned if x["status"] == "ok"]
        by_sector = collections.Counter(x["sector"] for x in ok)
        print(f"[{mode}] ✅ chains ok: {len(ok)} / {len(cleaned)}")
        print(f"[{mode}] by sector:", dict(by_sector))
        print(f"[{mode}] wrote: {out_path}")

        index[mode] = {
            "total": len(cleaned),
            "ok": len(ok),
            "by_sector": dict(by_sector),
            "file": out_path,
        }

    with open("universe_index.json", "w") as f:
        json.dump(index, f, indent=2)
    print("Wrote: universe_index.json")

    # Link active universe to the selected PORTFOLIO_MODE
    active_mode = PORTFOLIO_MODE
    src = Path(f"universe_{active_mode}.json")
    dst = Path("universe_active.json")
    if src.exists():
        dst.write_text(src.read_text())
        print(f"🔗 active universe -> universe_active.json ({active_mode})")
    else:
        print(f"⚠️ active source {src} not found")

if __name__ == "__main__":
    main()
```

**Run:** `python3 universe.py`
