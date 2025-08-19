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
