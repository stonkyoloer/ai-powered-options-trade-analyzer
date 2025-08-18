## Create Sectors

**Create:** `sectors.py`

**Query:** `open -e sectors.py`

```bash
# sectors.py
"""
Sector universes and symbol helpers.

Toggle which universe to use by setting PORTFOLIO_MODE to one of:
  - "gpt"     -> SECTORS_GPT (9 sectors × 4 = 36 tickers)
  - "grok"    -> SECTORS_GROK (9 sectors × 4 = 36 tickers)
  - "merged"  -> union of GPT+Grok tickers per sector (deduped, order-preserved)

Optional paste-overrides:
Create overrides/gpt.json or overrides/grok.json with:
{
  "Information Technology": ["...","...","...","..."],
  "...": ["..."]
}
"""

from pathlib import Path
import json

# -----------------------------
# GPT Portfolio
# -----------------------------
SECTORS_GPT = {
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["ADI", "INTU", "NVDA", "PANW"],
    },
    "Communication Services": {
        "etf": "XLC",
        "description": "ads, platforms, media",
        "tickers": ["DIS", "GOOGL", "META", "TMUS"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment",
        "tickers": ["HD", "LOW", "ROST", "TJX"],
    },
    "Consumer Staples": {
        "etf": "XLP",
        "description": "defensive cashflows, low vol",
        "tickers": ["EL", "MDLZ", "TGT", "WMT"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["ABBV", "CAH", "LLY", "MDT"],
    },
    "Financials": {
        "etf": "XLF",
        "description": "rate curve/credit sensitivity",
        "tickers": ["BAC", "GS", "JPM", "MS"],
    },
    "Industrials": {
        "etf": "XLI",
        "description": "capex, global trade, PMIs",
        "tickers": ["CAT", "DE", "LMT", "UNP"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge",
        "tickers": ["COP", "CVX", "SLB", "XOM"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity",
        "tickers": ["DUK", "NEE", "PCG", "SO"],
    },
}

# -----------------------------
# Grok Portfolio
# -----------------------------
SECTORS_GROK = {
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["AAPL", "AVGO", "MSFT", "NVDA"],
    },
    "Communication Services": {
        "etf": "XLC",
        "description": "ads, platforms, media",
        "tickers": ["GOOG", "GOOGL", "META", "NFLX"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment",
        "tickers": ["AMZN", "HD", "MCD", "TSLA"],
    },
    "Consumer Staples": {
        "etf": "XLP",
        "description": "defensive cashflows, low vol",
        "tickers": ["COST", "KO", "PG", "WMT"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["ABBV", "JNJ", "LLY", "UNH"],
    },
    "Financials": {
        "etf": "XLF",
        "description": "rate curve/credit sensitivity",
        "tickers": ["BRK.B", "JPM", "MA", "V"],
    },
    "Industrials": {
        "etf": "XLI",
        "description": "capex, global trade, PMIs",
        "tickers": ["CAT", "GE", "RTX", "UBER"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge",
        "tickers": ["COP", "CVX", "EOG", "XOM"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity",
        "tickers": ["CEG", "DUK", "NEE", "SO"],
    },
}

# -----------------------------
# Mode & helpers
# -----------------------------
PORTFOLIO_MODE = "gpt"  # "gpt", "grok", or "merged"

def _merge_sectors(a: dict, b: dict) -> dict:
    out = {}
    keys = set(a) | set(b)
    for k in keys:
        ea, eb = a.get(k, {}), b.get(k, {})
        etf = ea.get("etf") or eb.get("etf")
        desc = ea.get("description") or eb.get("description")
        tickers = []
        for src in (ea.get("tickers", []), eb.get("tickers", [])):
            for t in src:
                if t not in tickers:
                    tickers.append(t)
        out[k] = {"etf": etf, "description": desc, "tickers": tickers}
    return out

def _with_override(base: dict, mode: str) -> dict:
    path = Path("overrides") / f"{mode}.json"
    if not path.exists():
        return base
    data = json.loads(path.read_text())
    out = {}
    for sector, meta in base.items():
        out[sector] = {
            "etf": meta["etf"],
            "description": meta["description"],
            "tickers": data.get(sector, meta["tickers"])
        }
    return out

def get_sectors(mode: str = PORTFOLIO_MODE) -> dict:
    mode = (mode or "").lower()
    if mode == "gpt":
        return _with_override(SECTORS_GPT, "gpt")
    if mode == "grok":
        return _with_override(SECTORS_GROK, "grok")
    if mode == "merged":
        g = _with_override(SECTORS_GPT, "gpt")
        r = _with_override(SECTORS_GROK, "grok")
        return _merge_sectors(g, r)
    raise ValueError(f"Unknown PORTFOLIO_MODE '{mode}' (use 'gpt' | 'grok' | 'merged')")

SECTORS = get_sectors()

# -----------------------------
# Symbol aliases
# -----------------------------
SYMBOL_ALIASES = {
    "BRK.B": ["BRK.B", "BRK-B", "BRK/B"],
    "GOOGL": ["GOOGL", "GOOG"],
    "GOOG": ["GOOG", "GOOGL"],
}

def alias_candidates(sym: str) -> list[str]:
    """Return preferred symbol + any alias candidates to try for data providers."""
    return [sym] + SYMBOL_ALIASES.get(sym, [])
```


**Run:** `python3 sectors.py`
